from flask import Flask, request, redirect, send_file, url_for, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__,template_folder='.')

def connect_db():
    import os
    db_path = os.path.abspath('ins.db')
    print(f"Database path: {db_path}")
    return sqlite3.connect(db_path)

@app.route('/')
def index():
    return send_file('dashboard.html')            #URL for SignUp

# Sign up route
@app.route('/signup')
def signup():
    return send_file('signup.html')    

@app.route('/login')
def login():
    return send_file('login.html')

@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    conn = connect_db()
    cursor = conn.cursor()
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confpass = request.form['confirm-password']

    # Check if passwords match
    if password == confpass:
        try:
            # Check if the table exists and insert data
            cursor.execute(
                '''CREATE TABLE IF NOT EXISTS Users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )'''
            )
            
            # Check if the email already exists
            cursor.execute('''SELECT * FROM Users WHERE email = ?''', (email,))
            if cursor.fetchone() is None:
                cursor.execute(
                    '''INSERT INTO Users (username, email, password) VALUES (?, ?, ?)''',
                    (name, email, password)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('dashboard', email=email))
            else:
                conn.close()
                return "Email already exists. Please try again."
        except Exception as e:
            conn.close()
            return f"An error occurred: {e}"
    else:
        return "Passwords do not match."
        
            
    conn.close()
    return redirect(url_for('/signup'))


@app.route('/confirmacc',methods=['GET','POST'])
def confirmacc():
    email = request.form['email']
    passw = request.form['password']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT COUNT(*) FROM Users WHERE email=? AND password=?''',(email,passw)
    )
    result = cursor.fetchone()
    if result[0]==1:
        conn.close()
        return redirect(url_for('dashboard',email = email))
    else:
        conn.close()
        return redirect(url_for('login'))
    
@app.route('/dashboard/<email>',methods=['GET','POST'])
def dashboard(email):
    return render_template("curr_new.html", email=email)

@app.route('/current_insurance/<email>', methods = ['GET','POST'])
def current_insurance(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM Insurance WHERE email = ?''',(email,)
    )
    results = cursor.fetchall()
    insurance = []
    for i in results:
        table_name = f"{i[2]}"
        cursor.execute(
            f'''SELECT * FROM {table_name} WHERE planid = ?''',(i[3],)
        )
        plan = cursor.fetchall()
        ins = [i[2], i[4]] + list(plan[0][1:])
            

        insurance.append(ins)
    
    conn.close()
    return render_template("cuurent_ins.html",email = email, insurance = insurance)

@app.route('/new_insurance/<email>', methods = ['GET','POST'])
def new_insurance(email):
    return render_template("ins_options.html",email = email)

@app.route('/home_insurance/<email>')
def home_insurance(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM Home'''
    )
    plans = cursor.fetchall()
    conn.close()
    return render_template("home.html", email = email, plans = plans)

@app.route('/life_insurance/<email>')
def life_insurance(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM Life'''
    )
    plans = cursor.fetchall()
    conn.close()
    return render_template("life_ins.html",email = email, plans = plans)

@app.route('/health_insurance/<email>')
def health_insurance(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT * FROM Health'''
    )
    plans = cursor.fetchall()
    conn.close()
    return render_template("health_ins.html",email = email, plans = plans)

@app.route('/apply',methods=['GET','POST'])
def apply():
    email = request.form['email']
    plan = request.form['plan']
    typ = request.form['type']
    return render_template("details.html",email = email, plan = plan, typ = typ)

    

@app.route('/approve', methods=['GET', 'POST'])
def approve():
    name = request.form['name']
    benef = request.form['beneficiary']
    nom = request.form['nominee']
    add = request.form['address']
    phone = request.form['phone']
    bank = request.form['bank_name']
    accno = request.form['account_number']
    ifsc = request.form['ifsc_code']
    
    mail = request.form['email']
    typ = request.form['type']
    plan = request.form['plan']
    
    conn = connect_db()  # Assuming you have a function to connect to your database
    cursor = conn.cursor()
    
    # Check if any insurance plan exists with the given type
    cursor.execute('''SELECT COUNT(*) FROM Insurance WHERE type=? AND email=?''', (typ,mail))
    result = cursor.fetchone()  # fetchone() returns a tuple with one element
    
    if result[0] == 0:  # If no rows found (count is 0)
        # Insert the new insurance plan into the database
        cursor.execute(
            '''INSERT INTO Insurance(email, type, planid, start) VALUES (?,?,?,CURRENT_DATE)''', 
            (mail, typ, plan)
        )
        conn.commit()
        
        cursor.execute(
            '''INSERT INTO Details(name,beneficiary,nominee,address,phone,email,bank,accno,ifsc) VALUES (?,?,?,?,?,?,?,?,?)''',(name,benef,nom,add,phone,mail,bank,accno,ifsc)
        )
        conn.commit()
        conn.close()
        
        # Redirect to the dashboard with the email as a query parameter
        return redirect(url_for('dashboard', email=mail))
    
    # If the condition is not met (i.e., there's already a plan with the given type)
    conn.close()
    
    return "Insurance already exists. Please try again."
if __name__ == '__main__':
    app.run(debug=True)
