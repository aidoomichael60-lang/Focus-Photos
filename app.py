from flask import Flask, render_template, request, redirect, url_for, flash, session
import random

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# 1. FIX: Root URL redirects to OTP verification instead of showing a 404 error
@app.route('/')
def home():
    return redirect(url_for('verify_otp'))

# 2. OTP Verification Route
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
            
    email = session.get('user_email', 'qphocus@gmail.com')
    phone = session.get('user_phone', '0548327035')
    
    if 'otp' not in session:
        session['otp'] = random.randint(100000, 999999)
        
    otp = session.get('otp')

    print(f"\n==============================")
    print(f"[DEV DEBUG] OTP Code for {email}: {otp}")
    print(f"==============================\n")

    message = f"Verification code sent to {email} / {phone}."
    return render_template('verify_otp.html', message=message)

# 3. FIX: Dashboard Route now renders a complete dashboard UI
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 4. Camera Route: Opens the Samsung Web Camera interface
@app.route('/camera')
def camera():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True)
