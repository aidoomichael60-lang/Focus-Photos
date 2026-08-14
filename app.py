import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "focus_photos_secret_key"  # Replace with a strong random key

# Folder where uploaded photos are saved
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if email:
            session['pending_email'] = email
            # Generate temporary 6-digit OTP code
            session['otp'] = str(random.randint(100000, 999999))
            flash(f"Your verification code is: {session['otp']}", "info")
            return redirect(url_for('verify_otp'))
        else:
            flash("Please enter a valid email.", "danger")
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
            flash("Invalid code. Please try again.", "danger")

    return render_template('verify_otp.html')

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', email=session['user_email'])

@app.route('/camera')
def camera():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('camera.html')

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'user_email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400

    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format'}), 400

    filename = secure_filename(file.filename)
    user_prefix = secure_filename(session['user_email'])
    saved_filename = f"{user_prefix}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
    file.save(filepath)

    file_size = os.path.getsize(filepath)

    return jsonify({
        'message': 'Photo uploaded successfully!',
        'filename': saved_filename,
        'url': url_for('get_uploaded_file', filename=saved_filename),
        'size': file_size
    })

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/get-user-photos', methods=['GET'])
def get_user_photos():
    if 'user_email' not in session:
        return jsonify({'photos': []}), 401

    user_prefix = secure_filename(session['user_email'])
    photos = []

    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for fname in os.listdir(app.config['UPLOAD_FOLDER']):
            if fname.startswith(user_prefix):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                photos.append({
                    'filename': fname,
                    'url': url_for('get_uploaded_file', filename=fname),
                    'size': os.path.getsize(filepath)
                })

    return jsonify({'photos': photos})

@app.route('/delete-photo', methods=['POST'])
def delete_photo():
    if 'user_email' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    filename = data.get('filename', '')
    user_prefix = secure_filename(session['user_email'])

    # Ensure security so users can only delete their own photos
    if filename and filename.startswith(user_prefix):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'message': 'Photo deleted successfully!'})

    return jsonify({'error': 'File not found or permission denied'}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
