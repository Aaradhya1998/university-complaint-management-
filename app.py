from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import random
import string


# ---------------- DATABASE ----------------
from database import (
    get_categories,
    get_category_counts,
    get_complaint_by_ticket,
    get_complaints,
    get_status_counts,
    init_app as init_database,
    insert_complaint,
    mark_complaint_resolved,
    get_complaint_by_id
)

# ---------------- ENV ----------------
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')

init_database(app)

# ---------------- SMTP OTP FUNCTION ----------------
import smtplib
from email.mime.text import MIMEText

def send_otp(email, otp):
    try:
        sender = os.environ.get("MAIL_USERNAME")
        password = os.environ.get("MAIL_PASSWORD")

        if not sender or not password:
            print("SMTP ERROR: Missing MAIL_USERNAME or MAIL_PASSWORD")
            return False

        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "Your OTP Code"
        msg["From"] = sender
        msg["To"] = email

        print("Connecting to SMTP...")

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)

        print("SMTP Login successful")

        server.send_message(msg)
        server.quit()

        print("SMTP: Email sent successfully")
        return True

    except Exception as e:
        print("SMTP ERROR:", e)
        return False


# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    try:
        print("LOGIN HIT")

        email = request.form.get('email')
        if not email:
            return "Email required", 400

        otp = ''.join(random.choices(string.digits, k=6))
        session['otp'] = otp
        session['email'] = email

        print("Generated OTP:", otp)

        import threading
        threading.Thread(target=send_otp, args=(email, otp)).start()

        return render_template('otp_verify.html')

    except Exception as e:
        print("LOGIN ERROR:", e)
        return f"Error: {e}", 500

    except Exception as e:
        print("LOGIN ERROR:", e)
        return f"Error: {e}", 500


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']

    if entered_otp == session.get('otp'):
        return redirect(url_for('user_dashboard'))
    else:
        flash('Invalid OTP. Please try again.')
        return redirect(url_for('home'))


@app.route('/dashboard')
def user_dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')


@app.route('/complaint_form')
def complaint_form():
    categories = [
        'Waste', 'Sanitation', 'Washroom', 'Library', 'Classrooms',
        'Electrical', 'Teaching Faculty', 'Course', 'Non-Teaching Faculty',
        'Security', 'Lost & Found'
    ]
    return render_template('complaint_form.html', categories=categories)


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


@app.route('/admin_dashboard')
def admin_dashboard():
   

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


# ---------------- RUN ----------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)