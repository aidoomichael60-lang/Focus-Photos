import os
import random
import socket
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message

socket.setdefaulttimeout(5.0)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here')

# -------------------------------------------------------------
# GMAIL CONFIGURATION
# -------------------------------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'qphocus@gmail.com'
app.config['MAIL_PASSWORD'] = 'njlljroqlixueyci'
app.config['MAIL_DEFAULT_SENDER'] = ('Focus Photos', 'qphocus@gmail.com')

mail = Mail(app)

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
            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "error")
                return render_template('login.html')

            users_db[email] = password
            session['user_email'] = email
            return send_and_redirect_otp(email)

        elif action == 'signin':
            session['user_email'] = email
            return send_and_redirect_otp(email)

    return render_template('login.html')

def send_and_redirect_otp(email):
    otp = random.randint(100000, 999999)
    session['otp'] = otp

    # Send OTP via Email
    try:
        msg = Message(
            subject="Your Focus Photos Verification Code 🔑",
            recipients=[email]
        )
        msg.body = f"Hello,\n\nYour Focus Photos verification code is: {otp}\n\nPlease enter this code to complete your login."
        mail.send(msg)
        print(f"[SUCCESS] Email sent to {email}")
    except Exception as e:
        print(f"[EMAIL NOTICE] Could not send live email: {e}")

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
