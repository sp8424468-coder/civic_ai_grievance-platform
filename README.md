Civic AI – Smart Civic Complaint Platform
Overview

Civic AI is a smart civic complaint management system designed to empower citizens to report issues efficiently and allow government departments to respond quickly. The platform uses AI for complaint categorization, prioritization, and worker allocation, making civic management faster and more data-driven.

Features
1. User Registration & Authentication

Users can register with their name, email, and password.
Email verification using OTP ensures authenticity.
Secure login system with session management.
Users can logout anytime.

2. Complaint Reporting

Users can submit complaints with:
Description
Geo-location (latitude & longitude)
Photo evidence
AI classifies the complaint into the correct department.
AI determines priority based on location clustering and urgency.
System automatically assigns available employees from the relevant department.

3. Complaint Tracking

Users can track their complaints in real-time by complaint ID.
View complaint details such as:
Description
Department handling it
Priority and status (Pending/Resolved)
Assigned employees

4. User Dashboard
View all submitted complaints.
Check complaint status updates.
Earn credit points when complaints are resolved.

5. Admin Dashboard

Admin login for system oversight.
View total complaints, pending vs resolved complaints.
Track active employees.
Verify complaints and update status to resolved.

6. Department Management

Admins can create departments.
Each department has its own admin credentials.
Department admin can:
Login to a dedicated dashboard.
Manage complaints assigned to the department.
Add or remove employees.
Assign employees to complaints.

7. Employee Management

Department employees can be added with:
Name, email, password, and working zone
Status (Available/Busy)
Employee assignment is automated based on priority and zone.

8. AI-Driven Features

Complaint Categorization: Uses NLP to classify complaints into departments.
Hotspot Detection: Clustering of complaints to detect problem areas.
Priority Assignment: High, Medium, Low priority based on department and cluster size.
Worker Prediction & Assignment: AI suggests number of employees needed and assigns them automatically.

9. Geo-Tag Verification

Uploaded complaint photos are checked for geotag data to ensure location authenticity.

10. Complaint Visualization

Admin dashboard provides heatmaps showing complaint density.
Visual representation of complaint clusters for easier decision-making.

11. Email Notifications

OTP sent via email for registration verification.
Optionally, future notifications can alert users when complaint status changes.



Tech Stack

Backend: Python, Flask
Database: SQLite (can be replaced with MySQL/PostgreSQL)
AI Modules: NLP & clustering (Python)
Frontend: HTML, CSS, JavaScript, Jinja2 Templates
Cloud Storage: Cloudinary (for complaint photos)
Mail: Flask-Mail (for OTP verification)
Other Libraries: PIL (image handling), Flask-CORS
