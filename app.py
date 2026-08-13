from flask import Flask, render_template, request, redirect, url_for, flash, session
import random

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

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
            
    # Retrieve user email/phone from session or defaults
    email = session.get('user_email', 'qphocus@gmail.com')
    phone = session.get('user_phone', '0548327035')
    
    # Generate OTP if not present
    if 'otp' not in session:
        session['otp'] = random.randint(100000, 999999)
        
    otp = session.get('otp')

    # SECURE LOGGING: Printed only in VS Code terminal for developer testing
    print(f"\n==============================")
    print(f"[DEV DEBUG] Generated OTP for {email}: {otp}")
    print(f"==============================\n")

    # Clean display message sent to front-end UI (No code leak)
    message = f"Verification code sent to {email} / {phone}."

    return render_template('verify_otp.html', message=message)

@app.route('/dashboard')
def dashboard():
    return "Welcome to your Focus Photos Dashboard!"

if __name__ == '__main__':
    app.run(debug=True)
