from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from random import randint
import os
import hashlib
from django.conf import settings
import mysql.connector
from django.db import connection as mydb
from django.conf import settings
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required



# Create your views here.
def index(request):
    return render(request, 'index.html')

def signup(request):
    msg = ''
    if request.method == 'POST':
        aadhar = request.POST.get('aadhar')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')

        if len(aadhar) != 12 or not aadhar.isdigit() or len(mobile) != 10 or not mobile.isdigit():
            msg = 'Invalid Aadhar or Mobile Number!'
        else:
            request.session['aadhar'] = aadhar
            request.session['email'] = email
            request.session['mobile'] = mobile
            request.session['password'] = password
            
            otp = str(randint(100000, 999999))
            request.session['otp'] = otp
            messages.info(request, f"Your OTP is: {otp}")  # Debugging only
            return redirect('otp')

    return render(request, 'signup.html', {'msg': msg})

def otp(request):
    msg = ''
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == request.session['otp']:
            return redirect('register_user')
        else:
            msg = 'Invalid OTP!'
    return render(request, 'otp.html', {'msg': msg})


def register_user(request):
    import mysql.connector

    msg = ''

    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        area = request.POST.get('area')
        taluk = request.POST.get('taluk')
        state = request.POST.get('state')
        district = request.POST.get('district')
        pincode = request.POST.get('pincode')
        contact = request.POST.get('contact')
        email = request.POST.get('email')
        password = request.session.get('password')  # Get password from session


        if not password:
            msg = "Password not found in session. Please try signing up again."
            return render(request, 'register_user.html', {'msg': msg})

        # Verify the CAPTCHA response with Google

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
                messages.success(request, 'Registration successful! Please login.')

                # Log the user in automatically
                request.session['loggedin'] = True
                request.session['name'] = name
                request.session['contact'] = contact
                return redirect('user_dashboard')  # Redirect to dashboard

        except mysql.connector.Error as err:
            msg = f"Database error: {err}"

    return render(request, 'register_user.html', {'msg': msg})



def user_login(request):
    msg = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
      

        # Hash the entered password to compare with stored hash
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM user_registration WHERE email = %s AND password = %s', (email, hashed_password))
        account = cursor.fetchone()

        if account:
            print('go')
            request.session['loggedin'] = True
            request.session['email'] = account[11]  # Assuming email is the 12th column
            request.session['name'] = account[1]  # Assuming name is the 2nd column
            request.session['contact'] = account[10]  # Assuming contact is the 11th column

            messages.success(request, 'Login successful!')
            return redirect('user_dashboard')  # Redirect to dashboard
        else:
            msg = 'Incorrect email or password!'

    return render(request, 'user_login.html', {'msg': msg})

def user_dashboard(request):
    if 'loggedin' in request.session:
        return render(request, 'user_dashboard.html', {
            'name': request.session['name'],
            'email': request.session['email']
        })
    messages.warning(request, 'Please log in first!')
    return redirect('user_login')
  

def admin_login(request):
    msg = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE email = %s AND password = %s', (email, hashed_password))
        account = cursor.fetchone()
        
        if account:
            request.session['admin_loggedin'] = True
            request.session['admin_email'] = account[1]  # Assuming email is the 2nd column
            return redirect('admin_dashboard')
        else:
            msg = 'Incorrect admin credentials!'
          


    return render(request, 'admin_login.html', {'msg': msg})



def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    applications = FundApplication.objects.filter(status='Pending')
    
    return render(request, 'admin_dashboard.html', {'applications': applications})




def user_profile(request):
    if 'loggedin' not in request.session:
        return redirect('user_login')
    
    cursor = mydb.cursor()
    cursor.execute("SELECT name, gender, dob, address, area, taluk, state, district, pincode, contact, email FROM user_registration WHERE contact = %s", (request.session['contact'],))
    
    user = cursor.fetchone()
    cursor.close()
    if user:
        return render(request, 'user_profile.html', {'user': user})
    else:
        messages.warning(request, "User profile not found!")
        return redirect('user_dashboard')

def logout(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully!')
    return redirect('user_login')

def fund_apply(request):
    if 'loggedin' not in request.session:
        messages.warning(request, "Please log in to apply for disaster relief funds.")
        return redirect('user_login')  # Redirect to login if not logged in

    msg = ''

    if request.method == 'POST':
        name = request.POST.get('name')
        disaster_type = request.POST.get('disasters')
        disaster_date = request.POST.get('date')
        damage_description = request.POST.get('damage')
        
        # File upload handling
        file = request.FILES.get('file')

        if not file or file.name == '':
            messages.error(request, 'No file selected. Please upload proof (JPG, PNG, PDF).')
            return render(request, 'fund_apply.html')
        
        if file and allowed_file(file.name):
            filename = secure_filename(file.name)
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            try:
                cursor = mydb.cursor()

                sql = "INSERT INTO fund_applications (name, disaster_type, disaster_date, damage_description, file_path) VALUES (%s, %s, %s, %s, %s)"
                values = (name, disaster_type, disaster_date, damage_description, file_path)
                
                cursor.execute(sql, values)
                mydb.commit()
                cursor.close()
                
                messages.success(request, 'Application submitted successfully! You can check your status.')
                return redirect('status')  # Redirect to status page

            except Exception as e:
                mydb.rollback()
                msg = f"Error: {e}"
        else:
            msg = 'Invalid file format! Only jpg, png, and pdf allowed.'

    return render(request, 'fund_apply.html', {'msg': msg})

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename(filename):
    return filename.replace(" ", "_").replace("(", "").replace(")", "")

def uploaded_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if default_storage.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        messages.error(request, 'File not found.')
        return redirect('user_dashboard')

def view_proof(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if default_storage.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        messages.error(request, 'File not found.')
        return redirect('user_dashboard')

    # Insert Admin Account Setup Logic Here (once only)
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

    except Exception as err:
        print(f"Error: {err}")

def status(request):
    if 'loggedin' not in request.session:
        return redirect('user_login')  # Redirect to login if not logged in

    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM fund_applications WHERE name = %s", (request.session['name'],))
        applications = cursor.fetchall()
        cursor.close()

        if applications:
            return render(request, 'status.html', {'applications': applications})
        else:
            messages.warning(request, 'No applications found. Please wait for processing.')
            return render(request, 'status.html', {'applications': []})
    except mysql.connector.Error as err:

        messages.error(request, f"Database error: {err}")
        return render(request, 'status.html', {'applications': [], 'error': True})

def edit_profile(request):
    if 'loggedin' in request.session:
        msg = ''
        if request.method == 'POST':
            name = request.POST.get('name')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            address = request.POST.get('address')
            area = request.POST.get('area')
            taluk = request.POST.get('taluk')
            state = request.POST.get('state')
            district = request.POST.get('district')
            pincode = request.POST.get('pincode')
            contact = request.POST.get('contact')
            email = request.POST.get('email')

            try:
                cursor = mydb.cursor()
                cursor.execute('UPDATE user_registration SET name = %s, gender = %s, dob = %s, address = %s, area = %s, taluk = %s, state = %s, district = %s, pincode = %s, contact = %s, email = %s WHERE contact = %s',
                                (name, gender, dob, address, area, taluk, state, district, pincode, contact, email, request.session['contact']))
                mydb.commit()
                messages.success(request, 'Profile updated successfully!')
                request.session['name'] = name
                request.session['contact'] = contact
                request.session['email'] = email
                return redirect('user_profile')
            except mysql.connector.Error as err:
                msg = f"Database error: {err}"

        return render(request, 'edit_profile.html', {
            'name': request.session['name'],
            'email': request.session['email'],
            'msg': msg
        })
    messages.warning(request, 'Please log in first!')
    return redirect('user_login')