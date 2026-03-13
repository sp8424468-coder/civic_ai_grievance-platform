from flask import Flask, render_template, request, jsonify, redirect, session
from flask_mail import Mail, Message
from flask_cors import CORS
from PIL import Image
from PIL.ExifTags import TAGS
import random

app = Flask(__name__)
CORS(app)

app.secret_key = "supersecretkey"

# ---------------- ADMIN ACCOUNT ----------------
admin_user = {
    "username": "admin",
    "password": "admin123"
}

# ---------------- TEMP STORAGE ----------------
users = []
complaints = []
otp_store = {}

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

    otp_store[email] = {
        "otp": otp,
        "name": name,
        "password": password
    }

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

    stored = otp_store.get(email)

    if stored and stored["otp"] == user_otp:

        user = {
            "id": len(users) + 1,
            "name": stored["name"],
            "email": email,
            "password": stored["password"]
        }

        users.append(user)

        otp_store.pop(email)

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

    for user in users:
        if user["email"] == email and user["password"] == password:

            session["user_id"] = user["id"]

            return redirect("/report")

    return "Invalid email or password"


# ---------------- USER LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("admin", None)
    return redirect("/")


# ---------------- REPORT PAGE ----------------
@app.route("/report")
def report_page():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("report.html")


# ---------------- ADMIN LOGIN PAGE ----------------
@app.route("/admin")
def admin_login_page():
    return render_template("admin_login.html")


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == admin_user["username"] and password == admin_user["password"]:

        session["admin"] = True
        return redirect("/admin-dashboard")

    return "Invalid Admin Credentials"


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    return render_template("admin_dashboard.html", complaints=complaints)


# ---------------- TRACK PAGE ----------------
@app.route("/track")
def track_page():
    return render_template("track.html")


# ---------------- TRACK COMPLAINT ----------------
@app.route("/track-complaint/<int:complaint_id>")
def track_complaint(complaint_id):

    for complaint in complaints:
        if complaint["id"] == complaint_id:
            return jsonify(complaint)

    return jsonify({"error": "Complaint not found"}), 404


# ---------------- SUBMIT COMPLAINT ----------------
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():

    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    description = request.form.get("description")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    photo = request.files.get("photo")

    if not description:
        return jsonify({"error": "Description required"}), 400

    if not photo:
        return jsonify({"error": "Photo required"}), 400

    # ---------------- FIND USER EMAIL ----------------
    user_email = None

    for user in users:
        if user["id"] == session["user_id"]:
            user_email = user["email"]

    # ---------------- GEO TAG CHECK ----------------
    if not has_geotag(photo):

        msg = Message(
            "Complaint Not Registered - Civic AI",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )

        msg.body = """
Hello,

Your complaint was NOT registered because the uploaded photo does not contain GPS location metadata.

Please follow these steps:

1. Turn ON GPS on your phone
2. Enable 'Location Tags' in camera settings
3. Take a new photo
4. Upload again

Thank you,
Civic AI Platform
"""

        mail.send(msg)

        return jsonify({
            "error": "Photo must contain GPS geotag. Please capture image with location enabled."
        }), 400

    photo.seek(0)

    complaint = {
        "id": len(complaints) + 1,
        "user_id": session["user_id"],
        "description": description,
        "latitude": latitude,
        "longitude": longitude,
        "photo": photo.filename,
        "status": "Pending"
    }

    complaints.append(complaint)

    # ---------------- SUCCESS EMAIL ----------------
    msg = Message(
        "Complaint Registered Successfully - Civic AI",
        sender=app.config['MAIL_USERNAME'],
        recipients=[user_email]
    )

    msg.body = f"""
Hello,

Your civic complaint has been successfully registered.

Complaint ID: {complaint["id"]}

Issue Description:
{description}

Location:
Latitude: {latitude}
Longitude: {longitude}

You can track your complaint using this Complaint ID.

Thank you for helping improve the city.

Civic AI Platform
"""

    mail.send(msg)

    return jsonify({
        "message": "Complaint submitted successfully",
        "complaint_id": complaint["id"],
        "complaint": complaint
    })


# ---------------- GET ALL COMPLAINTS ----------------
@app.route("/complaints", methods=["GET"])
def get_complaints():
    return jsonify(complaints)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)