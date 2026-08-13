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
# Replace with your actual Gmail address
app.config['MAIL_USERNAME'] = 'qphocus@gmail.com'  
# Replace with your 16-character Google App Password (no spaces)
app.config['MAIL_PASSWORD'] = 'your_16_digit_app_password' 
app.config['MAIL_DEFAULT_SENDER'] = ('Focus Photos', 'qphocus@gmail.com')

mail = Mail(app)

# -------------------------------------------------------------
# 1. HOMEPAGE ROUTE
# -------------------------------------------------------------
@app.route('/')
def home():
    return redirect(url_for('verify_otp'))

# -------------------------------------------------------------
# 2. OTP VERIFICATION ROUTE
# -------------------------------------------------------------
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        session_otp = session.get('otp')
        
        if user_otp and str(user_otp) == str(session_otp):
            flash("Account verified successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid verification code. Please try again.", "error")
            
    recipient_email = session.get('user_email', 'qphocus@gmail.com')
    recipient_phone = session.get('user_phone', '0548327035')
    
    # Generate code and send email if code isn't generated yet
    if 'otp' not in session:
        session['otp'] = random.randint(100000, 999999)
        otp = session.get('otp')

        # Send Real Verification Email
        try:
            msg = Message(
                subject="Your Focus Photos Verification Code 🔑",
                recipients=[recipient_email]
            )
            msg.body = f"Hello,\n\nYour Focus Photos verification code is: {otp}\n\nIf you did not request this code, please ignore this email."
            mail.send(msg)
            print(f"\n[EMAIL SUCCESS] Sent OTP {otp} to {recipient_email}\n")
        except Exception as e:
            print(f"\n[EMAIL ERROR] Failed to send email: {e}\n")

    message = f"Verification code sent to {recipient_email} / {recipient_phone}."
    return render_template('verify_otp.html', message=message)

# -------------------------------------------------------------
# 3. DASHBOARD ROUTE
# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -------------------------------------------------------------
# 4. CAMERA ROUTE
# -------------------------------------------------------------
@app.route('/camera')
def camera():
    return render_template('camera.html')

# -------------------------------------------------------------
# 5. LOGOUT ROUTE
# -------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('verify_otp'))

if __name__ == '__main__':
    app.run(debug=True)
