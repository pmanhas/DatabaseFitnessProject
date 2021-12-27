from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import yaml

# Create Flask object
app = Flask(__name__)

# Configure database
db = yaml.load(open("db_config.yaml"))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

# Connect to MySql server on this computer with our Flask app
mysql = MySQL(app)

# For checking a user's session
logged_in = False

# From here on, different URLs are handled
@app.route('/')
def home_page():
    return render_template('home_page.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    # In the HTML page rendered by this function in the last line, the submit
    # button in the form element was pressed...
    if request.method == "POST":

        # Grab all the data from the input type elements (input fields) and
        # put it in a dictionary
        user_details = request.form

        # Store the individual pieces of data into variables
        username = user_details['username']
        password = user_details['password']
        weight = user_details['weight']
        height = user_details['height']
        age = user_details['age']
        gender = user_details['gender']

        vals = (username, password, int(weight), int(height), int(age), gender)

        # Get a cursor object for the database
        cursor = mysql.connection.cursor()

        # Insert the new user into the database
        cursor.execute("INSERT INTO person(username, password, weight, \
                        height, age, gender) VALUES(%s,%s,%s,%s,%s,%s)", vals)

        # Save and close the cursor
        mysql.connection.commit()
        cursor.close()

        # Redirect to another URL
        return redirect('/sign_up_success')

    return render_template('sign_up.html')

@app.route('/sign_up_success')
def sign_up_success():
    return render_template('sign_up_success.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == "POST":

        user_details = request.form

        username = user_details['username']
        password = user_details['password']

        cursor = mysql.connection.cursor()
        ret = cursor.execute("SELECT password FROM person \
                              WHERE username = %s", [username])
        # ret is the number of tuples returned by the query

        # This username exists, proceed to validate password
        if ret == 1:
            # fetchall() on a cursor will return a list containing all the
            # rows returned by the query that the cursor just executed;
            # so a list of tuples
            valid_password = cursor.fetchall()[0][0]
            cursor.close()
            if password == valid_password:
                global logged_in
                logged_in = True
                # User can now log in, redirected to the dashboard
                # WITH a piece of information from this page (ie. username)
                # *VERY IMPORTANT: username can be used to extract information
                # (from the database) specific to the user that is logged in
                return redirect(url_for('dashboard', username=username))
            else:
                return redirect('/incorrect_password')
        # No tuple in the Person table has this username
        else:
            return redirect('/incorrect_user')

    return render_template('sign_in.html')

@app.route('/incorrect_user', methods=['GET', 'POST'])
def incorrect_user():
    return render_template('sign_in_user_not_found.html')

@app.route('/incorrect_password', methods=['GET', 'POST'])
def incorrect_password():
    return render_template('sign_in_incorrect_password.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global logged_in
    if logged_in == False:
        return redirect('/')

    # *This URL should only be accessed via the redirect from the Sign In page
    # Extract the username of the user that is logged in, from the Sign In page
    username = request.args['username']
    # From here on, 'username' will be passed in to other URLS (such as
    # ones for Goals, Exercises, Programs, Meals, and My Profile) via
    # redirects, like
    # return redirect(url_for('dashboard', username=username))

    # If a submit button was pressed in the HTML...
    if request.method == 'POST':

        # Check which one was pressed, by their names, then redirect to
        # the appropriate URL with 'username' for further information
        # inputs into the database, or further information extraction
        # from the database

        if 'goals' in request.form:
            return redirect(url_for('goal', username=username))

        elif 'exercises' in request.form:
            return redirect(url_for('exercise', username=username))

        elif 'programs' in request.form:
            return redirect(url_for('program', username=username))

        elif 'meals' in request.form:
            return redirect(url_for('meals', username=username))

        elif 'my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))

        elif 'log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('dashboard.html', username=username)

# MY PROFILE
#=====================================================================================================

@app.route('/dashboard/my_profile', methods=['GET', 'POST'])
def my_profile():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Person WHERE username = %s", [username])
    user_details = cursor.fetchall()[0]
    cursor.close()

    if request.method == 'POST':

        if 'back' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'save' in request.form:
            new_user_details = request.form

            new_password = new_user_details['password']
            new_age = new_user_details['age']
            new_weight = new_user_details['weight']
            new_height = new_user_details['height']
            new_gender = new_user_details['gender']

            vals = (new_password, new_age, new_weight,
                        new_height, new_gender, username)

            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Person \
                            SET password = %s, age = %s, weight = %s, \
                                height = %s, gender = %s \
                            WHERE username = %s", vals)
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('dashboard', username=username))

        elif 'delete_acc' in request.form:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Person WHERE username = %s", [username])
            mysql.connection.commit()
            cursor.close()

            return redirect('/')

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('my_profile.html', username=username,
                                              user_details=user_details)

# MEALS
#=====================================================================================================

@app.route('/dashboard/meals', methods=['GET', 'POST'])
def meals():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    if request.method == 'POST':

        if 'back' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'add_meals' in request.form:
            return redirect(url_for('add_meal_date', username=username))
        elif 'view_meals' in request.form:
            return redirect(url_for('view_meals', username=username))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('meals.html', username=username)

@app.route('/dashboard/meals/view_meals', methods=['GET', 'POST'])
def view_meals():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'select_date' in request.form:
            selected_date = (request.form)['selected_date']
            return redirect(url_for('view_meals_results', username=username,
                                                 selected_date=selected_date))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_meals.html', username=username)

@app.route('/dashboard/meals/view_meals_results', methods=['GET', 'POST'])
def view_meals_results():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    selected_date = request.args['selected_date']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    id = cursor.fetchall()[0][0]
    cursor.execute("CREATE VIEW MealsWithCal AS \
                    SELECT M.meal_name, M.calories \
                    FROM Meal M, Eats E \
                    WHERE M.meal_name = E.meal_name \
                    AND E.id = %s AND E.date = %s", [id, selected_date])
    mysql.connection.commit()
    cursor.execute("SELECT * FROM MealsWithCal")
    meals_with_cal = cursor.fetchall()
    cursor.execute("SELECT SUM(calories) FROM MealsWithCal")
    total_cal = cursor.fetchall()[0][0]
    cursor.execute("DROP VIEW MealsWithCal")
    mysql.connection.commit()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'select_date' in request.form:
            selected_date = (request.form)['selected_date']
            return redirect(url_for('view_meals_results', username=username,
                                                 selected_date=selected_date))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_meals_results.html', username=username,
                                                 selected_date=selected_date,
                                                         meals=meals_with_cal,
                                                     total_cal=total_cal)

@app.route('/dashboard/meals/add_meal_date', methods=['GET', 'POST'])
def add_meal_date():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'select_date' in request.form:
            selected_date = (request.form)['selected_date']
            return redirect(url_for('add_meals', username=username,
                                                 selected_date=selected_date))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('add_meal_date.html', username=username)

@app.route('/dashboard/meals/add_meals', methods=['GET', 'POST'])
def add_meals():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    selected_date = request.args['selected_date']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Meal")
    meal_options = cursor.fetchall()
    cursor.execute("SELECT * FROM Veggie")
    veg_options = cursor.fetchall()
    cursor.execute("SELECT * FROM Pescatarian")
    pes_options = cursor.fetchall()
    cursor.execute("SELECT * FROM Omnivore")
    omni_options = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('add_meal_date', username=username))
        elif 'add_meal' in request.form:
            selected_meal = (request.form)['selected_meal']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
            id = cursor.fetchall()[0][0]

            ret = cursor.execute("SELECT * FROM Eats WHERE meal_name = %s AND \
                            id = %s AND date = %s", [selected_meal, id, selected_date])
            cursor.close()

            if ret == 1:
                return redirect(url_for('dup_meal_error', username=username,
                                                     selected_date=selected_date))

            else:
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO Eats(meal_name, id, date) \
                                VALUES(%s,%s,%s)", [selected_meal, id, selected_date])
                mysql.connection.commit()
                cursor.close()

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('add_meals.html', username=username,
                                             selected_date=selected_date,
                                             meal_options=meal_options,
                                             veg_options=veg_options,
                                             pes_options=pes_options,
                                             omni_options=omni_options)

@app.route('/dashboard/meals/add_meals/dup_meal_error', methods=['GET', 'POST'])
def dup_meal_error():
    username = request.args['username']
    selected_date = request.args['selected_date']
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('add_meals', username=username,
                                            selected_date=selected_date))
    return render_template('dup_meal_error.html')

# PROGRAMS
#=====================================================================================================
@app.route('/dashboard/program', methods=['GET', 'POST'])
def program():
    global logged_in
    if logged_in == False:
        return redirect('/')

    # Extract the username of the user that is logged in
    username = request.args['username']

    # If a submit button was pressed in the HTML...
    if request.method == 'POST':

        if 'back' in request.form:
            return redirect(url_for('dashboard', username=username))

        elif 'add_program' in request.form:
            return redirect(url_for('add_program', username=username))

        elif 'remove_program' in request.form:
            return redirect(url_for('remove_program', username=username))

        elif 'view_program' in request.form:
            return redirect(url_for('view_program', username=username))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('program.html', username=username)

@app.route('/dashboard/program/add_program', methods=['GET', 'POST'])
def add_program():
    global logged_in
    if logged_in == False:
        return redirect('/')

    # Extract the username of the user that is logged in, from the Sign In page
    username = request.args['username']

    # If a submit button was pressed in the HTML...
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('program', username=username))
        elif 'add_program' in request.form:
            # Grab all the data from the input type elements (input fields) and
            # put it in a dictionary
            user_details = request.form

            # Get a cursor object for the database
            cursor = mysql.connection.cursor()

            # Store the individual pieces of data into variables
            program_name = user_details['program_name']
            start_date = user_details['start_date']
            cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
            userid = cursor.fetchall()[0][0]

            vals = (userid, program_name, start_date)

            # Insert the new record into the database
            cursor.execute("INSERT INTO Uses(id, program_name, start_date) VALUES(%s,%s,%s)", vals)

            # Save and close the cursor
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('program', username=username))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('add_program.html', username=username)

@app.route('/dashboard/program/remove_program', methods=['GET', 'POST'])
def remove_program():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    userid = cursor.fetchall()[0][0]

    cursor.execute("SELECT program_name FROM Uses WHERE id = %s", [userid])
    program_options = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('program', username=username))
        elif 'remove' in request.form:
            selected_program = (request.form)['selected_program']
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Uses WHERE program_name = %s \
                                             AND id = %s",
                                             [selected_program, userid])
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('program', username=username))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('remove_program.html', username=username,
                                                    program_options=program_options)

@app.route('/dashboard/program/view_program', methods=['GET', 'POST'])
def view_program():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    userid = cursor.fetchall()[0][0]

    cursor.execute("SELECT program_name FROM Uses WHERE id = %s", [userid])
    program_options = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('program', username=username))
        elif 'view' in request.form:
            selected_program = (request.form)['selected_program']
            return redirect(url_for('view_details', username=username,
                                                program_name=selected_program))

        # Navigation bar
        elif 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_program.html', username=username,
                                                    program_options=program_options)

@app.route('/dashboard/program/view_program/view_details', methods=['GET', 'POST'])
def view_details():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    programname = request.args['program_name']

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    userid = cursor.fetchall()[0][0]

    cursor.execute("SELECT * FROM Program WHERE program_name = %s", [programname])
    program_info = cursor.fetchall()

    cursor.execute("SELECT exercise_name, sets, repetitions FROM Contains WHERE program_name = %s", [programname])
    exercises = cursor.fetchall()

    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('program', username=username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_details.html', username=username, program_info=program_info, exercises=exercises)

# EXERCISES
#=====================================================================================================
@app.route('/dashboard/exercises', methods=['GET', 'POST'])
def exercise():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    cursor = mysql.connection.cursor()

    # get id of person
    cursor.execute("SELECT id FROM PERSON WHERE username = %s", [username])
    posts = cursor.fetchall()
    id = posts[0]
    #get all possible exercises
    cursor.execute("SELECT * FROM EXERCISE")
    posts = cursor.fetchall()
    posts =[i[0] for i in posts]
    cursor.close()

    # If a submit button was pressed in the HTML...
    if request.method == 'POST':
        if 'log' in request.form:
                return redirect(url_for('log', username=username, id = id))
        for i in posts:
            if i in request.form:
                return redirect(url_for('perform_exercise', username=username,
                                                    exerciseName = i, id = id))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('exercise.html',username=username, posts= posts, id = id)

@app.route('/dashboard/exercises/perform_exercise', methods=['GET', 'POST'])
def perform_exercise():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    exerciseName = request.args['exerciseName']
    id = request.args['id']
    if request.method == "POST":
        if 'submitPerformance' in request.form:
            # Grab all the data from the input type elements (input fields) and
            # put it in a dictionary
            perform_details = request.form

            # Store the individual pieces of data into variables
            repetitions = perform_details['repetitions']
            date = perform_details['date']

            #create tuple
            vals = (id, exerciseName, date,  repetitions)

            # Get a cursor object for the database
            cursor = mysql.connection.cursor()
            ret = cursor.execute("SELECT * FROM PERFORMS \
                                WHERE id = %s AND exercise_name = %s AND date = %s ", [id, exerciseName, date])
            # ret is the number of tuples returned by the query
            # This user has already done this exercise today

            if ret > 0:
                return redirect(url_for('exercise', username=username))

            # Insert the new perform tuple into the database
            cursor.execute("INSERT INTO PERFORMS(id, exercise_name, date, \
                            repetitions) VALUES(%s,%s,%s,%s)", vals)

            # Save and close the cursor
            mysql.connection.commit()
            cursor.close()

            # Redirect to another URL
            return redirect(url_for('exercise', username=username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('perform_exercise.html',exerciseName = exerciseName, username=username,id = id )


@app.route('/dashboard/exercises/log',methods=['GET', 'POST'])
def log():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    id = request.args['id']
    # Get a cursor object for the database
    cursor = mysql.connection.cursor()

    # get id of person
    cursor.execute("SELECT repetitions, exercise_name, date FROM PERFORMS WHERE id = %s", id)
    posts = cursor.fetchall()
    #close the cursor
    cursor.close()

    # If a submit button was pressed in the HTML...
    if request.method == 'POST':
        if 'countBtn' in request.form:
            return redirect(url_for('totalCount', username = username, id=id))

        elif 'divisionBtn' in request.form:
            # Grab all the data from the input type elements (input fields) and
            # put it in a dictionary
            division_details = request.form
            # Store the individual pieces of data into variables
            date = division_details['date']

            cursor = mysql.connection.cursor()
            #drop old view so new one can be created
            cursor.execute("DROP VIEW IF EXISTS logTable")
            mysql.connection.commit()
            #Create View so we can perform division query
            cursor.execute("CREATE OR REPLACE VIEW logTable(repetitions, exercise_name, date) \
                            AS SELECT repetitions, exercise_name, date \
                            FROM PERFORMS \
                            WHERE id = %s", id)
            #save changes and close cursor
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('division', username=username, id=id, date = date))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('log.html',username=username, id = id,posts = posts)

@app.route('/dashboard/exercises/division',methods=['GET', 'POST'])
def division():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    id = request.args['id']
    date = request.args['date']
    # Get a cursor object for the database
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT repetitions, exercise_name \
    FROM logTable\
    WHERE date in \
    (SELECT date\
    FROM performs\
    WHERE id = %s AND date = %s)", [id, date])
    posts = cursor.fetchall()

    if request.method == 'POST':
        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('division.html', username=username, id = id,
                                                date = date, posts = posts)

@app.route('/dashboard/exercises/totalCount', methods=['GET', 'POST'])
def totalCount():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    id = request.args['id']

    # Get a cursor object for the database
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT exercise_name, COUNT(*) \
                    FROM PERFORMS \
                    WHERE id = %s \
                    GROUP BY exercise_name", [id])
    posts = cursor.fetchall()

    if request.method == 'POST':
        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('totalCount.html', username=username, id = id,
                                                              posts = posts)

# GOALS
#=====================================================================================================
@app.route('/dashboard/goals', methods=['GET', 'POST'])
def goal():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'update_goals' in request.form:
            return redirect(url_for('update_goals', username=username))
        elif 'add_goal' in request.form:
            return redirect(url_for('add_goal', username=username))
        elif 'view_goals' in request.form:
            return redirect(url_for('view_goals', username=username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('goal.html', username=username)

@app.route('/dashboard/goal/view_goals', methods=['GET', 'POST'])
def view_goals():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'select_goal_type' in request.form:
            selected_goal_achievement = (request.form)['selected_goal_achievement']
            return redirect(url_for('view_goals_results', username=username,
                           selected_goal_achievement=selected_goal_achievement))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_goals.html', username=username)

@app.route('/dashboard/goal/view_goals_results', methods=['GET', 'POST'])
def view_goals_results():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    # print(request.form)
    selected_goal_achievement = request.args['selected_goal_achievement']
    # print(selected_goal_achievement)
    cursor = mysql.connection.cursor()
    # Get the user's id
    cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    id = cursor.fetchall()[0][0]
    # If the user selects unachieved goals from the dropdown menu display all unachieved goals
    if 'Unachieved Goals' in selected_goal_achievement:
        cursor.execute("SELECT * FROM Goal WHERE id = %s AND goal_achieved = %s \
                        ORDER BY goal_number",[id, "False"])
    else:
        cursor.execute("SELECT * FROM Goal WHERE id = %s AND goal_achieved = %s \
                        ORDER BY goal_number",[id, "True"])

    goals_with_achievement = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('view_goals', username=username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('view_goals_results.html', username=username,
                        selected_goal_achievement=selected_goal_achievement,
                            goals_with_achievement = goals_with_achievement)

@app.route('/dashboard/goal/update_goals', methods=['GET', 'POST'])
def update_goals():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    cursor = mysql.connection.cursor()
    ret = cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
    user_id = cursor.fetchall()[0][0]
    cursor.execute("SELECT goal_number, target_weight, time_frame, goal_achieved \
                    FROM Goal WHERE id = %s", [user_id])
    display_goals = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('goal', username=username))
        elif "update_goals" in request.form:

            update_details = request.form

            goal_num = update_details['goal_number']

            cursor = mysql.connection.cursor()
            # Execute Query to make sure the Goal Number entered exists in DB
            ret = cursor.execute("SELECT goal_number From goal \
                                  WHERE goal_number = %s \
                                  AND id = %s", [goal_num, user_id])
            if ret == 1:
                # Execute an Update Query to change the corresponding
                # goal_achoeved attributes to True.
                cursor.execute("UPDATE goal SET goal_achieved = %s \
                                WHERE goal_number = %s \
                                AND id = %s",  ["True", goal_num, user_id] )
            else:
                return 'Goal Does not Exist: Try Again'

            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('update_set', username = username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('add_update.html', display_goals = display_goals)

@app.route('/dashboard/goal/update_set', methods = ['GET','POST'])
def update_set():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    # Check if the submit button was pressed
    if request.method == "POST":
        if "return_to_goal" in request.form:
            return redirect(url_for('goal', username = username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('update_set.html')


@app.route('/dashboard/goal/add_goal', methods = ['GET','POST'])
def add_goal():
    global logged_in
    if logged_in == False:
        return redirect('/')

      # In the HTML page rendered by this function in the last line, the submit
    # button in the form element was pressed...
    username = request.args['username']
    if request.method == 'POST':
        if 'back' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'set_goal' in request.form:
            # Grab all the data from the input type elements (input fields) and
            # put it in a dictionary
            update_details = request.form

            # Get a cursor object for the database
            cursor = mysql.connection.cursor()
            target_weight = update_details['target_weight']
            time_frame = update_details['time_frame']
            ret = cursor.execute("SELECT id FROM Person WHERE username = %s", [username])
            user_id = cursor.fetchall()[0][0]
            vals = (user_id,int(target_weight), int(time_frame), 'False')

            # Insert the new goal into the database
            cursor.execute("INSERT INTO goal(id,target_weight, time_frame, goal_achieved\
                            ) VALUES(%s,%s,%s,%s)", vals)
            # Save and close the cursor
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('goal_set', username = username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('add_goal.html')

@app.route('/dashboard/goal/add_goal/goal_set', methods=['GET', 'POST'])
def goal_set():
    global logged_in
    if logged_in == False:
        return redirect('/')

    username = request.args['username']
    # Check if the submit button was pressed
    if request.method == "POST":
        if "return_to_goal" in request.form:
            return redirect(url_for('goal', username = username))

        # Navigation bar
        if 'nav_dashboard' in request.form:
            return redirect(url_for('dashboard', username=username))
        elif 'nav_goals' in request.form:
            return redirect(url_for('goal', username=username))
        elif 'nav_exercises' in request.form:
            return redirect(url_for('exercise', username=username))
        elif 'nav_programs' in request.form:
            return redirect(url_for('program', username=username))
        elif 'nav_meals' in request.form:
            return redirect(url_for('meals', username=username))
        elif 'nav_my_profile' in request.form:
            return redirect(url_for('my_profile', username=username))
        elif 'nav_log_out' in request.form:
            logged_in = False
            return redirect('/')

    return render_template('goal_set.html')

#=====================================================================================================

if __name__ == '__main__':
    app.debug = True
    app.run()
    #app.run(host = '0.0.0.0', port = 5000)
