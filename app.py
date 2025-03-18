from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import folium
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Appointment model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    consultation_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(20), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample user class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Sample user database
users = {'user1': {'password': 'password1'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Sample data for doctors
doctors = [
    {
        "id": 1,
        "name": "Dr. Kavita Rao",
        "specialty": "Gynecologist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 43210",
        "hospital": "Apollo Hospitals",
        "experience": "15 years",
        "qualifications": "MBBS, MD (Obstetrics & Gynecology)",
        "about": "Dr. Kavita Rao is a highly experienced gynecologist with over 15 years of practice.",
        "services": ["Pregnancy Care", "Infertility Treatment", "Laparoscopic Surgery"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "https://storage.googleapis.com/a1aa/image/YM3YR24d0oYhOxbHzseNujkpd6L7KxDWgWDcweIPhyewqVQoA.jpg",
    },
    {
        "id": 2,
        "name": "Dr. Arjun Menon",
        "specialty": "Cardiologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 32109",
        "hospital": "Fortis Malar Hospital",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Cardiology)",
        "about": "Dr. Arjun Menon is a renowned cardiologist with expertise in interventional cardiology.",
        "services": ["Angioplasty", "Pacemaker Implantation", "Heart Failure Management"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "https://storage.googleapis.com/a1aa/image/WTYikW81pV6wPF5Qgde2bMBv40X2Payh4kbgefzt3gcrqVQoA.jpg"
    },
{
        "id": 3,
        "name": "Dr. Meera Iyer",
        "specialty": "Dermatologist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 21098",
        "hospital": "MIOT International",
        "experience": "10 years",
        "qualifications": "MBBS, MD (Dermatology)",
        "about": "Dr. Meera Iyer is a leading dermatologist specializing in cosmetic dermatology, skin cancer treatment, and acne management. She is known for her innovative treatments and personalized care.",
        "services": ["Laser Treatments", "Acne Management", "Skin Cancer Treatment", "Anti-Aging Therapies"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "https://storage.googleapis.com/a1aa/image/IouKVtMS1n7KOR9IU85h6wYsgTj9S1lf42yVmRHz9nzraFEKA.jpg"
        },
        {
        "id": 4,
        "name": "Dr. Rakesh Singh",
        "specialty": "Orthopedic Surgeon",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 10987",
        "hospital": "Global Hospitals",
        "experience": "18 years",
        "qualifications": "MBBS, MS (Orthopedics)",
        "about": "Dr. Rakesh Singh is a highly skilled orthopedic surgeon with expertise in joint replacement surgeries, sports injuries, and spine surgeries. He has successfully performed over 3,000 joint replacement surgeries.",
        "services": ["Knee Replacement", "Hip Replacement", "Arthroscopy", "Spine Surgery"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "https://storage.googleapis.com/a1aa/image/4EVTMv9EVvpYNd7NUjTwAdr0uxsE2lYZJIXCneVGo1DqaFEKA.jpg"
        },
        {
        "id": 5,
        "name": "Dr. Suman Gupta",
        "specialty": "Neurologist",
        "location": "Velachery, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 09876",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "14 years",
        "qualifications": "MBBS, DM (Neurology)",
        "about": "Dr. Suman Gupta is a leading neurologist specializing in stroke management, epilepsy, and movement disorders. She is known for her research in neurodegenerative diseases and patient-focused care.",
        "services": ["Stroke Management", "Epilepsy Treatment", "Parkinson's Disease Management", "Migraine Treatment"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "https://storage.googleapis.com/a1aa/image/RCvPCkkBAAZaPJy1gBeCShWxPts9oUfnDNQXil8RtRBT1KIUA.jpg"
        },
        {
        "id": 6,
        "name": "Dr. Anil Mehta",
        "specialty": "Pediatrician",
        "location": "Kodambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 98765",
        "hospital": "Kanchi Kamakoti Childs Trust Hospital",
        "experience": "16 years",
        "qualifications": "MBBS, DCH (Pediatrics)",
        "about": "Dr. Anil Mehta is a dedicated pediatrician with expertise in neonatal care, childhood vaccinations, and developmental disorders. He is known for his gentle approach and effective communication with children.",
        "services": ["Neonatal Care", "Vaccinations", "Developmental Disorders", "Nutrition Counseling"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "https://storage.googleapis.com/a1aa/image/Sszi2eFoeZkakEOwnv6ftQfV0CJ889hP589N9hEPqySIVrgQB.jpg"
        },
        {
        "id": 7,
        "name": "Dr. Priya Sharma",
        "specialty": "Oncologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 32109 87654",
        "hospital": "Adyar Cancer Institute",
        "experience": "13 years",
        "qualifications": "MBBS, MD (Oncology)",
        "about": "Dr. Priya Sharma is a renowned oncologist specializing in breast cancer, lung cancer, and hematologic malignancies. She is known for her empathetic care and cutting-edge treatment approaches.",
        "services": ["Chemotherapy", "Radiation Therapy", "Immunotherapy", "Palliative Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/7.jpg"
        },
        {
        "id": 8,
        "name": "Dr. Rajesh Kumar",
        "specialty": "ENT Specialist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 21098 76543",
        "hospital": "SIMS Hospital",
        "experience": "11 years",
        "qualifications": "MBBS, MS (ENT)",
        "about": "Dr. Rajesh Kumar is an experienced ENT specialist with expertise in sinus surgeries, hearing loss treatments, and voice disorders. He is known for his meticulous approach and patient satisfaction.",
        "services": ["Sinus Surgery", "Hearing Aid Fitting", "Voice Disorder Treatment", "Tonsillectomy"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "/static/images/8.jpg"
        },
        {
        "id": 9,
        "name": "Dr. Sunita Reddy",
        "specialty": "Psychiatrist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 10987 65432",
        "hospital": "VHS Mental Health Center",
        "experience": "17 years",
        "qualifications": "MBBS, MD (Psychiatry)",
        "about": "Dr. Sunita Reddy is a leading psychiatrist specializing in anxiety disorders, depression, and addiction treatment. She is known for her holistic approach and effective therapy techniques.",
        "services": ["Cognitive Behavioral Therapy", "Depression Treatment", "Addiction Counseling", "Stress Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/9.jpg"
        },
        {
        "id": 10,
        "name": "Dr. Vikram Patel",
        "specialty": "Urologist",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 09876 54321",
        "hospital": "Kauvery Hospital",
        "experience": "14 years",
        "qualifications": "MBBS, MS (Urology)",
        "about": "Dr. Vikram Patel is a skilled urologist with expertise in kidney stone treatment, prostate surgeries, and urinary incontinence. He is known for his minimally invasive techniques and patient care.",
        "services": ["Kidney Stone Treatment", "Prostate Surgery", "Urinary Incontinence Treatment", "Vasectomy"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/10.jpg"
        },
        {
        "id": 11,
        "name": "Dr. Ananya Das",
        "specialty": "Endocrinologist",
        "location": "Alwarpet, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12345",
        "hospital": "Billroth Hospitals",
        "experience": "12 years",
        "qualifications": "MBBS, DM (Endocrinology)",
        "about": "Dr. Ananya Das is a renowned endocrinologist specializing in diabetes management, thyroid disorders, and hormonal imbalances. She is known for her patient-centered approach and innovative treatments.",
        "services": ["Diabetes Management", "Thyroid Treatment", "Hormone Replacement Therapy", "Obesity Management"],
        "languages": ["English", "Tamil", "Bengali"],
        "image": "/static/images/11.jpg"
        },
        {
        "id": 12,
        "name": "Dr. Sanjay Verma",
        "specialty": "Gastroenterologist",
        "location": "Perungudi, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12345",
        "hospital": "Gleneagles Global Hospitals",
        "experience": "15 years",
        "qualifications": "MBBS, DM (Gastroenterology)",
        "about": "Dr. Sanjay Verma is a leading gastroenterologist with expertise in liver diseases, endoscopic procedures, and inflammatory bowel disease. He is known for his precision and compassionate care.",
        "services": ["Endoscopy", "Liver Disease Treatment", "IBD Management", "Colonoscopy"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/12.jpg"
        },
        {
        "id": 13,
        "name": "Dr. Nandini Kapoor",
        "specialty": "Rheumatologist",
        "location": "Egmore, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 12345",
        "hospital": "Apollo Speciality Hospitals",
        "experience": "10 years",
        "qualifications": "MBBS, DM (Rheumatology)",
        "about": "Dr. Nandini Kapoor is a dedicated rheumatologist specializing in arthritis, lupus, and autoimmune diseases. She is known for her holistic approach and patient education.",
        "services": ["Arthritis Treatment", "Lupus Management", "Autoimmune Disease Treatment", "Osteoporosis Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/13.jpg"
        },
        {
        "id": 14,
        "name": "Dr. Karthik Rajan",
        "specialty": "Pulmonologist",
        "location": "Guindy, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 12345",
        "hospital": "MIOT International",
        "experience": "13 years",
        "qualifications": "MBBS, MD (Pulmonology)",
        "about": "Dr. Karthik Rajan is a skilled pulmonologist specializing in asthma, COPD, and sleep disorders. He is known for his expertise in critical care and patient-focused treatments.",
        "services": ["Asthma Management", "COPD Treatment", "Sleep Disorder Treatment", "Critical Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/14.jpg"
        },
        {
        "id": 15,
        "name": "Dr. Shalini Menon",
        "specialty": "Nephrologist",
        "location": "Porur, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 12345",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "16 years",
        "qualifications": "MBBS, DM (Nephrology)",
        "about": "Dr. Shalini Menon is a leading nephrologist specializing in kidney transplants, dialysis, and chronic kidney disease. She is known for her compassionate care and innovative treatments.",
        "services": ["Kidney Transplant", "Dialysis", "Chronic Kidney Disease Management", "Hypertension Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/15.jpg"
        },
        {
        "id": 16,
        "name": "Dr. Ravi Shankar",
        "specialty": "Ophthalmologist",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 12345",
        "hospital": "Sankara Nethralaya",
        "experience": "18 years",
        "qualifications": "MBBS, MS (Ophthalmology)",
        "about": "Dr. Ravi Shankar is a renowned ophthalmologist specializing in cataract surgery, LASIK, and glaucoma treatment. He is known for his precision and patient satisfaction.",
        "services": ["Cataract Surgery", "LASIK", "Glaucoma Treatment", "Retinal Disorders"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/16.jpg"
        },
        {
        "id": 17,
        "name": "Dr. Anjali Desai",
        "specialty": "Gynecologist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12346",
        "hospital": "Apollo Hospitals",
        "experience": "14 years",
        "qualifications": "MBBS, MD (Obstetrics & Gynecology)",
        "about": "Dr. Anjali Desai specializes in high-risk pregnancies and laparoscopic surgeries. She is known for her patient-centric approach.",
        "services": ["Pregnancy Care", "Infertility Treatment", "Laparoscopic Surgery", "Menopause Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/17.jpg"
        },
        {
        "id": 18,
        "name": "Dr. Rahul Sharma",
        "specialty": "Cardiologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12346",
        "hospital": "Fortis Malar Hospital",
        "experience": "13 years",
        "qualifications": "MBBS, MD (Cardiology)",
        "about": "Dr. Rahul Sharma is an expert in interventional cardiology and heart failure management. He is known for his innovative techniques.",
        "services": ["Angioplasty", "Pacemaker Implantation", "Heart Failure Management", "Preventive Cardiology"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/18.jpg"
        },
        {
        "id": 19,
        "name": "Dr. Priya Menon",
        "specialty": "Dermatologist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 12346",
        "hospital": "MIOT International",
        "experience": "11 years",
        "qualifications": "MBBS, MD (Dermatology)",
        "about": "Dr. Priya Menon specializes in cosmetic dermatology and skin cancer treatment. She is known for her personalized care.",
        "services": ["Laser Treatments", "Acne Management", "Skin Cancer Treatment", "Anti-Aging Therapies"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "/static/images/19.jpg"
        },
        {
        "id": 20,
        "name": "Dr. Vikas Singh",
        "specialty": "Orthopedic Surgeon",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 12346",
        "hospital": "Global Hospitals",
        "experience": "17 years",
        "qualifications": "MBBS, MS (Orthopedics)",
        "about": "Dr. Vikas Singh is an expert in joint replacement surgeries and sports injuries. He is known for his precision.",
        "services": ["Knee Replacement", "Hip Replacement", "Arthroscopy", "Spine Surgery"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/20.jpg"
        },
        {
        "id": 21,
        "name": "Dr. Ananya Reddy",
        "specialty": "Neurologist",
        "location": "Velachery, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 12346",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "15 years",
        "qualifications": "MBBS, DM (Neurology)",
        "about": "Dr. Ananya Reddy specializes in stroke management and epilepsy treatment. She is known for her research in neurodegenerative diseases.",
        "services": ["Stroke Management", "Epilepsy Treatment", "Parkinson's Disease Management", "Migraine Treatment"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/21.jpg"
        },
        {
        "id": 22,
        "name": "Dr. Arjun Kapoor",
        "specialty": "Pediatrician",
        "location": "Kodambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 12346",
        "hospital": "Kanchi Kamakoti Childs Trust Hospital",
        "experience": "14 years",
        "qualifications": "MBBS, DCH (Pediatrics)",
        "about": "Dr. Arjun Kapoor specializes in neonatal care and childhood vaccinations. He is known for his gentle approach.",
        "services": ["Neonatal Care", "Vaccinations", "Developmental Disorders", "Nutrition Counseling"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/22.jpg"
        },
        {
        "id": 23,
        "name": "Dr. Shalini Gupta",
        "specialty": "Oncologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 32109 12346",
        "hospital": "Adyar Cancer Institute",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Oncology)",
        "about": "Dr. Shalini Gupta specializes in breast cancer and lung cancer. She is known for her empathetic care.",
        "services": ["Chemotherapy", "Radiation Therapy", "Immunotherapy", "Palliative Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/23.jpg"
        },
        {
        "id": 24,
        "name": "Dr. Rajesh Iyer",
        "specialty": "ENT Specialist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 21098 12346",
        "hospital": "SIMS Hospital",
        "experience": "10 years",
        "qualifications": "MBBS, MS (ENT)",
        "about": "Dr. Rajesh Iyer specializes in sinus surgeries and hearing loss treatments. He is known for his meticulous approach.",
        "services": ["Sinus Surgery", "Hearing Aid Fitting", "Voice Disorder Treatment", "Tonsillectomy"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "/static/images/24.jpg"
        },
        {
        "id": 25,
        "name": "Dr. Sunita Menon",
        "specialty": "Psychiatrist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 10987 12346",
        "hospital": "VHS Mental Health Center",
        "experience": "16 years",
        "qualifications": "MBBS, MD (Psychiatry)",
        "about": "Dr. Sunita Menon specializes in anxiety disorders and depression. She is known for her holistic approach.",
        "services": ["Cognitive Behavioral Therapy", "Depression Treatment", "Addiction Counseling", "Stress Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/25.jpg"
        },
        {
        "id": 26,
        "name": "Dr. Vikram Desai",
        "specialty": "Urologist",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 09876 12346",
        "hospital": "Kauvery Hospital",
        "experience": "13 years",
        "qualifications": "MBBS, MS (Urology)",
        "about": "Dr. Vikram Desai specializes in kidney stone treatment and prostate surgeries. He is known for his minimally invasive techniques.",
        "services": ["Kidney Stone Treatment", "Prostate Surgery", "Urinary Incontinence Treatment", "Vasectomy"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/26.jpg"
        },
        {
        "id": 27,
        "name": "Dr. Ananya Kapoor",
        "specialty": "Endocrinologist",
        "location": "Alwarpet, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12347",
        "hospital": "Billroth Hospitals",
        "experience": "11 years",
        "qualifications": "MBBS, DM (Endocrinology)",
        "about": "Dr. Ananya Kapoor specializes in diabetes management and thyroid disorders. She is known for her patient-centered approach.",
        "services": ["Diabetes Management", "Thyroid Treatment", "Hormone Replacement Therapy", "Obesity Management"],
        "languages": ["English", "Tamil", "Bengali"],
        "image": "/static/images/27.jpg"
        },
        {
        "id": 28,
        "name": "Dr. Sanjay Reddy",
        "specialty": "Gastroenterologist",
        "location": "Perungudi, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12347",
        "hospital": "Gleneagles Global Hospitals",
        "experience": "14 years",
        "qualifications": "MBBS, DM (Gastroenterology)",
        "about": "Dr. Sanjay Reddy specializes in liver diseases and endoscopic procedures. He is known for his precision.",
        "services": ["Endoscopy", "Liver Disease Treatment", "IBD Management", "Colonoscopy"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/28.jpg"
        },
        {
        "id": 29,
        "name": "Dr. Nandini Sharma",
        "specialty": "Rheumatologist",
        "location": "Egmore, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 12347",
        "hospital": "Apollo Speciality Hospitals",
        "experience": "12 years",
        "qualifications": "MBBS, DM (Rheumatology)",
        "about": "Dr. Nandini Sharma specializes in arthritis and lupus. She is known for her holistic approach.",
        "services": ["Arthritis Treatment", "Lupus Management", "Autoimmune Disease Treatment", "Osteoporosis Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/29.jpg"
        },
        {
        "id": 30,
        "name": "Dr. Karthik Menon",
        "specialty": "Pulmonologist",
        "location": "Guindy, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 12347",
        "hospital": "MIOT International",
        "experience": "13 years",
        "qualifications": "MBBS, MD (Pulmonology)",
        "about": "Dr. Karthik Menon specializes in asthma and COPD. He is known for his expertise in critical care.",
        "services": ["Asthma Management", "COPD Treatment", "Sleep Disorder Treatment", "Critical Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/30.jpg"
        },
        {
        "id": 31,
        "name": "Dr. Shalini Reddy",
        "specialty": "Nephrologist",
        "location": "Porur, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 12347",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "15 years",
        "qualifications": "MBBS, DM (Nephrology)",
        "about": "Dr. Shalini Reddy specializes in kidney transplants and dialysis. She is known for her compassionate care.",
        "services": ["Kidney Transplant", "Dialysis", "Chronic Kidney Disease Management", "Hypertension Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/31.jpg"
        },
        {
        "id": 32,
        "name": "Dr. Ravi Kapoor",
        "specialty": "Ophthalmologist",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 12347",
        "hospital": "Sankara Nethralaya",
        "experience": "17 years",
        "qualifications": "MBBS, MS (Ophthalmology)",
        "about": "Dr. Ravi Kapoor specializes in cataract surgery and LASIK. He is known for his precision.",
        "services": ["Cataract Surgery", "LASIK", "Glaucoma Treatment", "Retinal Disorders"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/32.jpg"
        },
        {
        "id": 33,
        "name": "Dr. Anjali Sharma",
        "specialty": "Gynecologist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12348",
        "hospital": "Apollo Hospitals",
        "experience": "13 years",
        "qualifications": "MBBS, MD (Obstetrics & Gynecology)",
        "about": "Dr. Anjali Sharma specializes in high-risk pregnancies and infertility treatments. She is known for her compassionate care.",
        "services": ["Pregnancy Care", "Infertility Treatment", "Laparoscopic Surgery", "Menopause Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/33.jpg"
        },
        {
        "id": 34,
        "name": "Dr. Rahul Menon",
        "specialty": "Cardiologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12348",
        "hospital": "Fortis Malar Hospital",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Cardiology)",
        "about": "Dr. Rahul Menon specializes in interventional cardiology and heart failure management. He is known for his innovative techniques.",
        "services": ["Angioplasty", "Pacemaker Implantation", "Heart Failure Management", "Preventive Cardiology"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/34.jpg"
        },
        {
        "id": 35,
        "name": "Dr. Priya Reddy",
        "specialty": "Dermatologist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 12348",
        "hospital": "MIOT International",
        "experience": "11 years",
        "qualifications": "MBBS, MD (Dermatology)",
        "about": "Dr. Priya Reddy specializes in cosmetic dermatology and skin cancer treatment. She is known for her personalized care.",
        "services": ["Laser Treatments", "Acne Management", "Skin Cancer Treatment", "Anti-Aging Therapies"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "/static/images/35.jpg"
        },
        {
        "id": 36,
        "name": "Dr. Vikas Kapoor",
        "specialty": "Orthopedic Surgeon",
        "location": "Nungambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 12348",
        "hospital": "Global Hospitals",
        "experience": "16 years",
        "qualifications": "MBBS, MS (Orthopedics)",
        "about": "Dr. Vikas Kapoor specializes in joint replacement surgeries and sports injuries. He is known for his precision.",
        "services": ["Knee Replacement", "Hip Replacement", "Arthroscopy", "Spine Surgery"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/36.jpg"
        },
        {
        "id": 37,
        "name": "Dr. Ananya Menon",
        "specialty": "Neurologist",
        "location": "Velachery, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 12348",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "14 years",
        "qualifications": "MBBS, DM (Neurology)",
        "about": "Dr. Ananya Menon specializes in stroke management and epilepsy treatment. She is known for her research in neurodegenerative diseases.",
        "services": ["Stroke Management", "Epilepsy Treatment", "Parkinson's Disease Management", "Migraine Treatment"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/37.jpg"
        },
        {
        "id": 38,
        "name": "Dr. Arjun Reddy",
        "specialty": "Pediatrician",
        "location": "Kodambakkam, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 12348",
        "hospital": "Kanchi Kamakoti Childs Trust Hospital",
        "experience": "13 years",
        "qualifications": "MBBS, DCH (Pediatrics)",
        "about": "Dr. Arjun Reddy specializes in neonatal care and childhood vaccinations. He is known for his gentle approach.",
        "services": ["Neonatal Care", "Vaccinations", "Developmental Disorders", "Nutrition Counseling"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/38.jpg"
        },
        {
        "id": 39,
        "name": "Dr. Shalini Kapoor",
        "specialty": "Oncologist",
        "location": "Adyar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 32109 12348",
        "hospital": "Adyar Cancer Institute",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Oncology)",
        "about": "Dr. Shalini Kapoor specializes in breast cancer and lung cancer. She is known for her empathetic care.",
        "services": ["Chemotherapy", "Radiation Therapy", "Immunotherapy", "Palliative Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/39.jpg"
        },
        {
        "id": 40,
        "name": "Dr. Rajesh Reddy",
        "specialty": "ENT Specialist",
        "location": "Anna Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 21098 12348",
        "hospital": "SIMS Hospital",
        "experience": "11 years",
        "qualifications": "MBBS, MS (ENT)",
        "about": "Dr. Rajesh Reddy specializes in sinus surgeries and hearing loss treatments. He is known for his meticulous approach.",
        "services": ["Sinus Surgery", "Hearing Aid Fitting", "Voice Disorder Treatment", "Tonsillectomy"],
        "languages": ["English", "Tamil", "Telugu"],
        "image": "/static/images/40.jpg"
        },
        {
        "id": 41,
        "name": "Dr. Sunita Kapoor",
        "specialty": "Psychiatrist",
        "location": "T. Nagar, Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 10987 12348",
        "hospital": "VHS Mental Health Center",
        "experience": "15 years",
        "qualifications": "MBBS, MD (Psychiatry)",
        "about": "Dr. Sunita Kapoor specializes in anxiety disorders and depression. She is known for her holistic approach.",
        "services": ["Cognitive Behavioral Therapy", "Depression Treatment", "Addiction Counseling", "Stress Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/41.jpg"
        },
        {
        "id": 42,
        "name": "Dr. Vikram Reddy",
        "specialty": "Urologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 09876 12348",
        "hospital": "Kauvery Hospital",
        "experience": "14 years",
        "qualifications": "MBBS, MS (Urology)",
        "about": "Dr. Vikram Reddy specializes in kidney stone treatment and prostate surgeries. He is known for his minimally invasive techniques.",
        "services": ["Kidney Stone Treatment", "Prostate Surgery", "Urinary Incontinence Treatment", "Vasectomy"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/42.jpg"
        },
        {
        "id": 43,
        "name": "Dr. Ananya Reddy",
        "specialty": "Endocrinologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12349",
        "hospital": "Billroth Hospitals",
        "experience": "12 years",
        "qualifications": "MBBS, DM (Endocrinology)",
        "about": "Dr. Ananya Reddy specializes in diabetes management and thyroid disorders. She is known for her patient-centered approach.",
        "services": ["Diabetes Management", "Thyroid Treatment", "Hormone Replacement Therapy", "Obesity Management"],
        "languages": ["English", "Tamil", "Bengali"],
        "image": "/static/images/43.jpg"
        },
        {
        "id": 44,
        "name": "Dr. Sanjay Kapoor",
        "specialty": "Gastroenterologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12349",
        "hospital": "Gleneagles Global Hospitals",
        "experience": "13 years",
        "qualifications": "MBBS, DM (Gastroenterology)",
        "about": "Dr. Sanjay Kapoor specializes in liver diseases and endoscopic procedures. He is known for his precision.",
        "services": ["Endoscopy", "Liver Disease Treatment", "IBD Management", "Colonoscopy"],
        "languages": ["English", "Hindi", "Tamil"],
        "image": "/static/images/44.jpg"
        },
        {
        "id": 45,
        "name": "Dr. Nandini Reddy",
        "specialty": "Rheumatologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 76543 12349",
        "hospital": "Apollo Speciality Hospitals",
        "experience": "11 years",
        "qualifications": "MBBS, DM (Rheumatology)",
        "about": "Dr. Nandini Reddy specializes in arthritis and lupus. She is known for her holistic approach.",
        "services": ["Arthritis Treatment", "Lupus Management", "Autoimmune Disease Treatment", "Osteoporosis Care"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/45.jpg"
        },
        {
        "id": 46,
        "name": "Dr. Karthik Kapoor",
        "specialty": "Pulmonologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 65432 12349",
        "hospital": "MIOT International",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Pulmonology)",
        "about": "Dr. Karthik Kapoor specializes in asthma and COPD. He is known for his expertise in critical care.",
        "services": ["Asthma Management", "COPD Treatment", "Sleep Disorder Treatment", "Critical Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/46.jpg"
        },
        {
        "id": 47,
        "name": "Dr. Shalini Menon",
        "specialty": "Nephrologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 54321 12349",
        "hospital": "Sri Ramachandra Medical Centre",
        "experience": "14 years",
        "qualifications": "MBBS, DM (Nephrology)",
        "about": "Dr. Shalini Menon specializes in kidney transplants and dialysis. She is known for her compassionate care.",
        "services": ["Kidney Transplant", "Dialysis", "Chronic Kidney Disease Management", "Hypertension Care"],
        "languages": ["English", "Tamil", "Malayalam"],
        "image": "/static/images/47.jpg"
        },
        {
        "id": 48,
        "name": "Dr. Ravi Reddy",
        "specialty": "Ophthalmologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 43210 12349",
        "hospital": "Sankara Nethralaya",
        "experience": "16 years",
        "qualifications": "MBBS, MS (Ophthalmology)",
        "about": "Dr. Ravi Reddy specializes in cataract surgery and LASIK. He is known for his precision.",
        "services": ["Cataract Surgery", "LASIK", "Glaucoma Treatment", "Retinal Disorders"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/48.jpg"
        },
        {
        "id": 49,
        "name": "Dr. Anjali Kapoor",
        "specialty": "Gynecologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 98765 12350",
        "hospital": "Apollo Hospitals",
        "experience": "12 years",
        "qualifications": "MBBS, MD (Obstetrics & Gynecology)",
        "about": "Dr. Anjali Kapoor specializes in high-risk pregnancies and infertility treatments. She is known for her compassionate care.",
        "services": ["Pregnancy Care", "Infertility Treatment", "Laparoscopic Surgery", "Menopause Management"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/49.jpg"
        },
        {
        "id": 50,
        "name": "Dr. Rahul Reddy",
        "specialty": "Cardiologist",
        "location": "Chennai, India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "contact": "+91 87654 12350",
        "hospital": "Fortis Malar Hospital",
        "experience": "11 years",
        "qualifications": "MBBS, MD (Cardiology)",
        "about": "Dr. Rahul Reddy specializes in interventional cardiology and heart failure management. He is known for his innovative techniques.",
        "services": ["Angioplasty", "Pacemaker Implantation", "Heart Failure Management", "Preventive Cardiology"],
        "languages": ["English", "Tamil", "Hindi"],
        "image": "/static/images/50.jpg"
        },
]

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'vedagiri003@gmail.com'  # Replace with your email
SMTP_PASSWORD = 'ejszucigjehrdnsj'  # Replace with your email password or app password

def send_email(to_email, subject, body):
    """Send an email using SMTP."""
    try:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Enable debug logging
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send the email
        server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html', doctors=doctors)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        if username in users:
            flash('Username already exists.')
            return redirect(url_for('signup'))

        users[username] = {'password': password}
        flash('Account created successfully. Please login.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/doctors', methods=['GET'])
@login_required
def get_doctors():
    return jsonify(doctors)

@app.route('/doctor/<int:doctor_id>')
@login_required
def doctor_detail(doctor_id):
    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if doctor:
        # Create a map centered at the doctor's location
        doctor_map = folium.Map(location=[doctor["latitude"], doctor["longitude"]], zoom_start=15)
        folium.Marker(
            location=[doctor["latitude"], doctor["longitude"]],
            popup=doctor["name"],
            icon=folium.Icon(color="blue")
        ).add_to(doctor_map)
        map_html = doctor_map._repr_html_()
        return render_template('doctor_detail.html', doctor=doctor, map_html=map_html)
    else:
        return "Doctor not found", 404

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        doctor_id = request.form.get('doctor')
        consultation_type = request.form.get('consultation-type')
        location = request.form.get('location')
        reason = request.form.get('reason')
        date = request.form.get('date')


        # Save to database
        new_appointment = Appointment(
            name=name,
            email=email,
            phone=phone,
            doctor_id=doctor_id,
            consultation_type=consultation_type,
            location=location,
            reason=reason,
            date=date
        )
        db.session.add(new_appointment)
        db.session.commit()

        # Find the selected doctor
        doctor = next((doc for doc in doctors if doc["id"] == int(doctor_id)), None)

        # Prepare email content
        subject = "Appointment Confirmation"
        body = f"""
        Hello {name},

        Your appointment has been booked successfully.

        Appointment Details:
        - Doctor: {doctor['name']} ({doctor['specialty']})
        - Hospital: {doctor['hospital']}
        - Location: {location}
        - Consultation Type: {consultation_type}
        - Date: {date}
        - Reason: {reason}

        Thank you for choosing DocHub!
        """

        # Send email
        if send_email(email, subject, body):
            flash('Appointment booked successfully! A confirmation email has been sent.', 'success')
        else:
            flash('Appointment booked successfully, but failed to send confirmation email.', 'warning')

        return redirect(url_for('appointment'))

    # Fetch appointments from the database
    appointments = Appointment.query.all()
    return render_template('appointment.html', doctors=doctors, appointments=appointments)

if __name__ == '__main__':
    app.run(debug=True)