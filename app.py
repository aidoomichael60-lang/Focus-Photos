from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# -------------------------------------------------------------
# GMAIL CONFIGURATION
# -------------------------------------------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'qphocus@gmail.com'
# To send actual emails, replace 'your_16_digit_app_password' below with a Google App Password
app.config['MAIL_PASSWORD'] = 'your_16_digit_app_password'
app.config['MAIL_DEFAULT_SENDER'] = ('Focus Photos', 'qphocus@gmail.com')

mail = Mail(app)

# -------------------------------------------------------------
# 1. LOGIN ROUTE (Email, Phone, or Both)
# -------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()

        if not email and not phone:
            flash("Please enter an email address or phone number.", "error")
            return redirect(url_for('login'))

        # Save details to session
        session['user_email'] = email
        session['user_phone'] = phone

        # Generate 6-digit OTP
        otp = random.randint(100000, 999999)
        session['otp'] = otp

        # Console print so you can always see the code during testing
        print(f"\n==========================================")
        print(f"🔑 VERIFICATION CODE FOR LOGIN: {otp}")
        print(f"📧 Email: {email if email else 'N/A'}")
        print(f"📱 Phone: {phone if phone else 'N/A'}")
        print(f"==========================================\n")

        # Try sending Email if user provided one
        if email:
            try:
                msg = Message(
                    subject="Your Focus Photos Code 🔑",
                    recipients=[email]
                )
                msg.body = f"Hello,\n\nYour Focus Photos verification code is: {otp}\n\nPlease enter this code to complete your login."
                mail.send(msg)
                print(f"[SUCCESS] Email sent to {email}")
            except Exception as e:
                print(f"[EMAIL NOTICE] Could not send live email: {e}")

        # SMS trigger notice
        if phone:
            print(f"[SMS NOTICE] Verification code {otp} targeted for phone: {phone}")

        return redirect(url_for('verify_otp'))

    return render_template('login.html')

# -------------------------------------------------------------
# 2. VERIFY CODE ROUTE (Locks app until correct code is entered)
# -------------------------------------------------------------
@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('user_email')
    phone = session.get('user_phone')

    if not email and not phone:
        return redirect(url_for('login'))

    destinations = []
    if email: destinations.append(email)
    if phone: destinations.append(phone)
    destination_str = " & ".join(destinations)

    if request.method == 'POST':
        user_otp = request.form.get('otp', '').strip()
        session_otp = str(session.get('otp', ''))

        if user_otp and user_otp == session_otp:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid verification code. Please try again.", "error")

    return render_template('verify_otp.html', destination=destination_str)

# -------------------------------------------------------------
# 3. DASHBOARD ROUTE (Protected)
# -------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# -------------------------------------------------------------
# 4. CAMERA ROUTE (Protected)
# -------------------------------------------------------------
@app.route('/camera')
def camera():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('camera.html')

# -------------------------------------------------------------
# 5. LOGOUT ROUTE
# -------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
