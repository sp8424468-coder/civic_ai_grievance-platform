from flask import Flask, render_template, request, jsonify, redirect, session
from flask_mail import Mail, Message
from models import db, User, Department, Employee, Complaint 
from flask_cors import CORS
from PIL import Image
from PIL.ExifTags import TAGS
import random

app = Flask(__name__)
CORS(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

app.secret_key = "supersecretkey"

# ---------------- ADMIN ACCOUNT ----------------
admin_user = {
    "username": "admin",
    "password": "admin123"
}

# ---------------- TEMP STORAGE ----------------
users = []
complaints = []
otp_store = []
employees = []
departments = []

# ---------------- EMAIL CONFIG ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sp8424468@gmail.com'
app.config['MAIL_PASSWORD'] = 'aeokdjqtfvaygmtx'

mail = Mail(app)

# ---------------- GEO TAG CHECK ----------------
def has_geotag(image_file):

    try:
        image_file.seek(0)
        img = Image.open(image_file)
        exif_data = img._getexif()

        if not exif_data:
            return False

        gps_info = None

        for tag_id in exif_data:
            tag = TAGS.get(tag_id)
            if tag == "GPSInfo":
                gps_info = exif_data[tag_id]

        if not gps_info:
            return False

        gps_latitude = gps_info.get(2)
        gps_longitude = gps_info.get(4)

        if gps_latitude and gps_longitude:
            return True

        return False

    except Exception as e:
        print("Geotag error:", e)
        return False


# ---------------- AI COMPLAINT ANALYSIS ----------------
def analyze_complaint(description):

    text = description.lower()

    if "garbage" in text or "waste" in text:
        return "Sanitation", "Sanitation", "Medium"

    elif "pothole" in text or "road" in text:
        return "Infrastructure", "Infrastructure", "High"

    elif "water" in text or "leak" in text:
        return "Water", "Water", "Medium"

    elif "electric" in text or "power" in text:
        return "Electricity", "Electricity", "High"

    elif "fight" in text or "crime" in text:
        return "Police", "Police", "High"

    return "General", "General", "Low"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER PAGE ----------------
@app.route("/register")
def register_page():
    return render_template("register.html")


# ---------------- SEND OTP ----------------
@app.route("/register-user", methods=["POST"])
def register_user():

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    otp = str(random.randint(100000, 999999))

    otp_store.append({
        "email": email,
        "otp": otp,
        "name": name,
        "password": password
    })

    msg = Message(
        "OTP Verification - Civic AI",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.body = f"Your OTP is: {otp}"
    mail.send(msg)

    return render_template("verify_otp.html", email=email)

# ---------------- VERIFY OTP ----------------
@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    email = request.form.get("email")
    user_otp = request.form.get("otp")

    for record in otp_store:

        if record["email"] == email and record["otp"] == user_otp:

            # Save user to database
            user = User(
                name=record["name"],
                email=record["email"],
                password=record["password"],
                credit_points=0
            )

            db.session.add(user)
            db.session.commit()

            otp_store.remove(record)

            return redirect("/login")

    return "Invalid OTP"

# ---------------- LOGIN PAGE ----------------
@app.route("/login")
def login_page():
    return render_template("login.html")


# ---------------- LOGIN USER ----------------
@app.route("/login-user", methods=["POST"])
def login_user():

    email = request.form.get("email")
    password = request.form.get("password")

    # Find user in database
    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        session["user_id"] = user.id
        return redirect("/report")

    return "Invalid email or password"
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- REPORT PAGE ----------------
@app.route("/report")
def report_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("report.html")

@app.route("/dashboard")
def user_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    complaints = Complaint.query.filter_by(user_id=user.id).all()

    return render_template(
        "user_dashboard.html",
        user=user,
        complaints=complaints
    )


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin/")
def admin_login_page():
    return render_template("admin_login.html")


@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == admin_user["username"] and password == admin_user["password"]:

        session["admin"] = True
        return redirect("/admin-dashboard")

    return "Invalid Admin Credentials"


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    return render_template("profile.html", user=user)

@app.route("/verify-complaint/<int:id>")
def verify_complaint(id):

    complaint = Complaint.query.get(id)

    complaint.status = "Resolved"

    user = User.query.get(complaint.user_id)

    user.credit_points += 10

    db.session.commit()

    return redirect("/admin-dashboard")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    # Get complaints from database
    complaints = Complaint.query.all()

    total_complaints = len(complaints)

    pending = len([c for c in complaints if c.status == "Pending"])
    resolved = len([c for c in complaints if c.status == "Resolved"])

    active_workers = len(employees)

    return render_template(
        "admin_dashboard.html",
        complaints=complaints,
        total_complaints=total_complaints,
        pending=pending,
        resolved=resolved,
        active_workers=active_workers
    )

# ---------------- CREATE DEPARTMENT ----------------
@app.route("/departments")
def departments_page():

    if "admin" not in session:
        return redirect("/admin")

    return render_template("departments.html", departments=departments)


@app.route("/create-department", methods=["POST"])
def create_department():

    if "admin" not in session:
        return redirect("/admin")

    name = request.form.get("name")
    admin_email = request.form.get("admin_email")
    admin_password = request.form.get("admin_password")

    department = {
        "id": len(departments) + 1,
        "name": name,
        "admin_email": admin_email,
        "admin_password": admin_password
    }

    departments.append(department)

    return redirect("/departments")


# ---------------- DEPARTMENT ADMIN LOGIN ----------------
@app.route("/department-login")
def department_login_page():
    return render_template("department_login.html")


@app.route("/department-admin-login", methods=["POST"])
def department_admin_login():

    email = request.form.get("email")
    password = request.form.get("password")

    for dept in departments:

        if dept["admin_email"] == email and dept["admin_password"] == password:

            session["department_admin"] = dept["name"]
            return redirect("/department-dashboard")

    return "Invalid Department Admin Credentials"


# ---------------- DEPARTMENT DASHBOARD ----------------
@app.route("/department-dashboard")
def department_dashboard():

    if "department_admin" not in session:
        return redirect("/department-login")

    department_name = session["department_admin"]

    dept_employees = [
        e for e in employees if e["department"] == department_name
    ]

    department_complaints = [
        c for c in complaints if c["department"] == department_name
    ]

    return render_template(
        "department_dashboard.html",
        employees=dept_employees,
        complaints=department_complaints,
        department=department_name
    )


# ---------------- ADD EMPLOYEE ----------------
@app.route("/add-department-employee", methods=["POST"])
def add_department_employee():

    if "department_admin" not in session:
        return redirect("/department-login")

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    zone = request.form.get("zone")

    employee = {
        "id": len(employees) + 1,
        "name": name,
        "email": email,
        "password": password,
        "department": session["department_admin"],
        "zone": zone,
        "status": "Available"
    }

    employees.append(employee)

    return redirect("/department-dashboard")


# ---------------- DELETE EMPLOYEE ----------------
@app.route("/delete-employee/<int:emp_id>")
def delete_employee(emp_id):

    global employees
    employees = [e for e in employees if e["id"] != emp_id]

    return redirect("/department-dashboard")


# ---------------- TRACK COMPLAINT ----------------
@app.route("/track")
def track_page():
    return render_template("track.html")


@app.route("/track-complaint/<int:complaint_id>")
def track_complaint(complaint_id):

    for complaint in complaints:
        if complaint["id"] == complaint_id:
            return jsonify(complaint)

    return jsonify({"error": "Complaint not found"}), 404


# ---------------- SUBMIT COMPLAINT ----------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():

    # Check if user logged in
    if "user_id" not in session:
        return jsonify({"error": "Login required"}), 401

    description = request.form.get("description")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    photo = request.files.get("photo")

    # Validation
    if not description:
        return jsonify({"error": "Description required"}), 400

    if not photo:
        return jsonify({"error": "Photo required"}), 400

    # AI complaint analysis
    category, department, priority = analyze_complaint(description)

    # Create complaint object
    complaint = Complaint(
        user_id=session["user_id"],
        description=description,
        category=category,
        department=department,
        priority=priority,
        latitude=latitude,
        longitude=longitude,
        photo=photo.filename,
        status="Pending"
    )

    # Save complaint to database
    db.session.add(complaint)
    db.session.commit()

    return jsonify({
        "message": "Complaint submitted successfully",
        "complaint_id": complaint.id
    })
# ---------------- GET COMPLAINTS ----------------
@app.route("/complaints", methods=["GET"])
def get_complaints():
    return jsonify(complaints)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)