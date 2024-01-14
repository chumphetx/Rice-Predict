from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime  # Import the datetime module
import joblib
from pymysql.cursors import DictCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash
app = Flask(__name__)

# MySQL Database configuration
app.config['MYSQL_HOST'] = 'chumphet.c38qkgc8yhkb.ap-southeast-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'root'  # Replace with your RDS username if different
app.config['MYSQL_PASSWORD'] = '123456789'  # Replace with your RDS password
app.config['MYSQL_DB'] = 'tbl_users'  # Replace with your RDS database name if different
app.secret_key = 'your-secret-key'  # Your secret key

# Initialize MySQL
mysql = MySQL(app)

# Load your pre-trained model
model = joblib.load('random_forest_model.joblib')

# Function to calculate features
def calculate_features(rev, cost, frm, tsk, mrevn, mcost, mplant, costlost, t_cost, alltime, timelost_3, duration):
    r1 = cost / rev if rev > 0 else 0
    r2 = bool(frm)
    r3 = bool(tsk)
    r4 = (mrevn / mcost) * mplant
    r5 = costlost / t_cost if t_cost > 0 else 0
    r6 = alltime / 15 if alltime > 0 else 0
    r7 = timelost_3 / 3 if timelost_3 > 0 else 0
    r8 = duration / 3 if duration > 0 else 0

    r1 = 1 if r1 > 1 else r1
    r4 = 1 if r4 > 1 else r4
    r5 = 1 if r5 > 1 else r5

    return {'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4, 'r5': r5, 'r6': r6, 'r7': r7, 'r8': r8}

# Function to get prediction
def get_prediction(features):
    return model.predict([list(features.values())])

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']  # Capture the username from the form
        email = request.form['email']        # Capture the email from the form
        join_date = datetime.now()           # Use current date and time as join_date
        password = request.form['password']  # Capture the password from the form

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO tbl_users(username, email, join_date, password) VALUES(%s, %s, %s, %s)', 
                       (username, email, join_date,password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("Username from form:", username)  # Debug print
        print("Password from form:", password)  # Debug print
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT username, password FROM tbl_users WHERE username = %s', [username])
        user = cursor.fetchone()
        cursor.close()

        if user and password == user[1]:
            session['username'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html',error ='invalid')
    return render_template('login.html')

# Index route with model prediction
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        rev = float(request.form['rev'])
        cost = float(request.form['cost'])
        frm = float(request.form['frm'])
        tsk = float(request.form['tsk'])
        mrevn = float(request.form['mrevn'])
        mcost = float(request.form['mcost'])
        mplant = float(request.form['mplant'])
        costlost = float(request.form['costlost'])
        t_cost = float(request.form['t_cost'])
        alltime = float(request.form['alltime'])
        timelost_3 = float(request.form['timelost_3'])
        duration = float(request.form['duration'])

        features = calculate_features(rev, cost, frm, tsk, mrevn, mcost, mplant, costlost, t_cost, alltime, timelost_3, duration)
        prediction = get_prediction(features)

        return render_template('index.html', result={'features': features, 'prediction': prediction[0]})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
