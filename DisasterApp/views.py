from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from random import randint
import os
import hashlib
from django.conf import settings
from django.db import connection as mydb
from django.conf import settings


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
    return render(request,'user_dashboard.html')

def admin_login(request):
    return render(request, 'admin_login.html')