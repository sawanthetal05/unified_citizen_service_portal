from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import random
from datetime import date

app = Flask(__name__)
app.secret_key = "ucsp_secret"

DATABASE = "ucsp.db"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            mobile TEXT,
            address TEXT
        )
    ''')

    # Police complaints
    cur.execute('''
        CREATE TABLE IF NOT EXISTS complaints(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    user_email TEXT,
    department TEXT,
    type TEXT,
    date TEXT,
    location TEXT,
    description TEXT,
    status TEXT
    )
    ''')
   

    # Legal Cases table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS legal_cases(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_number TEXT,
        name TEXT,
        case_type TEXT,
        description TEXT,
        status TEXT
    )
''')

    # Certificate records
    cur.execute('''
        CREATE TABLE IF NOT EXISTS certificates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cert_no TEXT,
            cert_type TEXT,
            name TEXT,
            address TEXT,
            extra TEXT,
            date TEXT
        )
    ''')

    # Agents table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS agents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        department TEXT
    )
''')
    cur.execute("INSERT OR IGNORE INTO agents(name,email,password,department) VALUES(?,?,?,?)",
            ("Police Officer","police@ucsp.com","123","Police"))

    cur.execute("INSERT OR IGNORE INTO agents(name,email,password,department) VALUES(?,?,?,?)",
            ("Grievance Officer","grievance@ucsp.com","123","Grievance"))

    cur.execute("INSERT OR IGNORE INTO agents(name,email,password,department) VALUES(?,?,?,?)",
            ("Legal Officer","legal@ucsp.com","123","Legal"))

    conn.commit()
    conn.close()


init_db()


# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        address = request.form['address']

        conn = get_db()
        conn.execute(
            "INSERT INTO users(name,email,password,mobile,address) VALUES(?,?,?,?,?)",
            (name, email, password, mobile, address)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect(url_for('dashboard'))

    return render_template('login.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# ---------------- POLICE SERVICE ----------------
@app.route('/police', methods=['GET', 'POST'])
def police():
    if request.method == 'POST':
        name = request.form['name']
        
        # First get values
        complaint_type = request.form.get('type')
        other_type = request.form.get('other_type')

        # Then check for Other
        if complaint_type == "Other" and other_type:
            complaint_type = other_type

        date = request.form['date']
        location = request.form['location']
        description = request.form['description']

        conn = get_db()
        conn.execute(
            "INSERT INTO complaints (name, user_email, department, type, date, location, description, status) VALUES (?,?,?,?,?,?,?,?)",
            (name, session['user'], "Police", complaint_type, date, location, description, "Pending")
        )
        conn.commit()
        conn.close()

        return render_template('success.html', message="Complaint Submitted Successfully")

    from datetime import date

    return render_template('police.html', today=date.today().strftime("%Y-%m-%d"))
# ---------------- GRIEVANCE ----------------
@app.route('/grievance', methods=['GET', 'POST'])
def grievance():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        description = request.form['description']

        conn = get_db()
        conn.execute(
            "INSERT INTO complaints (name, user_email, department, type, date, location, description, status) VALUES (?,?,?,?,?,?,?,?)",
            (name, session['user'], "Grievance", subject, "", "", description, "Pending")
        )
        conn.commit()
        conn.close()

        return render_template('success.html', message="Grievance Submitted Successfully")

    return render_template('grievance.html')


# ---------------- GOVERNMENT SCHEMES ----------------
@app.route('/schemes', methods=['GET', 'POST'])
def schemes():
    schemes_list = []

    if request.method == 'POST':
        age = int(request.form['age'])
        income = int(request.form['income'])
        category = request.form['category']

        if income < 200000:
            schemes_list.append("PMAY")
            schemes_list.append("Ayushman Bharat")

        if category in ['SC', 'ST', 'OBC']:
            schemes_list.append("Scholarship Scheme")

        if age > 60:
            schemes_list.append("Senior Citizen Pension")

    return render_template('schemes.html', schemes=schemes_list)
# -------------------------------
# Court & Legal Assistant Module
# -------------------------------

# Main Court & Legal Page
@app.route('/court_legal')
def court_legal():
    return render_template('court_legal.html')


# Basic Legal Information
@app.route('/legal_info')
def legal_info():
    topics = {
        "Divorce": "You can file a divorce petition in family court under mutual consent or contested divorce.",
        "Property Dispute": "Property disputes are handled in civil courts based on ownership documents.",
        "Consumer Complaint": "You can file a complaint in Consumer Court for defective products or poor service."
    }
    return render_template('legal_info.html', topics=topics)


# Case Status Tracking
@app.route('/case_status', methods=['GET', 'POST'])
def case_status():
    case = None

    if request.method == 'POST':
        case_number = request.form['case_number']

        conn = get_db()
        case = conn.execute(
            "SELECT * FROM legal_cases WHERE case_number=?",
            (case_number,)
        ).fetchone()
        conn.close()

    return render_template('case_status.html', case=case)




# Advocate Directory
@app.route('/advocates')
def advocates():
    lawyers = [
        {"name": "Adv. Rajesh Sharma", "specialization": "Family Law", "contact": "9876543210"},
        {"name": "Adv. Meena Patil", "specialization": "Property Law", "contact": "9123456780"},
        {"name": "Adv. Amit Desai", "specialization": "Consumer Law", "contact": "9988776655"}
    ]
    return render_template('advocates.html', lawyers=lawyers)
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file

#------------file case routes-------------#
@app.route('/file_case', methods=['GET', 'POST'])
def file_case():
    if request.method == 'POST':
        name = request.form['name']
        case_type = request.form['case_type']
        description = request.form['description']

        case_number = "CASE" + str(random.randint(1000,9999))

        conn = get_db()
        conn.execute(
    "INSERT INTO legal_cases(case_number,name,case_type,description,status,user_email) VALUES(?,?,?,?,?,?)",
    (case_number, name, case_type, description, "Pending", session['user'])
)
        conn.commit()
        conn.close()

        # After submit → show success + download button
        return render_template('case_success.html', case_number=case_number)

    return render_template('file_case.html')
#--------download case-----------#
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

@app.route('/download_case/<case_number>')
def download_case(case_number):
    conn = get_db()
    case = conn.execute(
        "SELECT * FROM legal_cases WHERE case_number=?",
        (case_number,)
    ).fetchone()
    conn.close()

    if not case:
        return "Case not found"

    # PDF path
    file_path = f"static/case_{case_number}.pdf"

    # Create PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 50, "Citizen Service Portal")

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 80, "Legal Case Report")

    # Line
    c.line(50, height - 95, width - 50, height - 95)

    # Case Details
    y = height - 130
    c.setFont("Helvetica", 12)

    c.drawString(60, y, f"Case Number : {case['case_number']}")
    y -= 25
    c.drawString(60, y, f"Applicant Name : {case['name']}")
    y -= 25
    c.drawString(60, y, f"Case Type : {case['case_type']}")
    y -= 25

    # Description (multi-line support)
    c.drawString(60, y, "Description :")
    y -= 20
    text = c.beginText(80, y)
    text.setFont("Helvetica", 12)
    text.textLines(case['description'])
    c.drawText(text)
    y -= 60

    # Status Highlight
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, f"Current Status : {case['status']}")
    y -= 40

    # Legal Authority Section
    c.setFont("Helvetica", 12)
    c.drawString(60, y, "Assigned Authority : Court Legal Department")
    y -= 20
    c.drawString(60, y, "Portal : Unified Citizen Service Portal")
    y -= 40

    # Footer / Signature
    c.line(350, 120, width - 80, 120)
    c.drawString(360, 100, "Authorized Legal Officer")

    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 50, "This is a system generated legal document.")

    c.save()

    return send_file(file_path, as_attachment=True)

# ---------------- CERTIFICATE MODULE (NEW) ----------------
@app.route('/certificate', methods=['GET', 'POST'])
def certificate():
    if request.method == 'POST':
        cert_type = request.form['cert_type']
        name = request.form['name']
        address = request.form['address']
        extra = request.form['extra']

        cert_no = "MH/2026/" + str(random.randint(10000, 99999))
        today = date.today().strftime("%d/%m/%Y")

        # Save in database
        conn = get_db()
        conn.execute(
            "INSERT INTO certificates(cert_no,cert_type,name,address,extra,date) VALUES(?,?,?,?,?,?)",
            (cert_no, cert_type, name, address, extra, today)
        )
        conn.commit()
        conn.close()

        return render_template(
            'certificate.html',
            cert_type=cert_type,
            name=name,
            address=address,
            extra=extra,
            cert_no=cert_no,
            today=today
        )

    return render_template('certificate_form.html')

#------Agent login------------#
@app.route('/agent_login', methods=['GET','POST'])
def agent_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        agent = conn.execute(
            "SELECT * FROM agents WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()

        if agent:
            session['agent'] = email
            session['department'] = agent['department']
            return redirect(url_for('agent_dashboard'))

    return render_template('agent_login.html')
#--------Agent dashboard--------#

@app.route('/agent_dashboard')
def agent_dashboard():
    if 'agent' not in session:
        return redirect(url_for('agent_login'))

    department = session['department']
    conn = get_db()

    if department == "Police":
        data = conn.execute(
        "SELECT * FROM complaints WHERE department='Police'"
        ).fetchall()
        
    elif department == "Grievance":
        data = conn.execute(
        "SELECT * FROM complaints WHERE department='Grievance'"
        ).fetchall()
        
    elif department == "Legal":
        data = conn.execute(
            "SELECT * FROM legal_cases"
        ).fetchall()

    else:
        data = []

    conn.close()

    return render_template('agent_dashboard.html', data=data, dept=department)
# -------- Agent Status Update --------
@app.route('/update_status', methods=['POST'])
def update_status():
    if 'agent' not in session:
        return redirect(url_for('agent_login'))

    id = request.form['id']
    status = request.form['status']
    department = session['department']

    conn = get_db()

    # Police and Grievance → complaints table
    if department in ["Police", "Grievance"]:
        conn.execute(
            "UPDATE complaints SET status=? WHERE id=?",
            (status, id)
        )

    # Legal → legal_cases table
    elif department == "Legal":
        conn.execute(
            "UPDATE legal_cases SET status=? WHERE id=?",
            (status, id)
        )

    conn.commit()
    conn.close()

    return redirect(url_for('agent_dashboard'))

# -------- User Case Tracking -------- #
@app.route('/my_cases')
def my_cases():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    # Police + Grievance
    complaints = conn.execute(
        "SELECT id, department, type, description, status FROM complaints WHERE user_email=?",
        (session['user'],)
    ).fetchall()

    # Legal Cases (only if you saved user_email in legal_cases)
    legal_cases = conn.execute(
        "SELECT id, case_number, case_type as type, description, status FROM legal_cases WHERE user_email=?",
        (session['user'],)
    ).fetchall()

    conn.close()

    # Convert legal data to same format
    legal_list = []
    for case in legal_cases:
        legal_list.append({
            "id": case["id"],
            "department": "Legal",
            "type": case["type"],
            "description": case["description"],
            "status": case["status"],
            "case_number": case["case_number"]
        })

    # Convert complaints to list
    complaint_list = []
    for c in complaints:
        complaint_list.append({
            "id": c["id"],
            "department": c["department"],
            "type": c["type"],
            "description": c["description"],
            "status": c["status"],
            "case_number": None
        })

    all_cases = complaint_list + legal_list

    return render_template('my_cases.html', cases=all_cases)
# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

#---------Agent logout------#
@app.route('/agent_logout')
def agent_logout():
    session.pop('agent', None)
    return redirect(url_for('index'))


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)