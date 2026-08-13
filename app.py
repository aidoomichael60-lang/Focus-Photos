from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Default home route redirects to the dashboard
@app.route('/')
def home():
    return redirect(url_for('dashboard'))

# Dashboard route (Albums, Photos, Profile)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Dedicated Camera route (Live camera feed, filters, timer, editor)
@app.route('/camera')
def camera():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True)
