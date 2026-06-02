from flask import Flask, request
from datetime import date
import pymysql

app=Flask(__name__)

db=pymysql.connect(
host='attendance-db.cd660kgyuxje.eu-north-1.rds.amazonaws.com',
user='admin',
password='admin12345',
database='attendance_system'
)

# HOME PAGE
@app.route('/')
def home():

    return '''

<html>
<body style="
font-family:Arial;
background:linear-gradient(to right,#4facfe,#00f2fe);
text-align:center;
padding-top:80px;
height:100vh;">

<div style="
background:white;
width:500px;
margin:auto;
padding:40px;
border-radius:20px;
box-shadow:0px 0px 20px gray;">

<h1 style="color:#2c3e50;">
📚 Student Attendance Management System
</h1>

<br>

<a href="/signup">

<button style="
padding:15px;
width:250px;
background:#28a745;
color:white;
font-size:18px;
border:none;
border-radius:10px;">

Student Sign Up

</button>

</a>

<br><br>

<a href="/login">

<button style="
padding:15px;
width:250px;
background:#007bff;
color:white;
font-size:18px;
border:none;
border-radius:10px;">

Teacher Login

</button>

</a>

</div>

</body>
</html>
'''


# STUDENT SIGNUP
@app.route('/signup')
def signup():

    return '''

<html>
<body style="
background:linear-gradient(to right,#ff9966,#ff5e62);
font-family:Arial;
text-align:center;
padding-top:80px;
height:100vh;">

<div style="
background:white;
width:450px;
margin:auto;
padding:30px;
border-radius:20px;">

<h1>👨‍🎓 Student Registration</h1>

<form action="/save_student" method="post">

<input type="text"
name="roll"
placeholder="Roll Number"
required>

<br><br>

<input type="text"
name="student"
placeholder="Student Name"
required>

<br><br>

<button style="
background:green;
color:white;
padding:10px;
border:none;
border-radius:10px;">

Register

</button>

</form>

</div>

</body>
</html>

'''


@app.route('/save_student',methods=['POST'])
def save_student():

    roll=request.form['roll']
    student=request.form['student']

    cursor=db.cursor()

    cursor.execute(
    """
    INSERT INTO students
    (roll_no,student_name)
    VALUES(%s,%s)
    """,
    (roll,student)
    )

    db.commit()

    return '''
    <center>
    <h2>Student Added Successfully</h2>
    <a href="/">Home</a>
    </center>
    '''


# LOGIN
@app.route('/login')
def login():

    return '''

<html>

<body style="
background:linear-gradient(to right,#667eea,#764ba2);
font-family:Arial;
text-align:center;
padding-top:100px;
height:100vh;">

<div style="
background:white;
width:400px;
margin:auto;
padding:30px;
border-radius:20px;">

<h1>👨‍🏫 Teacher Login</h1>

<form action="/check" method="post">

<input
type="text"
name="user"
placeholder="Username">

<br><br>

<input
type="password"
name="pass"
placeholder="Password">

<br><br>

<button style="
background:#007bff;
color:white;
padding:10px;
border:none;
border-radius:10px;">

Login

</button>

</form>

</div>

</body>

</html>

'''


@app.route('/check',methods=['POST'])
def check():

    user=request.form['user']
    pw=request.form['pass']

    cursor=db.cursor()

    cursor.execute(
    """
    SELECT *
    FROM users
    WHERE username=%s
    AND password=%s
    """,
    (user,pw)
    )

    if cursor.fetchone():

        return '''
        <script>
        window.location="/attendance"
        </script>
        '''

    return "Invalid Login"


# ATTENDANCE PAGE
@app.route('/attendance')
def attendance():

    cursor=db.cursor()

    cursor.execute(
    "SELECT student_name FROM students"
    )

    students=cursor.fetchall()

    rows=""

    for s in students:

        rows+=f'''

<tr>

<td>{s[0]}</td>

<td>

<input
type="checkbox"
name="present"
value="{s[0]}">

</td>

</tr>

'''

    return f'''

<html>

<body style="
background:linear-gradient(to right,#43cea2,#185a9d);
font-family:Arial;
text-align:center;
padding-top:50px;">

<div style="
background:white;
width:700px;
margin:auto;
padding:30px;
border-radius:20px;">

<h1>Take Attendance</h1>

<form action="/submit"
method="post">

Teacher:

<input
name="teacher"
required>

<br><br>

Subject:

<input
name="subject"
required>

<br><br>

Period:

<input
name="period"
required>

<br><br>

<table border=1 align=center>

<tr>

<th>Student</th>
<th>Present</th>

</tr>

{rows}

</table>

<br>

<button style="
background:green;
color:white;
padding:10px;
border:none;
border-radius:10px;">

Save Attendance

</button>

</form>

</div>

</body>
</html>

'''


@app.route('/submit',methods=['POST'])
def submit():

    teacher=request.form['teacher']
    subject=request.form['subject']
    period=request.form['period']

    selected=request.form.getlist("present")

    cursor=db.cursor()

    cursor.execute(
    "SELECT student_name FROM students"
    )

    students=cursor.fetchall()


    # Insert / Update attendance

    for s in students:

        student=s[0]

        status="Absent"

        if student in selected:
            status="Present"


        # Check existing record

        cursor.execute(
        """
        SELECT id
        FROM attendance
        WHERE teacher_name=%s
        AND student_name=%s
        AND period_no=%s
        """,

        (
        teacher,
        student,
        period
        )
        )

        existing=cursor.fetchone()


        # Update existing row

        if existing:

            cursor.execute(
            """
            UPDATE attendance
            SET
            status=%s,
            subject=%s,
            attendance_date=CURDATE()

            WHERE id=%s
            """,

            (
            status,
            subject,
            existing[0]
            )
            )


        # Insert new row

        else:

            cursor.execute(
            """
            INSERT INTO attendance
            (
            teacher_name,
            student_name,
            status,
            subject,
            period_no,
            attendance_date
            )

            VALUES
            (%s,%s,%s,%s,%s,CURDATE())
            """,

            (
            teacher,
            student,
            status,
            subject,
            period
            )
            )



    # Attendance percentage calculation

    for s in students:

        student=s[0]

        # Total classes by teacher

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE student_name=%s
        AND teacher_name=%s
        """,

        (
        student,
        teacher
        )
        )

        total=cursor.fetchone()[0]


        # Present classes by teacher

        cursor.execute(
        """
        SELECT COUNT(*)
        FROM attendance
        WHERE student_name=%s
        AND teacher_name=%s
        AND status='Present'
        """,

        (
        student,
        teacher
        )
        )

        present=cursor.fetchone()[0]


        percentage=0

        if total>0:

            percentage=(present/total)*100


        cursor.execute(
        """
        UPDATE attendance
        SET attendance_percentage=%s
        WHERE student_name=%s
        AND teacher_name=%s
        """,

        (
        percentage,
        student,
        teacher
        )
        )


    db.commit()


    return '''

    <html>

    <body align=center
    style="
    font-family:Arial;
    padding-top:100px;
    background:linear-gradient(
    to right,
    #56ccf2,
    #2f80ed);
    height:100vh;">

    <div style="
    background:white;
    width:500px;
    margin:auto;
    padding:30px;
    border-radius:20px;">

    <h2>

    Attendance Updated Successfully

    </h2>

    <br>

    <a href="/report">

    <button>

    View Report

    </button>

    </a>

    <br><br>

    <a href="/analysis">

    <button>

    Student Analysis

    </button>

    </a>

    </div>

    </body>

    </html>

    '''


@app.route('/report')
def report():

    cursor=db.cursor()

    cursor.execute(
    """
    SELECT DISTINCT
    teacher_name,
    subject,
    period_no

    FROM attendance

    ORDER BY teacher_name,period_no
    """
    )

    sessions=cursor.fetchall()

    output=""

    for s in sessions:

        teacher=s[0]
        subject=s[1]
        period=s[2]

        output += f'''

        <div style="
        background:white;
        width:900px;
        margin:auto;
        padding:20px;
        border-radius:20px;
        margin-bottom:40px;
        box-shadow:0px 0px 15px gray;">

        <h2 style="color:#2c3e50;">

        👨‍🏫 Teacher : {teacher}

        </h2>

        <h3>

        📘 Subject : {subject}

        &nbsp;&nbsp;&nbsp;

        ⏰ Period : {period}

        </h3>

        <table border=1 align=center>

        <tr>

        <th>ID</th>
        <th>Student</th>
        <th>Status</th>
        <th>Date</th>
        <th>Percentage</th>

        </tr>

        '''

        cursor.execute(
        """
        SELECT
        student_name,
        status,
        attendance_date,
        attendance_percentage

        FROM attendance

        WHERE teacher_name=%s
        AND subject=%s
        AND period_no=%s
        """,

        (
        teacher,
        subject,
        period
        )
        )

        data=cursor.fetchall()

        count=1

        for r in data:

            color="green"

            if r[1]=="Absent":
                color="red"

            output += f'''

            <tr>

            <td>{count}</td>
            <td>{r[0]}</td>

            <td style="
            color:{color};
            font-weight:bold;">

            {r[1]}

            </td>

            <td>{r[2]}</td>

            <td>{round(r[3],2)}%</td>

            </tr>

            '''

            count+=1

        output += "</table></div>"


    return f'''

    <html>

    <body style="
    background:linear-gradient(
    to right,
    #89f7fe,
    #66a6ff);

    font-family:Arial;
    text-align:center;">

    <h1>

    📊 Attendance Report

    </h1>

    {output}

    </body>

    </html>
    '''
@app.route('/analysis')
def analysis():

    cursor=db.cursor()

    cursor.execute(
    """
    SELECT DISTINCT student_name
    FROM attendance
    """
    )

    students=cursor.fetchall()

    output=""

    for s in students:

        student=s[0]

        output += f'''

        <div style="
        background:white;
        width:850px;
        margin:auto;
        padding:20px;
        border-radius:20px;
        margin-bottom:30px;
        box-shadow:0px 0px 10px gray;">

        <h2>{student}</h2>

        <h3>Subject-wise Attendance</h3>

        <table border=1 align=center>

        <tr>

        <th>Subject</th>
        <th>Total Classes</th>
        <th>Present</th>
        <th>Absent</th>
        <th>Percentage</th>

        </tr>

        '''

        cursor.execute(
        """
        SELECT DISTINCT subject
        FROM attendance
        WHERE student_name=%s
        """,
        (student,)
        )

        subjects=cursor.fetchall()

        for sub in subjects:

            subject=sub[0]

            cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE student_name=%s
            AND subject=%s
            """,
            (student,subject)
            )

            total=cursor.fetchone()[0]


            cursor.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            WHERE student_name=%s
            AND subject=%s
            AND status='Present'
            """,
            (student,subject)
            )

            present=cursor.fetchone()[0]

            absent=total-present

            percentage=(present/total)*100 if total>0 else 0


            output += f'''

            <tr>

            <td>{subject}</td>
            <td>{total}</td>
            <td>{present}</td>
            <td>{absent}</td>
            <td>{round(percentage,2)}%</td>

            </tr>

            '''


        output += '''

        </table>

        <hr>

        <h3>Day-wise Details</h3>

        <table border=1 align=center>

        <tr>

        <th>Date</th>
        <th>Teacher</th>
        <th>Subject</th>
        <th>Period</th>
        <th>Status</th>

        </tr>

        '''

        cursor.execute(
        """
        SELECT
        attendance_date,
        teacher_name,
        subject,
        period_no,
        status

        FROM attendance

        WHERE student_name=%s
        """,
        (student,)
        )

        records=cursor.fetchall()

        for r in records:

            color="green"

            if r[4]=="Absent":
                color="red"

            output += f'''

            <tr>

            <td>{r[0]}</td>
            <td>{r[1]}</td>
            <td>{r[2]}</td>
            <td>{r[3]}</td>

            <td style="
            color:{color};
            font-weight:bold;">

            {r[4]}

            </td>

            </tr>

            '''

        output += "</table></div>"


    return f'''

    <html>

    <body style="
    background:linear-gradient(
    to right,
    #56ccf2,
    #2f80ed);

    font-family:Arial;
    text-align:center;">

    <h1>

    📊 Student Subject-wise Analysis

    </h1>

    {output}

    </body>

    </html>

    '''


app.run(
host='0.0.0.0',
port=5000,
debug=True
)
