import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_dev_key")

# Retrieve Resend API key from environment variable or fallback for local testing
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")

def send_and_redirect_otp(email):
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    session['otp'] = otp
    session['pending_email'] = email

    print(f"\n==========================================")
    print(f"🔑 VERIFICATION CODE FOR {email}: {otp}")
    print(f"==========================================\n")

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Always route the email to your primary inbox to bypass Resend sandbox restrictions
    payload = {
        "from": "Focus Photos <onboarding@resend.dev>",
        "to": ["aidoomichael60@gmail.com"],
        "subject": f"Verification Code for {email} 🔑",
        "html": f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #333; max-width: 500px; margin: auto; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #111;">Focus Photos Verification</h2>
            <p>A user is trying to log in/register with the email: <strong>{email}</strong></p>
            <p>The verification code is:</p>
            <div style="background-color: #f4f4f5; padding: 15px; text-align: center; border-radius: 8px;">
                <h1 style="color: #00f0ff; letter-spacing: 6px; margin: 0;">{otp}</h1>
            </div>
            <p style="margin-top: 15px; color: #666; font-size: 14px;">Enter or share this code to complete the verification step.</p>
        </div>
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        if response.status_code in [200, 201]:
            print(f"[SUCCESS] OTP email routed to aidoomichael60@gmail.com")
        else:
            print(f"[RESEND NOTICE] {response.status_code} Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Could not reach Resend API: {e}")

    return redirect(url_for('verify_otp'))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash("Please enter a valid email address.", "danger")
            return render_template('login.html')
        return send_and_redirect_otp(email)
    return render_template('login.html')


@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        actual_otp = str(session.get('otp', ''))

        if entered_otp and entered_otp == actual_otp:
            session['user_email'] = session.get('pending_email')
            session.pop('otp', None)
            flash("Successfully logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid or expired verification code. Please try again.", "danger")

    return render_template('verify_otp.html')


@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html', email=session['user_email'])


# --- CAMERA ROUTE ---
@app.route('/camera')
def camera():
    if 'user_email' not in session:
        flash("Please log in to access the camera.", "warning")
        return redirect(url_for('login'))
    return render_template('camera.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
