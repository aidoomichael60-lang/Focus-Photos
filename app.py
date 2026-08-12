import os
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'focus_photos_secret_key_123')

# In-memory store for registered verified users
users_db = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if username in users_db:
            flash("Username already exists. Please pick another one.")
            return redirect(url_for('register'))

        # Generate 6-Digit OTP Code
        otp_code = str(random.randint(100000, 999999))

        # Save registration info in session until verified
        session['temp_user'] = {
            'username': username,
            'email': email,
            'phone': phone,
            'password': password,
            'otp': otp_code
        }

        # Print OTP to terminal console for easy testing
        print("\n" + "="*50)
        print(f"VERIFICATION OTP FOR {username} ({email}): {otp_code}")
        print("="*50 + "\n")

        flash(f"Verification code sent to {email} / {phone}. (Check terminal: {otp_code})")
        return redirect(url_for('verify_otp'))

    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session:
        flash("No registration in progress. Please register first.")
        return redirect(url_for('register'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        temp_user = session.get('temp_user')

        if temp_user and user_otp == temp_user['otp']:
            # Save user into verified database
            users_db[temp_user['username']] = {
                'username': temp_user['username'],
                'email': temp_user['email'],
                'phone': temp_user['phone'],
                'password': temp_user['password'],
                'is_verified': True
            }
            session.pop('temp_user', None)
            flash("Account successfully verified! You can now sign in.")
            return redirect(url_for('login'))
        else:
            flash("Invalid OTP code. Please try again.")
            return redirect(url_for('verify_otp'))

    return render_template('verify_otp.html')

@app.route('/resend_otp')
def resend_otp():
    temp_user = session.get('temp_user')
    if temp_user:
        new_otp = str(random.randint(100000, 999999))
        temp_user['otp'] = new_otp
        session['temp_user'] = temp_user
        
        print("\n" + "="*50)
        print(f"NEW RESENT OTP: {new_otp}")
        print("="*50 + "\n")
        
        flash(f"A new OTP code was generated! (Check terminal: {new_otp})")
    return redirect(url_for('verify_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_db.get(username)
        if user and user['password'] == password:
            session['user'] = username
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password, or account not verified.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please login to access the dashboard.")
        return redirect(url_for('login'))

    username = session['user']
    user_data = users_db.get(username, {'username': username})

    return render_template('dashboard.html', user=user_data, username=username)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)