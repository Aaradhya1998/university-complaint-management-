from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import random
import string

# ---------------- DATABASE ----------------
from database import (
    get_categories,
    get_complaint_by_ticket,
    get_complaints,
    init_app as init_database,
    insert_complaint,
    mark_complaint_resolved,
    get_complaint_by_id
)

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fixed_secret_key_123')

init_database(app)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('login.html')

# ---------------- LOGIN (UI OTP) ----------------
@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.form.get('email')

        if not email:
            return "Email required", 400

        otp = ''.join(random.choices(string.digits, k=6))

        session['otp'] = otp
        session['email'] = email

        print("Generated OTP:", otp)

        # 🔥 Show OTP in UI (Demo Mode)
        flash(f"Your OTP is: {otp}")

        return render_template('otp_verify.html')

    except Exception as e:
        print("LOGIN ERROR:", e)
        return "Login error", 500

# ---------------- VERIFY OTP ----------------
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form.get('otp', '').strip()

    print("SESSION OTP:", session.get('otp'))
    print("ENTERED OTP:", entered_otp)

    if entered_otp == session.get('otp'):
        return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid OTP. Please try again.')
        return redirect(url_for('home'))

# ---------------- USER DASHBOARD ----------------
@app.route('/dashboard')
def user_dashboard():
    return render_template('dashboard.html')

# ---------------- COMPLAINT FORM ----------------
@app.route('/complaint_form')
def complaint_form():
    categories = [
        'Waste', 'Sanitation', 'Washroom', 'Library', 'Classrooms',
        'Electrical', 'Teaching Faculty', 'Course', 'Non-Teaching Faculty',
        'Security', 'Lost & Found'
    ]
    return render_template('complaint_form.html', categories=categories)

# ---------------- SUBMIT COMPLAINT ----------------
@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    email = session.get('email')

    prn_or_faculty_id = request.form['prn_or_faculty_id']
    category = request.form['category']
    description = request.form['description']

    image_path = None

    if 'image' in request.files:
        image = request.files['image']
        if image and image.filename:
            filename = secure_filename(image.filename)

            upload_dir = os.path.join(app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)

            image.save(os.path.join(upload_dir, filename))
            image_path = filename

    ticket_id = insert_complaint(
        email=email,
        prn_or_faculty_id=prn_or_faculty_id,
        category=category,
        description=description,
        image_path=image_path,
    )

    flash(f"Complaint submitted! Ticket ID: {ticket_id}")
    return redirect(url_for('complaint_form'))

# ---------------- TRACK COMPLAINT ----------------
@app.route('/track', methods=['GET', 'POST'])
def track_complaint():
    complaint = None

    if request.method == 'POST':
        ticket_id = request.form.get('complaint_id')

        if ticket_id:
            complaint = get_complaint_by_ticket(ticket_id.strip())

        if not complaint:
            flash("Complaint not found")

    return render_template('track.html', complaint=complaint)

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        selected_category = request.args.get('category', '').strip()
        selected_status = request.args.get('status', '').strip()

        complaints = get_complaints(
            category=selected_category or None,
            status=selected_status or None,
        )

        categories = get_categories()

        return render_template(
            'admin_dashboard.html',
            complaints=complaints,
            categories=categories,
            selected_category=selected_category,
            selected_status=selected_status,
        )

    except Exception as e:
        print("ADMIN ERROR:", e)
        return "Admin dashboard error", 500

# ---------------- DIRECT ADMIN ROUTE ----------------
@app.route('/admin')
def go_admin():
    return redirect(url_for('admin_dashboard'))

# ---------------- MARK RESOLVED ----------------
@app.route('/mark_resolved/<int:complaint_id>', methods=['POST'])
def mark_resolved(complaint_id):
    complaint = get_complaint_by_id(complaint_id)

    if complaint is None:
        flash('Complaint not found.')
    elif mark_complaint_resolved(complaint_id):
        flash('Complaint marked as resolved!')
    else:
        flash('Unable to update complaint status.')

    return redirect(url_for('admin_dashboard'))

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)