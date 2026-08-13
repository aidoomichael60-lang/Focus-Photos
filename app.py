from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# -------------------------------------------------------------
# GMAIL SMTP CONFIGURATION
# -------------------------------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'qphocus@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_16_digit_app_password'
app.config['MAIL_DEFAULT_SENDER'] = ('Focus Photos', 'qphocus@gmail.com')

mail = Mail(app)

# -------------------------------------------------------------
# 1. HOMEPAGE / VERIFICATION ROUTE
# -------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def verify_otp():
    # Generate OTP on first visit
    if 'otp' not in session:
        session['otp'] = random.randint(100000, 999999)
        otp = session['otp']
        recipient_email = session.get('user_email', 'qphocus@gmail.com')

        # Send Email safely (wrapped in try/except so it NEVER causes HTTP 500)
        try:
            msg = Message(
                subject="Your Focus Photos Verification Code 🔑",
                recipients=[recipient_email]
            )
            msg.body = f"Hello,\n\nYour Focus Photos verification code is: {otp}\n\nPlease enter this code to access your account."
            mail.send(msg)
            print(f"[SUCCESS] Verification email sent to {recipient_email}")
        except Exception as e:
            print(f"[EMAIL NOTICE] Could not send email via SMTP: {e}")

    # Handle OTP Submission
    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()
        session_otp = str(session.get('otp', ''))

        if user_otp and user_otp == session_otp:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid verification code. Please try again.", "error")

    recipient_email = session.get('user_email', 'qphocus@gmail.com')
    recipient_phone = session.get('user_phone', '0548327035')
    message = f"Verification code sent to {recipient_email} / {recipient_phone}."

    return render_template('verify_otp.html', message=message)

# -------------------------------------------------------------
# 2. PROTECTED DASHBOARD
# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('verify_otp'))
    return render_template('dashboard.html')

# -------------------------------------------------------------
# 3. PROTECTED CAMERA
# -------------------------------------------------------------
@app.route('/camera')
def camera():
    if not session.get('logged_in'):
        return redirect(url_for('verify_otp'))
    return render_template('camera.html')

# -------------------------------------------------------------
# 4. LOGOUT ROUTE
# -------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('verify_otp'))

if __name__ == '__main__':
    app.run(debug=True)
