# University Civil Complaint Management System

This project is a full-stack web application designed for managing civil complaints within a university setting. It allows students and faculty to submit complaints regarding various campus issues and provides an admin panel for tracking and resolving these complaints.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication via university email and OTP verification.
- Complaint submission form for students and faculty.
- Admin dashboard for managing and resolving complaints.
- Data visualization using Matplotlib for complaint statistics.
- Responsive design for a modern user experience.

## Technologies Used

- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (with structure for MySQL/PostgreSQL)
- **Graphs:** Matplotlib for generating visual data representations

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/university-complaint-system.git
   cd university-complaint-system
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` and fill in your SMTP email credentials.

5. **Run the application:**
   ```
   python app.py
   ```

6. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- **For Students/Faculty:**
  - Log in using your university email and receive an OTP for verification.
  - Fill out the complaint form to submit your issues.

- **For Admin:**
  - Access the admin dashboard to view, filter, and resolve complaints.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.