# Student-attendance-system

A cloud-based Student Attendance Management System developed using Python Flask, MySQL, and AWS Cloud Services. The application enables teachers to mark attendance, generate reports, and analyze student attendance records through a simple web interface.

**Features**
Teacher attendance management
Student attendance tracking
Attendance report generation
Attendance percentage analysis
Cloud deployment on AWS
MySQL database integration
Responsive web interface

**Technologies Used**
**Frontend**
HTML
CSS
**Backend**
Python
Flask
**Database**
MySQL
Amazon RDS
**Cloud Services**
AWS EC2
AWS RDS
Security Groups
**Deployment**
Gunicorn

**System Architecture**
Teacher/User
    │
    ▼
Web Browser
    │
    ▼
AWS EC2 Instance
    │
    ▼
Gunicorn
    │
    ▼
Flask Application
    │
    ▼
Amazon RDS (MySQL)
    │
    ▼
Attendance Reports & Analysis

**AWS Deployment**
Launch EC2 Instance.
Configure Security Group:
Port 22 (SSH)
Port 5000 (Application)
Port 3306 (RDS)
Create Amazon RDS MySQL Database.
Upload project to EC2.
Install dependencies.
Run application using Gunicorn:
gunicorn -w 4 -b 0.0.0.0:5000 app:app
