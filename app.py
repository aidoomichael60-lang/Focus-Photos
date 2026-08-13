import os
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

# Fetch Resend API Key from Environment
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')

# In-memory user database simulation
users_db = {}

# -------------------------------------------------------------
# 1. AUTHENTICATION ROUTE (Sign In / Sign Up)
# -------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if action == 'signup':
            fullname = request.form.get('fullname', '').strip()
            phone = request.form.get('phone', '').strip()
            username = request.form.get('username', '').strip()

            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "error")
                return render_template('login.html')

            users_db[email] = {
                'fullname': fullname,
                'phone': phone,
                'username': username,
                'password': password
            }
            session['user_email'] = email
            return send_and_redirect_otp(email)

        elif action == 'signin':
            session['user_email'] = email
            return send_and_redirect_otp(email)

    return render_template('login.html')

def send_and_redirect_otp(email):
    otp = random.randint(100000, 999999)
    session['otp'] = otp

    print(f"\n==========================================")
    print(f"🔑 VERIFICATION CODE FOR {email}: {otp}")
    print(f"==========================================\n")

    # Send email via Resend HTTPS API (Bypasses Render SMTP restrictions)
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": "Focus Photos <onboarding@resend.dev>",
        "to": [email],
        "subject": "Your Focus Photos Verification Code 🔑",
        "html": f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2>Focus Photos Verification</h2>
            <p>Your verification code is:</p>
            <h1 style="color: #00f0ff; letter-spacing: 4px;">{otp}</h1>
            <p>Enter this code in your browser to log in.</p>
        </div>
        """
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8)
        if response.status_code == 200 or response.status_code == 201:
            print(f"[SUCCESS] Verification email sent to {email}")
        else:
            print(f"[RESEND NOTICE] {response.status_code} Response: {response.text}")
    except Exception as e:
        print(f"[ERROR] Could not reach Resend API: {e}")

    return redirect(url_for('verify_otp'))

# -------------------------------------------------------------
# 2. VERIFICATION ROUTE
# -------------------------------------------------------------
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('user_email', 'qphocus@gmail.com')

    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()
        session_otp = str(session.get('otp', ''))

        if user_otp and user_otp == session_otp:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid verification code. Please try again.", "error")

    message = f"Verification code sent to {email}."
    return render_template('verify_otp.html', message=message)

# -------------------------------------------------------------
# 3. PROTECTED ROUTES
# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/camera')
def camera():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('camera.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
