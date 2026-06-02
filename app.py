
from reportlab.platypus import SimpleDocTemplate,Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from flask import Flask ,render_template,request,redirect,url_for,session
import sqlite3

app= Flask(__name__)
app.secret_key='miniproject' 

# ---------------- DATABASE SETUP ----------------
import sqlite3
def init_db():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # REQUEST TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        regno TEXT,
        department TEXT,
        date TEXT,
        reason TEXT,
        status TEXT,
        request_type TEXT
    )
    """)

    # STUDENT TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        regno TEXT,
        password TEXT
    )
    """)

    # FACULTY TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS faculty (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/student')
def student():
    return render_template('student.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/faculty')
def faculty():
    return render_template('faculty.html')

@app.route('/request')
def request_page():
    return render_template('request.html')

@app.route('/leave')
def leave():
    return render_template('leave.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/update_status/<int:id>/<status>")
def update_status(id, status):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        UPDATE requests
        SET status = ?
        WHERE id = ?
    """, (status, id))

    conn.commit()
    conn.close()

    return "Updated"


@app.route('/student_login', methods=['POST'])
def student_login():

    regno = request.form['regno']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM students
    WHERE regno=? AND password=?
    """, (regno, password))

    user = cur.fetchone()

    conn.close()

    if user:
        session['regno']=regno
        return redirect(url_for('dashboard'))

    else:
        return "Invalid Student Login"
    
@app.route('/faculty_login', methods=['POST'])
 
def faculty_login():

    name = request.form['name']
    password = request.form['password']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM faculty
    WHERE name=? AND password=?
    """, (name, password))

    user = cur.fetchone()

    conn.close()

    if user:
        return redirect(url_for('faculty_dashboard'))

    else:
        return "Invalid Faculty Login"

# ---------------- OD REQUEST ----------------
@app.route('/submit_request', methods=['POST'])
def submit_request():

    name = request.form['name']
    regno = request.form['regno']
    department = request.form['department']
    date = request.form['date']
    reason = request.form['reason']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO requests
    (name, regno, department, date, reason, status, request_type)

    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,

    (
        name,
        regno,
        department,
        date,
        reason,
        "Pending",
        "OD"
    )
    )

    conn.commit()
    conn.close()

    return render_template("request.html", success=True)
# ---------------- LEAVE REQUEST ----------------
@app.route('/submit_leave', methods=['POST'])
def submit_leave():

    name = request.form['name']
    regno = request.form['regno']
    department = request.form['department']
    date = request.form['date']
    reason = request.form['reason']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO requests
    (name, regno, department, date, reason, status,request_type)

    VALUES (?, ?, ?, ?, ?, ?,?)
    """, (name, regno, department,
          date, reason, "Pending","LEAVE"))

    conn.commit()
    conn.close()

    return render_template('leave.html',success=True)

# ---------------- FACULTY DASHBOARD ----------------
@app.route('/fdashboard')
def faculty_dashboard():

    search = request.args.get('search')

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if search:

        cur.execute(
            "SELECT * FROM requests WHERE regno=?",
            (search,)
        )

    else:

        cur.execute(
            "SELECT * FROM requests"
        )
    data = cur.fetchall()

    # Statistics

    cur.execute("SELECT COUNT(*) FROM requests")
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Accepted'"
    )
    accepted = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Rejected'"
    )
    rejected = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM requests WHERE status='Pending'"
    )
    pending = cur.fetchone()[0]

    conn.close()

    return render_template(
        "fdashboard.html",
        data=data,
        total=total,
        accepted=accepted,
        rejected=rejected,
        pending=pending,
    )

# ---------------- ACCEPT / REJECT ----------------
@app.route('/update/<int:id>/<action>')
def update(id, action):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("UPDATE requests SET status=? WHERE id=?", (action, id))

    conn.commit()
    conn.close()

    return redirect(url_for('faculty_dashboard'))

@app.route('/accept/<int:id>')
def accept(id):

    print("ACCEPT CLICKED", id)

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE requests SET status='Accepted' WHERE id=?",
        (id,)
    )

    print("Rows Updated:", cur.rowcount)

    conn.commit()
    conn.close()

    return redirect(url_for('faculty_dashboard'))

@app.route('/reject/<int:id>')
def reject(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "UPDATE requests SET status='Rejected' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('faculty_dashboard'))
# ---------------- VEIW STATUS ----------------
@app.route('/view_status')
def view_status():
    regno=session['regno']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM requests WHERE regno=?",
        (regno,)
        )

    data = cur.fetchall()

    conn.close()

    return render_template(
        "view_status.html",
        data=data
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))
# ---------------- DOWNLOAD PDF ----------------
@app.route('/download_pdf/<int:id>')
def download_pdf(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM requests WHERE id=?",
        (id,)
    )

    row = cur.fetchone()

    conn.close()

    pdf = SimpleDocTemplate("approval_letter.pdf")

    styles = getSampleStyleSheet()
    content = [

    Paragraph("SRI RAMAKRISHNA COLLEGE OF ARTS AND SCIENCE", styles['Title']),
    Paragraph("<br/>", styles['Normal']),

    Paragraph("OD / LEAVE APPROVAL LETTER", styles['Heading2']),
    Paragraph("<br/>", styles['Normal']),

    Paragraph(f"Student Name : {row[1]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),

    Paragraph(f"Register Number : {row[2]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),

    Paragraph(f"Department : {row[3]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),

    Paragraph(f"Date : {row[4]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),

    Paragraph(f"Reason : {row[5]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),


    Paragraph(f"Status : {row[6]}", styles['Normal']),
    Paragraph("<br/><br/>", styles['Normal']),

    Paragraph("Faculty Signature", styles['Normal']),
    Paragraph("__________________", styles['Normal'])
]
    
    pdf.build(content)

    return send_file(
        "approval_letter.pdf",
        as_attachment=True
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

