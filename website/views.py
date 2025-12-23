from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from .models import Table, User, Misc, Report
from . import db
from datetime import timedelta, datetime, timezone
from sqlalchemy import desc, update
from zoneinfo import ZoneInfo

# Count how many hours the user has and calculate how many more they need
def program_hours():
    # Return a total hours variable
    hours = []
    for table in current_user.user_table:
        number = table.hours_earned
        hours.append(number)
    hours_counter = (sum(hours))

    # Calculate how many more hours the user needs
    for misc in current_user.user_data:
        choice = misc.program_choice
    # Get how many hours the user wants
    if choice == "Recognition Level 1":
        number = 100
    elif choice == "Recognition Level 2":
        number = 70
    elif choice == "Recognition Level 3":
        number = 50
    else:
        number = "none"
    # Calculate how many more hours they need
    if number != "none":
        remaining_hours = (int(number) - hours_counter)
        if remaining_hours < 0:
            remaining_hours = 0
    else:
        remaining_hours = ""

    # Remove decimal points if it is a whole number
    if ".0" in str(hours_counter):
        hours_counter = str(hours_counter).replace(".0","")
        remaining_hours = str(remaining_hours).replace(".0","")

    hours_information = [hours_counter, choice, number, remaining_hours]
    return hours_information

# Compare the service date with the current date to confirm it's not in the future or too far in the past
def date_calculatoins(service_date):
    # Make sure the date isn't in the future
    now = datetime.now()
    current_date = now.strftime("%m-%d-%Y")
    # User's graduation year minus x years
    start_point = ((int(current_user.graduation_year))-5)
    # Current date
    current_date_month = int(current_date.split("-")[0])
    current_date_day = int(current_date.split("-")[1])
    current_date_year = int(current_date.split("-")[2])
    # Inputted service date
    service_date_month = int(service_date.split("/")[0])
    service_date_day = int(service_date.split("/")[1])
    service_date_year = int(service_date.split("/")[2])

    # The service date year is after the current date year (future)
    if service_date_year > current_date_year:
        error_msg = 'Date is in the future.'
    # The service month is after current date month, so check the year (future)
    elif service_date_month > current_date_month and service_date_year >= current_date_year:
        error_msg = 'Date is in the future.'
    # The service date is greater than the current date (future)
    elif service_date_day > current_date_day and service_date_month >= current_date_month and service_date_year >= current_date_year:
        error_msg = 'Date is in the future.'
    # The service date year less than 5 years before HS graduation date (past)
    elif service_date_year < start_point:
        error_msg = 'Date is before the allowed participation period.'
    else:
        error_msg = "no errors found"
    return error_msg

def dot_test(hours_earned):
    if (str(hours_earned).split(".", 1)[1]) == "0" or (str(hours_earned).split(".", 1)[1]) == "00" or (str(hours_earned).split(".", 1)[1]) == "25" or (str(hours_earned).split(".", 1)[1]) == "5" or (str(hours_earned).split(".", 1)[1]) == "50" or (str(hours_earned).split(".", 1)[1]) == "75":
        modified_hours_earned = "accepted"
    else:
        modified_hours_earned = "declined"
    return modified_hours_earned

# Make sure the entered service date is a legitimate date at all
def service_date_errors(service_date):
    # Make sure its only numbers (replace the dashes)
    if (str(service_date.replace('/',''))).isnumeric() == False: 
        error_msg = 'Invalid service date.'
    # Check the length of the service date
    elif len(str(service_date)) != 10:
        error_msg = 'Invalid service date.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check the organization name to make sure it meets the requirements
def organization_errors(organization):
    # Make sure there is an input
    if organization == '': 
        error_msg = 'Enter an organization.'
    # Check the length of the organization
    elif len(str(organization)) < 2:
        error_msg = 'Invalid organization.'
    # The organization contains less than 2 different letters
    elif len(set(organization)) < 2:
        error_msg = 'Invalid organization.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check the brief description name to make sure it meets the requirements
def brief_description_errors(brief_description):
    # Make sure there is an input
    if brief_description == '': 
        error_msg = 'Enter a brief description.'
    # Check the length of the description
    elif len(str(brief_description)) < 10:
        error_msg = 'Enter a longer description.'
    # The description contains less than 5 different letters
    elif len(set(brief_description)) < 5:
        error_msg = 'Invalid description.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check the hours earned name to make sure it meets the requirements
def hours_earned_errors(hours_earned, modified_hours_earned):
    # Make sure there is an input
    if hours_earned == '': 
        error_msg = 'Enter the hours earned.'
    # Make sure there is 1 or less periods in the input
    elif (hours_earned.count('.')) > 1:
        error_msg = 'The hours earned is not a numeric value.'
    # Make sure its only numbers in the hours field
    elif (str(hours_earned.replace('.',''))).isnumeric() == False:
        error_msg = 'The hours earned is not a numeric value.'
    # Make sure there is 1 or less periods in the input
    elif modified_hours_earned == "declined":
        error_msg = 'Hours earned should be in full or quarter hour increments (.25, .5, .75).'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check the Contact Person's name/title to make sure it meets the minimum requirements
def contact_person_errors(contact_person):
    # Make sure there is an input
    if contact_person == '': 
        error_msg = 'Enter a name and title of the contact person.'
    # Check the length of the contact person
    elif len(str(contact_person)) < 3:
        error_msg = 'Invalid contact person.'
    # The contact person contains less than 2 different letters
    elif len(set(contact_person)) < 2:
        error_msg = 'Invalid contact person.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check the Contact Person's information to make sure it meets the minimum requirements
def contact_person_info_errors(contacts_info):
    # Make sure there is an input
    if contacts_info == '': 
        error_msg = 'Enter a phone number and/or email for the contact person.'
    # Check the length of the contact's info
    elif len(str(contacts_info)) < 5:
        error_msg = "Contact person's info is invalid."
    # The contact's info contains less than 2 different letters
    elif len(set(contacts_info)) < 2:
        error_msg = "Contact person's info is invalid."
    # Doesn't have a number (for phone number) or @ (for email)
    elif ('@' in str(contacts_info)) == False: 
        if any(char.isdigit() for char in contacts_info) == False:
            error_msg = "Contact person's info doesn't contain a phone number or email"
        else: 
            error_msg = "no errors found"
    elif any(char.isdigit() for char in contacts_info) == False:
        if ('@' in str(contacts_info)) == False: 
            error_msg = "Contact person's info doesn't contain a phone number or email"
        else: 
            error_msg = "no errors found"
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check reflection1 to make sure it meets the minimum requirements
def reflection1_errors(reflection1):
    # Make sure there is an input
    if reflection1 == '': 
        error_msg = 'Explain what you did in the textbox below.'
    # Check the length of the description
    elif len(str(reflection1)) < 16:
        error_msg = 'Enter a longer description for what you did.'
    # The description contains less than 5 different letters
    elif len(set(reflection1)) < 5:
        error_msg = 'Enter a longer description for what you did.'
    else:
        error_msg = "no errors found"
    return(error_msg)

# Check reflection2 to make sure it meets the minimum requirements
def reflection2_errors(reflection2):
    # Make sure there is an input
    if reflection2 == '': 
        error_msg = 'Describe how STEM was applied in your service in the textbox below.'
    # Check the length of the description
    elif len(str(reflection2)) < 16:
        error_msg = 'Enter a longer description for how STEM was applied in your service.'
    # The description contains less than 5 different letters
    elif len(set(reflection2)) < 5:
        error_msg = 'Enter a longer description for how STEM was applied in your service.'
    else:
        error_msg = "no errors found"
    return(error_msg)

views = Blueprint('views', __name__)

# Name of Blueprint and the basic website URL ('/')
@views.route('/')
def base():
    logout_user() # Log user out if they access this page
    return render_template("base.html", user = current_user)


# Home page you first see when you log in
@views.route('/home', methods = ['GET', 'POST'])
@login_required
def home():
    # Pull the first & last name and change capitalization
    first_name = f'{((current_user.first_name).lower()).capitalize()}'
    last_name = f'{((current_user.last_name).lower()).capitalize()}'
    # Get the current time
    now = datetime.now()
    current_time = now.strftime("%m/%d/%Y")
    return render_template("home.html", user = current_user, first_name = first_name, last_name = last_name, current_time = current_time)


# Name of Blueprint and the basic website URL ('/')
@views.route('/service-log', methods = ['GET', 'POST'])
@login_required
def serviceLog():
    # Set the cached inputs to nothing until otherwise changed
    cached_service_date = ''
    cached_organization = ''
    cached_brief_description = ''
    cached_hours_earned = ''

    # Return the user's program choice to html
    for misc in current_user.user_data:
        program_choice = misc.program_choice

    # Pull the first & last name and change capitalization top of page
    first_name = f'{((current_user.first_name).lower()).capitalize()}'
    last_name = f'{((current_user.last_name).lower()).capitalize()}'
    graduation_year = f'{(current_user.graduation_year)}'
    
    # Run the function to get all the information on hours remaining, program choice, etc.
    hours_counter = program_hours()[0]
    choice = program_hours()[1]
    number = program_hours()[2]
    remaining_hours = program_hours()[3]

    # Changes saved at this current time (no saves yet)
    last_save = ""

    # When a user submits information, check parameters before commiting to database
    if request.method == 'POST':
        # Get all the inputs to be run through the error checks
        service_date = request.form.get('serviceDate')
        organization = request.form.get('organization')
        brief_description = request.form.get('briefDescription')
        hours_earned = request.form.get('hoursEarned')

        # Save all the raw information to be passed back and filled in (if an error comes up)
        cached_service_date = request.form.get('serviceDate')
        cached_organization = request.form.get('organization')
        cached_brief_description = request.form.get('briefDescription')
        cached_hours_earned = request.form.get('hoursEarned')

        # Return the user's program choice to html
        for misc in current_user.user_data:
            program_choice = misc.program_choice

        # Update the user's program choice if there is a different selection
        if program_choice != (request.form.get("select_program")) and (request.form.get("select_program")) != "selection":

            for misc in current_user.user_data:
                if (request.form.get("select_program")) != "selection":
                    misc.program_choice = request.form.get("select_program")
                    program_choice = misc.program_choice
                    db.session.commit()

            # Run the function to get all the information on hours remaining, program choice, etc.
            hours_counter = program_hours()[0]
            remaining_hours = program_hours()[3]

            # Changes saved at this current time
            last_save = datetime.now(tz=ZoneInfo("UTC")).strftime("%I:%M %p")
            # Remove leading zero if present
            if last_save[0] == "0":
                last_save = last_save[1:]

        # Change the format on the date (only if it has an input)
        elif service_date != '':
            service_date = (f'{service_date.split("-")[1]}/{service_date.split("-")[2]}/{service_date.split("-")[0]}')

            # Create a modified hours variable to be used in error checks
            if "." in hours_earned:
                modified_hours_earned = dot_test(hours_earned)
            else:
                modified_hours_earned = "ignore"

            # Run checks to make sure the service date is in an acceptable time range (not future or past)
            if date_calculatoins(service_date) != "no errors found":
                error_msg = date_calculatoins(service_date)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the service date to make sure it meets the requirements
            elif service_date_errors(service_date) != "no errors found":
                error_msg = service_date_errors(service_date)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the organization to make sure it meets the requirements 
            elif organization_errors(organization) != "no errors found":
                error_msg = organization_errors(organization)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the brief description to make sure it meets the requirements 
            elif brief_description_errors(brief_description) != "no errors found":
                error_msg = brief_description_errors(brief_description)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the hours earned to make sure it meets the requirements 
            elif hours_earned_errors(hours_earned, modified_hours_earned) != "no errors found":
                error_msg = hours_earned_errors(hours_earned, modified_hours_earned)
                flash(error_msg, category = 'error')
                print(error_msg)

            # No errors, so add the information to the Table
            else:
                # Add information to the Table database
                table_data = Table(service_date = service_date, organization = organization, brief_description = brief_description, hours_earned = hours_earned, user_id = current_user.id)
                db.session.add(table_data)
                db.session.commit()

                tableIDs = []
                # Get the ID of the row that was just created
                for table in current_user.user_table:
                    tableID = table.id
                    tableIDs.append(tableID)
                
                newestID = max(tableIDs)
                # Generate a report form with the same ID (largest number)
                report_form = Report(contact_person = '', contact_person_info = '', reflection1 = '', reflection2 = '', reflection3 = '', table_id = newestID, user_id = current_user.id)
                db.session.add(report_form)
                db.session.commit()

                # Run the function to get all the information on hours remaining, program choice, etc.
                hours_counter = program_hours()[0]
                remaining_hours = program_hours()[3]

                # Changes saved at this current time
                last_save = datetime.now(tz=ZoneInfo("UTC")).strftime("%I:%M %p")
                # Remove leading zero if present
                if last_save[0] == "0":
                    last_save = last_save[1:]

                # Set the cached inputs to nothing, since it was added
                cached_service_date = ''
                cached_organization = ''
                cached_brief_description = ''
                cached_hours_earned = ''

                # Success message
                success_msg = 'Information Added!'
                flash(success_msg, category = 'success')
                print(f'{success_msg} User: {current_user.first_name}')

        # There was no input for the service date, so assume it was the update information
        else: 
            # Find out how many rows there are
            row_count = 0
            for table in current_user.user_table:
                row_count += 1

            # Loop through each row and add the ID to a list
            count = 0
            id_list = []
            while count != row_count:
                for table in reversed(current_user.user_table):
                    id_list.append(table.id)
                    count += 1

            # Loop through all the information by id and update the database
            for x in id_list:
                service_date = request.form.get(f'ShowServiceDate-{str(x)}')
                organization = request.form.get(f'ShowOrganization-{str(x)}')
                brief_description = request.form.get(f'ShowBriefDescription-{str(x)}')
                hours_earned = request.form.get(f'ShowHoursEarned-{str(x)}')
                
                # Create a modified hours variable to be used in error checks
                if "." in hours_earned:
                    modified_hours_earned = dot_test(hours_earned)
                else:
                    modified_hours_earned = "ignore"

                # All the fields are empty, so the user is trying to delete the row
                if service_date == '' or service_date.isspace() == True and organization == '' or organization.isspace() == True and brief_description == '' or brief_description.isspace() == True and hours_earned == '' or hours_earned.isspace() == True:
                    row_ID = Table.query.get(int(x))
                    row_ID.user_id = -1
                    db.session.commit()
                    print(row_ID)
    
                # Run checks to make sure the service date is in an acceptable time range (not future or past)
                elif date_calculatoins(service_date) != "no errors found":
                    error_msg = date_calculatoins(service_date)
                    flash(error_msg, category = 'error')
                    print(error_msg)

                # Check the service date to make sure it meets the requirements
                elif service_date_errors(service_date) != "no errors found":
                    error_msg = service_date_errors(service_date)
                    flash(error_msg, category = 'error')
                    print(error_msg)

                # Check the organization to make sure it meets the requirements 
                elif organization_errors(organization) != "no errors found":
                    error_msg = organization_errors(organization)
                    flash(error_msg, category = 'error')
                    print(error_msg)

                # Check the brief description to make sure it meets the requirements 
                elif brief_description_errors(brief_description) != "no errors found":
                    error_msg = brief_description_errors(brief_description)
                    flash(error_msg, category = 'error')
                    print(error_msg)

                # Check the hours earned to make sure it meets the requirements 
                elif hours_earned_errors(hours_earned, modified_hours_earned) != "no errors found":
                    error_msg = hours_earned_errors(hours_earned, modified_hours_earned)
                    flash(error_msg, category = 'error')
                    print(error_msg)

                # No Errors, so update the database
                else:
                    row_ID = Table.query.get(int(x))
                    row_ID.service_date = service_date
                    row_ID.organization = organization
                    row_ID.brief_description = brief_description
                    row_ID.hours_earned = hours_earned

                    # Save changes to database
                    db.session.commit()

            # Update the user's program choice
            for misc in current_user.user_data:
                if (request.form.get("select_program")) != "selection":
                    misc.program_choice = request.form.get("select_program")
                    program_choice = misc.program_choice
                    db.session.commit()

            # Run the function to get all the information on hours remaining, program choice, etc.
            hours_counter = program_hours()[0]
            remaining_hours = program_hours()[3]

            # Changes saved at this current time
            last_save = datetime.now(tz=ZoneInfo("UTC")).strftime("%I:%M %p")
            # Remove leading zero if present
            if last_save[0] == "0":
                last_save = last_save[1:]

            # Get the value (report form ID number) from which ever button was pressed
            report_button = request.form.get('reportButton')
            # Check to see if it was a Report Form button that was clicked
            # If it was, create a session, so it can be shared over to the report form route and redirect to report form template
            if report_button:
                if 'button' in report_button:
                    report_button = report_button.replace('button-', '') # Leaves just the Number ID
                    session['report_form_button_ID'] = report_button
                    return redirect(url_for('views.reportForm')) # Redirect to (file name and function)

    return render_template("service-log.html", user = current_user, first_name = first_name, last_name = last_name, graduation_year = graduation_year,
                          cached_service_date = cached_service_date, cached_organization = cached_organization, cached_brief_description = cached_brief_description, 
                          cached_hours_earned = cached_hours_earned, reversed_data = reversed(current_user.user_table), current_date = (datetime.now()).strftime("%m/%d/%Y"),
                          hours_counter = hours_counter, program_choice = program_choice, remaining_hours = remaining_hours, last_save = last_save)


# Name of Blueprint and the basic website URL ('/')
@views.route('/report-form', methods = ['GET', 'POST'])
@login_required
def reportForm():

    # Get the ID of the button that was clicked (carried over from service log route)
    reportFormID = session.get('report_form_button_ID', None)

    # A specific number button was pressed
    if reportFormID:
        # Get the information of that ID
        row_ID = Table.query.get(int(reportFormID))
        service_date = row_ID.service_date
        organization = row_ID.organization
        brief_description = row_ID.brief_description
        hours_earned = row_ID.hours_earned

        # Get the information from the report form with that same ID
        row_ID = Report.query.get(int(reportFormID))
        contact_person = row_ID.contact_person
        contacts_info = row_ID.contact_person_info
        upload_description = row_ID.reflection1
        reflection2 = row_ID.reflection2
        reflection3 = row_ID.reflection3

    # They just used the generic report form link, so take them to a page to select a number
    else:
        return redirect(url_for('views.reportFormAlert')) # Redirect to (file name and function)

    # Pull the first & last name and change capitalization top of page
    first_name = f'{((current_user.first_name).lower()).capitalize()}'
    last_name = f'{((current_user.last_name).lower()).capitalize()}'
    graduation_year = f'{(current_user.graduation_year)}'
    # Changes saved at this current time (no saves yet)
    last_save = ''

    # When a user submits information, check parameters before commiting to database
    if request.method == 'POST':

        # Get all the inputs to be run through the error checks
        contact_person = request.form.get('contact')
        contacts_info = request.form.get('contactInfo')
        reflection1 = request.form.get('reflection1')
        reflection2 = request.form.get('reflection2')
        reflection3 = request.form.get('reflection3')
        # Get the value (report form ID number) from which ever button was pressed
        upload_button = request.form.get('uploadButton')

        # Check to see if it was a Upload Info button that was clicked
        if upload_button == 'uploadButton':
            upload_description = brief_description

        # The upload description button was not pressed so save all other fields
        else: 
            upload_description = reflection1

            # Check the name/title of contact person to make sure it meets the requirements 
            if contact_person_errors(contact_person) != "no errors found":
                error_msg = contact_person_errors(contact_person)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the contact person's info to make sure it meets the requirements 
            elif contact_person_info_errors(contacts_info) != "no errors found":
                error_msg = contact_person_info_errors(contacts_info)
                flash(error_msg, category = 'error')
                print(error_msg)
            
            # Check the first reflection box to make sure it meets the requirements 
            elif reflection1_errors(reflection1) != "no errors found":
                error_msg = reflection1_errors(reflection1)
                flash(error_msg, category = 'error')
                print(error_msg)

            # Check the second reflection box to make sure it meets the requirements 
            elif reflection2_errors(reflection2) != "no errors found":
                error_msg = reflection2_errors(reflection2)
                flash(error_msg, category = 'error')
                print(error_msg)
    
            else:
                # Update the Report Form database
                row_ID = Report.query.get(int(reportFormID))
                row_ID.contact_person = contact_person
                row_ID.contact_person_info = contacts_info
                row_ID.reflection1 = reflection1
                row_ID.reflection2 = reflection2
                row_ID.reflection3 = reflection3

                # Save changes
                db.session.commit()
                success_msg = 'Report Form Updated!'
                flash(success_msg, category = 'success')
                print(f'{success_msg} User: {current_user.first_name}')

                # Changes saved at this current time
                last_save = datetime.now(tz=ZoneInfo("UTC")).strftime("%I:%M %p")
                # Remove leading zero if present
                if last_save[0] == "0":
                    last_save = last_save[1:]

    return render_template("report-form.html", user = current_user, first_name = first_name, last_name = last_name, graduation_year = graduation_year, last_save = last_save,
                            service_date = service_date, organization = organization, contact_person = contact_person, contacts_info = contacts_info, reflection1 = upload_description,
                            hours_earned = hours_earned, reflection2 = reflection2, reflection3 = reflection3)


# GO BACK AND MAKE A REDIRECT TO ANOTHER PAGE TELLING THEM TO SELCECT A NUMBER AND INSTRUCTIONS ON DOING SERVICE LOG FIRST
# Name of Blueprint and the basic website URL ('/')
@views.route('/report-form/alert', methods = ['GET', 'POST'])
@login_required
def reportFormAlert():

     # When a user submits information, check parameters before commiting to database
    if request.method == 'POST':

        # Get the inputed ID of the Report Form
        reportFormID = request.form.get('reportFormID')

        # Get the IDs of all the user's service logs
        id_list = []
        for table in current_user.user_table:
            id_list.append(str(table.id))

        Entered_ID = 'null'
        # Compare the Entered ID with the User's list of Report Form IDs
        for ID in id_list:
            if (ID == str(reportFormID)):
                Entered_ID = reportFormID

        # A legitamate ID was entered
        if Entered_ID != "null":
            print(Entered_ID)
            # Send the ID to the Report Form page and load it up
            session['report_form_button_ID'] = Entered_ID
            return redirect(url_for('views.reportForm')) # Redirect to (file name and function)
        else:
            error_msg = "Report Form number does not exist."
            flash(error_msg, category = 'error')
            print(error_msg)
        
    return render_template("report-form-alert.html", user = current_user)