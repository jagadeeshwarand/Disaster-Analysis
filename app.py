from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from flask import Flask, send_from_directory 
import mysql.connector
import os
from random import randint
from datetime import timedelta
import hashlib
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from flask import Flask, request, render_template, jsonify
import requests


class Config(object):
    # previous configurations

    # reCAPTCHA configuration
    RECAPTCHA_PUBLIC_KEY = os.environ.get('6LeJydUqAAAAAD9XnbUXXAj6_9EEMnc5VJvHitsN')
    RECAPTCHA_PRIVATE_KEY= os.environ.get('6LeJydUqAAAAAEkTXdYRB1WgIZmCNKAWLk2lPppi')
# Initialize Flask app
myapp = Flask(__name__)
myapp.secret_key = 'your_secret_key'
myapp.permanent_session_lifetime = timedelta(minutes=30)


# Dash App Initialization
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=myapp, url_base_pathname='/admin_dashboard/', external_stylesheets=external_stylesheets)

def fetch_data():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT disaster_type, status, DATE_FORMAT(disaster_date, '%Y-%m') AS month FROM fund_applications")
    data = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(data)

dash_app.layout = html.Div([
    html.H1("Admin Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    html.Div([
        dcc.Graph(id='status-bar-chart'),
        dcc.Graph(id='disaster-pie-chart'),
        dcc.Graph(id='monthly-trend-chart'),
        dcc.Graph(id='disaster-line-chart'),
        dcc.Graph(id='status-pie-chart')
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'padding': '20px'})
])

@dash_app.callback(
    [
        Output('status-bar-chart', 'figure'),
        Output('disaster-pie-chart', 'figure'),
        Output('monthly-trend-chart', 'figure'),
        Output('disaster-line-chart', 'figure'),
        Output('status-pie-chart', 'figure')
    ],
    [Input('status-bar-chart', 'id')]
)
def update_charts(_):
    df = fetch_data()
    
    # Bar Chart - Approval Status Breakdown
    status_fig = px.bar(df, x='status', title="Approval Status Breakdown", color='status', barmode='group')
    
    # Pie Chart - Disaster Type Distribution
    disaster_fig = px.pie(df, names='disaster_type', title="Disaster Type Analysis", hole=.3)
    
    # Line Chart - Applications Over Time
    trend_fig = px.line(df.groupby('month').size().reset_index(name='count'), x='month', y='count', title="Monthly Applications Trend")
    
    # Line Chart - Disaster Type Over Time
    disaster_line_fig = px.line(df.groupby(['month', 'disaster_type']).size().reset_index(name='count'), x='month', y='count', color='disaster_type', title="Disaster Type Over Time")
    
    # Pie Chart - Status Distribution
    status_pie_fig = px.pie(df, names='status', title="Status Distribution", hole=.3)
    
    return status_fig, disaster_fig, trend_fig, disaster_line_fig, status_pie_fig

# Ensure the upload folder exists
UPLOAD_FOLDER = 'static/uploads'
myapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
myapp.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png', 'pdf'}

# Database connection
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="disaster_relief"
    )
except mysql.connector.Error as err:
    print(f"Error: {err}")
    mydb = None

# Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in myapp.config['ALLOWED_EXTENSIONS']

@myapp.route('/')
def index():
    return render_template('index.html')  # Home Page

@myapp.route('/submit', methods=['POST'])
def submit():
    recaptcha_response = request.form.get('g-recaptcha-response')

    # Verify the CAPTCHA response with Google
    payload = {
        'secret': '6LeJydUqAAAAAEkTXdYRB1WgIZmCNKAWLk2lPppi',
        'response': recaptcha_response
    }
    r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = r.json()

    if result.get("success"):
        return "CAPTCHA verified successfully. Form submitted!"
    else:
        return "CAPTCHA verification failed. Please try again."

@myapp.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        if len(aadhar) != 12 or not aadhar.isdigit() or len(mobile) != 10 or not mobile.isdigit():
            msg = 'Invalid Aadhar or Mobile Number!'
        else:
            session['aadhar'] = aadhar
            session['email'] = email
            session['mobile'] = mobile
            session['password'] = password
            
            otp = str(randint(100000, 999999))
            session['otp'] = otp
            flash(f"Your OTP is: {otp}")  # Debugging only
            return redirect(url_for('otp'))
    
    return render_template('signup.html', msg=msg)

@myapp.route('/otp', methods=['GET', 'POST'])
def otp():
    msg = ''
    if 'aadhar' not in session or 'mobile' not in session:
        return redirect(url_for('signup'))

    if 'otp' not in session:
        session['otp'] = str(randint(100000, 999999))
        flash(f"Your OTP is: {session['otp']}")
    
    if request.method == 'POST':
        entered_otp = request.form['otp'].strip()

        if entered_otp == session.get('otp'):
            flash('OTP Verified Successfully!')
            session.pop('otp', None)
            return redirect(url_for('register_user'))
        else:
            msg = 'Incorrect OTP! Please try again.' 
    
    return render_template('otp.html', msg=msg)

import hashlib

@myapp.route('/register', methods=['GET', 'POST'])
def register_user():
    msg = ''

    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        area = request.form['area']
        taluk = request.form['taluk']
        state = request.form['state']
        district = request.form['district']
        pincode = request.form['pincode']
        contact = request.form['contact']
        email = request.form['email']
        password = session.get('password')  # Get password from session
        recaptcha_response = request.form.get('g-recaptcha-response')

        if not password:
            msg = "Password not found in session. Please try signing up again."
            return render_template('register_user.html', msg=msg)

         # Verify the CAPTCHA response with Google
        payload = {
            'secret': os.environ.get('6LeJydUqAAAAAEkTXdYRB1WgIZmCNKAWLk2lPppi'),
            'response': recaptcha_response
        }
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
        result = r.json()

        # Hash the password before storing it
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            mycursor = mydb.cursor()
            mycursor.execute('SELECT * FROM user_registration WHERE contact = %s', (contact,))
            account = mycursor.fetchone()

            if account:
                msg = 'User already exists!'
            else:
                mycursor.execute(
                    'INSERT INTO user_registration (name, gender, dob, address, area, taluk, state, district, pincode, contact, email, password) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (name, gender, dob, address, area, taluk, state, district, pincode, contact, email, hashed_password)
                )
                mydb.commit()
                flash('Registration successful! Please login.')

                # Log the user in automatically
                session['loggedin'] = True
                session['name'] = name
                session['contact'] = contact
                return redirect(url_for('user_dashboard'))  # Redirect to dashboard

        except mysql.connector.Error as err:
            msg = f"Database error: {err}"
    
    return render_template('register_user.html', msg=msg)


@myapp.route('/profile')
def user_profile():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))
    
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT name, gender, dob, address, area, taluk, state, district, pincode, contact, email FROM user_registration WHERE contact = %s", (session['contact'],))

    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return render_template('user_profile.html', user=user)
    else:
        flash("User profile not found!")
        return redirect(url_for('user_dashboard'))

@myapp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))

    msg = ''
    cursor = mydb.cursor(dictionary=True)
    
    # Fetch user details
    cursor.execute("SELECT * FROM user_registration WHERE contact = %s", (session['contact'],))
    user = cursor.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        area = request.form['area']
        taluk = request.form['taluk']
        state = request.form['state']
        district = request.form['district']
        pincode = request.form['pincode']
        email = request.form['email']
        contact = request.form['contact']

        try:
            # Update user details in the database
            update_sql = '''UPDATE user_registration 
                            SET name = %s, gender = %s, dob = %s, address = %s, area = %s, 
                                taluk = %s, state = %s, district = %s, pincode = %s, 
                                email = %s, contact = %s
                            WHERE contact = %s'''
            cursor.execute(update_sql, (name, gender, dob, address, area, taluk, state, district, pincode, email, contact, session['contact']))
            mydb.commit()

            # Update session details
            session['name'] = name
            session['email'] = email
            session['contact'] = contact

            flash("Profile updated successfully!", "success")
            return redirect(url_for('user_profile'))

        except mysql.connector.Error as err:
            msg = f"Database error: {err}"

    cursor.close()
    return render_template('edit_profile.html', user=user, msg=msg)



@myapp.route('/login', methods=['GET', 'POST'])
def user_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hash the entered password to compare with stored hash
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mydb.cursor(dictionary=True)  # Use dictionary=True to get column names
        cursor.execute('SELECT * FROM user_registration WHERE email = %s AND password = %s', (email, hashed_password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['email'] = account['email']
            session['name'] = account['name']
            session['contact'] = account['contact']

            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))  # Redirect to dashboard
        else:
            msg = 'Incorrect email or password!'

    return render_template('user_login.html', msg=msg)


@myapp.route('/dashboard')
def user_dashboard():
    if 'loggedin' in session:
        return render_template('user_dashboard.html', name=session['name'], email=session['email'])
    flash('Please log in first!', 'warning')
    return redirect(url_for('user_login'))


@myapp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in myapp.config['ALLOWED_EXTENSIONS']


@myapp.route('/fund_apply', methods=['GET', 'POST'])
def fund_apply():
    if 'loggedin' not in session:
        flash("Please log in to apply for disaster relief funds.", "warning")
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    msg = ''

    if request.method == 'POST':
        name = request.form['name']
        disaster_type = request.form['disasters']
        disaster_date = request.form['date']
        damage_description = request.form['damage']
        
        # File upload handling
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('No file selected. Please upload proof (JPG, PNG, PDF).', 'danger')
            return render_template('fund_apply.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(myapp.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save file
            
            try:
                # Create a cursor here
                mycursor = mydb.cursor()

                sql = "INSERT INTO fund_applications (name, disaster_type, disaster_date, damage_description, file_path) VALUES (%s, %s, %s, %s, %s)"
                values = (name, disaster_type, disaster_date, damage_description, file_path)
                
                mycursor.execute(sql, values)
                mydb.commit()
                mycursor.close()
                
                flash('Application submitted successfully! You can check your status.', 'success')
                return redirect(url_for('status'))  # Redirect to status page


            except Exception as e:
                mydb.rollback()
                msg = f"Error: {e}"
        else:
            msg = 'Invalid file format! Only jpg, png, and pdf allowed.'

    return render_template('fund_apply.html', msg=msg)

@myapp.route('/status')
def status():
    if 'loggedin' not in session:
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    try:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM fund_applications WHERE name = %s", (session['name'],))
        applications = cursor.fetchall()
        cursor.close()

        if applications:
            return render_template('status.html', applications=applications)
        else:
            flash('No applications found. Please wait for processing.', 'warning')
            return render_template('status.html', applications=[])


    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'danger')
        return render_template('status.html', applications=[], error=True)



@myapp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, hashed_password))
        account = cursor.fetchone()
        
        if account:
            session['admin_loggedin'] = True
            session['admin_email'] = account['email']
            return redirect(url_for('admin_dashboard'))
        else:
            msg = 'Incorrect admin credentials!'

    return render_template('admin_login.html', msg=msg)

@myapp.route('/bank_details', methods=['GET', 'POST'])
def bank_details():
    # Ensure the user is logged in
    if 'loggedin' not in session:
        flash("Please log in to submit bank details.", "warning")
        return redirect(url_for('user_login'))

    msg = ''
    if request.method == 'POST':
        # Get form data
        account_holder_name = request.form['account_holder_name']
        bank_name = request.form['bank_name']
        account_number = request.form['account_number']
        ifsc_code = request.form['ifsc_code']
        branch = request.form.get('branch', '')  # Optional field

        # (Optionally, add input validations here)

        try:
            mycursor = mydb.cursor()
            sql = '''INSERT INTO bank_details 
                     (user_contact, account_holder_name, bank_name, account_number, ifsc_code, branch)
                     VALUES (%s, %s, %s, %s, %s, %s)'''
            values = (session['contact'], account_holder_name, bank_name, account_number, ifsc_code, branch)
            mycursor.execute(sql, values)
            mydb.commit()
            mycursor.close()

            flash("Bank details submitted successfully!", "success")
            # Redirect to status page or another page as needed
            return redirect(url_for('status'))

        except mysql.connector.Error as err:
            msg = f"Database error: {err}"

    return render_template('bank_details.html', msg=msg)



@myapp.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin_login'))

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fund_applications WHERE status = 'Pending'")
    applications = cursor.fetchall()
    cursor.close()
    
    return render_template('admin_dashboard.html', applications=applications)


@myapp.route('/update_status/<int:app_id>/<status>')
def update_status(app_id, status):
    if 'admin_loggedin' not in session:
        return redirect(url_for('admin_login'))

    if status not in ["Approved", "Denied"]:
        flash("Invalid action!", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        cursor = mydb.cursor()
        cursor.execute("UPDATE fund_applications SET status = %s WHERE id = %s", (status, app_id))
        mydb.commit()
        cursor.close()
        flash(f"Application {status} successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")

    return redirect(url_for('admin_dashboard'))

@myapp.route('/admin_logout')
def admin_logout():
    session.pop('admin_loggedin', None)
    session.pop('admin_email', None)
    flash("Admin logged out successfully.", "success")
    return redirect(url_for('admin_login'))

@myapp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(myapp.config['UPLOAD_FOLDER'], filename)

@myapp.route('/view-proof/<filename>')
def view_proof(filename):
    return send_from_directory(myapp.config['UPLOAD_FOLDER'], filename)

file_path = os.path.join(myapp.config['UPLOAD_FOLDER'], 'your_filename_here').replace("\\", "/")

#     # Insert Admin Account Setup Logic Here (once only)
admin_password = 'admin123'  # The password you want to store for the admin user
hashed_admin_password = hashlib.sha256(admin_password.encode()).hexdigest()
print(f"Hashed Admin Password: {hashed_admin_password}")  # Display the hashed password

try:
        mycursor = mydb.cursor()
        admin_email = 'admin@admin.com'  # Admin email

        # Check if admin record already exists
        mycursor.execute('SELECT * FROM admin WHERE email = %s', (admin_email,))
        account = mycursor.fetchone()

        if not account:
            sql = "INSERT INTO admin (email, password) VALUES (%s, %s)"
            values = (admin_email, hashed_admin_password)

            mycursor.execute(sql, values)
            mydb.commit()
            print("Admin record created successfully!")
        else:
            print("Admin record already exists.")

except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == '__main__':
    myapp.run(debug=True)