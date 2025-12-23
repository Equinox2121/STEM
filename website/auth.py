from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Misc
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   # Importing the database, so we can add users 
from flask_login import login_user, login_required, logout_user, current_user
from datetime import timedelta, datetime
import random
import string
import os

# Function to count capitalized, lowercase, numbers, and symbols in string (for password requirments)
def string_test(password):
    symbol_list = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "\\", "-", "=", "[", "]", "{", "}", ";", "'", ":", "|", ",", ".", "<", ">", "/", "?"]
    capital_counter = 0
    lowercase_counter = 0
    num_and_symbol_counter = 0
    for letter in password:
        if letter.isupper():
            capital_counter+=1
        elif letter.islower():
            lowercase_counter+=1
        elif any(char in letter for char in symbol_list):
            num_and_symbol_counter+=1
        elif (str(letter)).isnumeric():
            num_and_symbol_counter+=1
        else:
            pass
    counters = [capital_counter, lowercase_counter, num_and_symbol_counter]
    return counters

# Function to check for errors in the first name
def first_name_errors(first_name):
    # Check to see if there is anything in the input box
    if first_name == '':
        error_msg = 'Enter a first name.'
    # Check to see if the name is too short
    elif len(str(first_name)) < 2:
        error_msg = 'First name is too short.'
    # Check to see if the first name has digits
    elif any(x.isdigit() for x in first_name):
        error_msg = 'First name cannot contain numbers.'
    # Check to see if the first name contians anything other than letters
    elif (first_name.replace(' ','')).isalpha() == False:
        error_msg = 'First name can only contain letters.'
    # The name contains less than 1 different letters (name could be JJ)
    elif len(set(first_name)) < 1:
        error_msg = 'Enter a valid first name.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the last name
def last_name_errors(last_name):
    # Check to see if there is anything in the input box
    if last_name == '':
        error_msg = 'Enter a last name.'
    # Check to see if the last name is too short
    elif len(str(last_name)) < 2:
        error_msg = 'Last name is too short.'
    # Check to see if the first name has digits
    elif any(x.isdigit() for x in last_name):
        error_msg = 'Last name cannot contain numbers.'
    # Check to see if the first name contians anything other than letters
    elif last_name.isalpha() == False:
        error_msg = 'Last name can only contain letters.'
    # The name contains less than 2 different letters
    elif len(set(last_name)) < 2:
        error_msg = 'Enter a valid last name.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the graduation year
def graduation_year_errors(graduation_year):
    # Check to see if there is anything in the input box
    if graduation_year == '':
        error_msg = 'Enter a graduation year.'
    # Check to see if the graduation year is 4 characters
    elif len(str(graduation_year)) < 4:
        error_msg = 'Enter a valid graduation year.'
    # The graduation year contains something other than numbers
    elif (str(graduation_year)).isnumeric() == False:
        error_msg = 'Graduation year can only contain numbers.'
    # Check to see if the graduation year is above the year 2100
    elif int(graduation_year) > 2100:
        error_msg = 'Enter a valid graduation year.'
    # Check to see if the graduation year is below the year 2024
    elif int(graduation_year) < os.getenv("GRADUATION_YEAR_MINIMUM"):
        error_msg = 'Enter a valid graduation year.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the student phone number
def student_phone_errors(student_phone):
    # Check to see if there is anything in the input box
    if student_phone == '':
        error_msg = 'Enter a student phone number.'
    # Check to see if the student phone number is below maximum # length
    elif len(str(student_phone)) >= 11:
        error_msg = 'Student phone number is too long.'
    # Check to see if the student phone number is too small
    elif len(str(student_phone)) <= 9:
        error_msg = 'Student phone number is too short.'
    # The phone number contains something other than numbers
    elif (str(student_phone)).isnumeric() == False:
        error_msg = 'Enter a valid student phone number.'
    # The phone number contains to many of the same numbers
    elif len(set(student_phone)) < 2:
        error_msg = 'Enter a valid student phone number.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the parent email
def parent_email_errors(parent_email):
    # Check to see if there is anything in the input box
    if parent_email == '':
        error_msg = 'Enter a parent email.'
    # Check to see if the parent email is below a maximum length
    elif len(str(parent_email)) < 5:
        error_msg = 'Parent email is too short.'
    # Check to see if there is a . near the end of the email (Last 4 digits)
    elif "." not in (parent_email[-4:]):
        error_msg = 'Parent email is invalid.'
    # Check to see if there is a . near the end of the email (Last 2 digits)
    elif "." in (parent_email[-2:]):
        error_msg = 'Parent email is invalid.'
    # Check to see if all the last 3 characters are letters (remove the period first)
    elif ((parent_email[-4:]).replace(".","")).isalpha() == False:
        error_msg = 'Parent email is invalid.'
    # Check to see if its a valid email
    elif '@' not in str(parent_email):
        error_msg = 'Parent email is invalid.'
    # Make sure @ doesn't appear twice
    elif str(parent_email).count("@") > 1:
        error_msg = 'Parent email is invalid.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the parent phone number
def parent_phone_errors(parent_phone):
    # Check to see if there is anything in the input box
    if parent_phone == '':
        error_msg = "Enter a parent's phone number."
    # Check to see if the parent phone number is below maximum # length
    elif len(str(parent_phone)) >= 11:
        error_msg = 'Parent phone number is too long.'
    # Check to see if the parent phone number is too small
    elif len(str(parent_phone)) <= 9:
        error_msg = 'Parent phone number is too short.'
    # The phone number contains something other than numbers
    elif (str(parent_phone)).isnumeric() == False:
        error_msg = 'Enter a valid parent phone number.'
    # The phone number contains to many of the same numbers
    elif len(set(parent_phone)) < 2:
        error_msg = 'Enter a valid parent phone number.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the student email
def student_email_errors(student_email):
    # Check to see if there is anything in the input box
    if student_email == '':
        error_msg = 'Enter a student email.'
    # Student email is too short
    elif len(str(student_email)) < 20:
        error_msg = 'Student email is too short.'
    # Doesnt have an @
    elif '@' not in str(student_email):
        error_msg = 'Student email is invalid.'
    # Check to see if its a school email
    elif os.getenv("SCHOOL_DOMAIN") not in str(student_email.lower()):
        error_msg = 'Student email has the wrong domain.'
    # Check to see if the shcool domain is at the end of the input
    elif (student_email.lower()).endswith(os.getenv("SCHOOL_DOMAIN")) == False:
        error_msg = 'Student email is invalid.'
    # Make sure @ doesn't appear twice
    elif str(student_email).count("@") > 1:
        error_msg = 'Student email is invalid.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Function to check for errors in the password
def password_errors(password1, password2):
    password_counter = string_test(password1) # Call the function to count capital, lowercase, numbers, symbols
    # Check to see if there is anything in the input box
    if password1 == '' or password2 == '':
        error_msg = 'Fill out both password fields.'
    # Password must be atleast 7 characters
    elif len(str(password1)) <= 7:
        error_msg = 'Password must be at least 8 characters.'
    # Passwords have to match to work
    elif password1 != password2:
        error_msg = 'Passwords do not match.'
    # Password must have capitals, lowercase, symbols/numbers
    elif password_counter[0] < 1 or password_counter[1] < 1 or password_counter[2] < 1:
        error_msg = 'Password must contain capital, lowercase, and a numeric or symbol character.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Define auth
auth = Blueprint('auth', __name__)

# Login page (Add /login to end of basic URL)
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    logout_user() # Log user out if they access this page

    # Compare sumbitted information with database to login
    if request.method == 'POST':
        # Get the information from the input boxes
        student_email = (request.form.get('email').lower())
        password = request.form.get('password')

        # Search for the person in the database by their student email
        user = User.query.filter_by(student_email = student_email).first()
        if user:
            if check_password_hash(user.password, password): # Hash the inputted password and compare the two
                #flash('Logged in successfully!', category = 'success')
                login_user(user, remember = False) # FALSE (Remembers user for quick login/stay logged in)
                print(f'{current_user.first_name} has successfully logged in.')

                # Updating Misc Informaion DB
                for misc in current_user.user_data:
                    # Add 1 to the login count in Misc DB
                    login_count = misc.account_login_count
                    login_count += 1
                    misc.account_login_count = login_count

                    # Update the most recent login date
                    now = datetime.now() # Get the current time
                    current_time = now.strftime("%m-%d-%Y %H:%M:%S")
                    misc.most_recent_login = current_time

                    # Save changes
                    db.session.commit()
                return redirect(url_for('views.home')) # Redirect to (file name and function)
            
            # Nothing was inputted into the password field
            elif password == '':
                error_msg = 'Enter a password.'
                flash(error_msg, category = 'error')
                print(error_msg)
            # The password was incorrect (but don't fully reveal that)
            else:
                error_msg = 'Information incorrect.'
                flash(error_msg, category = 'error')
                print(error_msg)

        # Nothing was inputetd into the student email field
        elif student_email == '':
            error_msg = 'Enter an email.'
            flash(error_msg, category = 'error')
            print(error_msg)
        # No account exists with the email they inputted
        else:
            error_msg = 'Information incorrect.'
            flash(error_msg, category = 'error')
            print(error_msg)

    return render_template('login.html', user = current_user)


# Logout page (Add /logout to end of basic URL)
@auth.route('/logout')
@login_required # Can't access this page without being logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login')) # Redirect to (file name and function)


# Create Account Page 1 (Add /register to end of basic URL). GET = pulling from website, POST = posting to website
@auth.route('/register', methods = ['GET', 'POST'])
def register():
    logout_user() # Log user out if they access this page

    # Set the cached inputs to nothing until otherwise changed
    cached_first_name = ''
    cached_last_name = ''
    cached_graduation_year = ''
    cached_student_phone = ''
    cached_parent_email = ''
    cached_parent_phone = ''
    cached_student_email = ''
    cached_password1 = ''
    cached_password2 = ''

    # When a user submits information, check parameters before commiting to database
    if request.method == 'POST':
        # Get all the inputs to be run through the error checks
        first_name = (request.form.get('firstName')).lower()
        last_name = (request.form.get('lastName')).lower()
        graduation_year = request.form.get('graduationYear')
        student_phone = request.form.get('studentPhoneNumber')
        parent_email = (request.form.get('parentEmail')).lower()
        parent_phone = request.form.get('parentPhoneNumber')
        student_email = (request.form.get('studentEmail')).lower()
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Save all the raw information to be passed back and filled in
        cached_first_name = request.form.get('firstName')
        cached_last_name = request.form.get('lastName')
        cached_graduation_year = request.form.get('graduationYear')
        cached_student_phone = request.form.get('studentPhoneNumber')
        cached_parent_email = request.form.get('parentEmail')
        cached_parent_phone = request.form.get('parentPhoneNumber')
        cached_student_email = request.form.get('studentEmail')
        cached_password1 = request.form.get('password1')
        cached_password2 = request.form.get('password2')

        user = User.query.filter_by(student_email = student_email).first()
        # Search for the person in the database (by school email)
        if user:
            error_msg = 'Account already exists with this email.'
            flash(error_msg, category = 'error')
            flash("Wrapper Active", category = 'Active') # Second page of registering (active wrapper)
            print(error_msg)

        # Check the first name to make sure it meets the requirements
        elif first_name_errors(first_name) != "no errors found":
            error_msg = first_name_errors(first_name)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the last name to make sure it meets the requirements
        elif last_name_errors(last_name) != "no errors found":
            error_msg = last_name_errors(last_name)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the graduation year to make sure it meets the requirements
        elif graduation_year_errors(graduation_year) != "no errors found":
            error_msg = graduation_year_errors(graduation_year)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the student phone number to make sure it meets the requirements
        elif student_phone_errors(student_phone) != "no errors found":
            error_msg = student_phone_errors(student_phone)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the parent email to make sure it meets the requirements
        elif parent_email_errors(parent_email) != "no errors found":
            error_msg = parent_email_errors(parent_email)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the parent phone number to make sure it meets the requirements
        elif parent_phone_errors(parent_phone) != "no errors found":
            error_msg = parent_phone_errors(parent_phone)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

        # Check the student email to make sure it meets the requirements
        elif student_email_errors(student_email) != "no errors found":
            error_msg = student_email_errors(student_email)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Active", category = 'Active') # Second page of registering (active wrapper)

        # Check the passwords to make sure it meets the requirements
        elif password_errors(password1, password2) != "no errors found":
            error_msg = password_errors(password1, password2)
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Active", category = 'Active') # Second page of registering (active wrapper)

        # No errors, so create the account
        else:
            new_user = User(first_name = first_name, last_name = last_name, graduation_year = graduation_year, student_phone = student_phone, parent_email = parent_email, parent_phone = parent_phone, student_email = student_email, password = generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember = False) # FALSE (Won't remember user for quick login/stay logged in)
            # Success message
            success_msg = 'Account Created!'
            #flash(success_msg, category = 'success')
            print(f'{success_msg} User: {current_user.first_name}')
            
            # Get the current time
            now = datetime.now()
            current_time = now.strftime("%m-%d-%Y %H:%M:%S")
            print(current_time)
            # Count how many characters in the password
            password_counter = len(password1)
            password_placeholder = ''.join(random.choices(string.ascii_uppercase + string.digits, k = password_counter))
            # Placeholder used for UI display only (not a real password)
            print(password_placeholder)
            # Add information to the Misc database
            user_data = Misc(account_creation_date = current_time, password_placeholder = password_placeholder, most_recent_login = current_time, account_login_count = 1, program_choice = 'Select one', user_id = current_user.id)
            db.session.add(user_data)
            db.session.commit()
            
            # Redirect to (file name and function)
            return redirect(url_for('views.home')) 
        
    return render_template('register.html', user = current_user, # Return all the cached values to be re-inputted
                           cached_first_name=cached_first_name, cached_last_name=cached_last_name, cached_graduation_year=cached_graduation_year, cached_student_phone=cached_student_phone, cached_parent_email=cached_parent_email,
                           cached_parent_phone=cached_parent_phone, cached_student_email=cached_student_email, cached_password1=cached_password1, cached_password2=cached_password2)


# Account page (Add /account to end of basic URL) - update informaton once logged in
@auth.route('/account', methods = ['GET', 'POST'])
@login_required # Can't access this page without being logged in
def account():
    
    # Get the random password placeholder from the DB and pass it on to html
    for misc in current_user.user_data:
        password_placeholder = misc.password_placeholder

    # Get all the inputs to be run through the error checks
    if request.method == 'POST':
        first_name = (request.form.get('firstName')).lower()
        last_name = (request.form.get('lastName')).lower()
        graduation_year = request.form.get('graduationYear')
        student_phone = request.form.get('studentPhoneNumber')
        parent_email = (request.form.get('parentEmail')).lower()
        parent_phone = request.form.get('parentPhoneNumber')
        # Reset password inputs
        old_password = (request.form.get('password_old'))
        new_password1 = (request.form.get('password1'))
        new_password2 = (request.form.get('password2'))
    
    # CHANGE INFORMATION PAGE
        # Nothing on the reset password page is filled out, so just look at account information page
        if old_password == '' and new_password1 == '' and new_password2 == '':
            # Check the first name to make sure it meets the requirements
            if first_name_errors(first_name) != "no errors found":
                error_msg = first_name_errors(first_name)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # Check the last name to make sure it meets the requirements
            elif last_name_errors(last_name) != "no errors found":
                error_msg = last_name_errors(last_name)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # Check the graduation year to make sure it meets the requirements
            elif graduation_year_errors(graduation_year) != "no errors found":
                error_msg = graduation_year_errors(graduation_year)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # Check the student phone number to make sure it meets the requirements
            elif student_phone_errors(student_phone) != "no errors found":
                error_msg = student_phone_errors(student_phone)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # Check the parent email to make sure it meets the requirements
            elif parent_email_errors(parent_email) != "no errors found":
                error_msg = parent_email_errors(parent_email)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # Check the parent phone number to make sure it meets the requirements
            elif parent_phone_errors(parent_phone) != "no errors found":
                error_msg = parent_phone_errors(parent_phone)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Inactive", category = 'notActive') # First page of registering (inactive wrapper)

            # No errors, so save the account information
            else:
                current_user.first_name = first_name
                current_user.last_name = last_name
                current_user.graduation_year = graduation_year
                current_user.student_phone = student_phone
                current_user.parent_email = parent_email
                current_user.parent_phone = parent_phone
                # Save changes
                db.session.commit()
                success_msg = 'Account Updated!'
                flash(success_msg, category = 'success')
                print(f'{success_msg} User: {current_user.first_name}')
                flash("Wrapper Inactive", category = 'notActive') # Redirect to same page (inactive wrapper)

    # RESET PASSWORD PAGE
        # All 3 inputs on the reset password page have a value
        elif old_password != '' and new_password1 != '' and new_password2 != '':
            # Check to see if they entered their current password correctly
            if check_password_hash(current_user.password, old_password) == False: # Hash the inputted password and compare the two
                error_msg = 'Current password is incorrect.'
                flash(error_msg, category = 'error')
                flash("Wrapper Active", category = 'Active') # Second page, reset password (active wrapper)
                print(error_msg)
            
            # New password is the same as old one
            elif old_password == new_password1:
                error_msg = 'Current password is the same as the new password.'
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Active", category = 'Active') # Second page of registering (active wrapper)

            # Check the new password to make sure it meets the requirements
            elif password_errors(new_password1, new_password2) != "no errors found":
                error_msg = password_errors(new_password1, new_password2)
                flash(error_msg, category = 'error')
                print(error_msg)
                flash("Wrapper Active", category = 'Active') # Second page of registering (active wrapper)

            # No errors, update the password in the database
            else:
                current_user.password = generate_password_hash(new_password1)
                # Save changes
                db.session.commit()
                success_msg = 'Password Updated!'
                flash(success_msg, category = 'success')
                print(f'{success_msg} User: {current_user.first_name}')
                flash("Wrapper Active", category = 'Active') # Second page, reset password (active wrapper)

    # NOTHING HAS CHANGED
        # One or more of the password inputs is empty
        elif old_password == '' or new_password1 == '' or new_password2 == '':
            error_msg = 'To reset the password, all fields must be filled out.'
            flash(error_msg, category = 'error')
            print(error_msg)
            flash("Wrapper Active", category = 'Active') # Second page, reset password (active wrapper)

    return render_template("account.html", user = current_user, password_placeholder = password_placeholder)


# Empty HTML (This is not a feature yet)
@auth.route('/empty')
def empty():
    return "<h1>This is not a feature yet.</h1>"