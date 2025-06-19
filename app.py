from flask import Flask, render_template, url_for, request, redirect, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flash messages

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST']) # we use POSt method to hide the data which can be shown on public url
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get('gender')
    
    if not username or not email or not password:
        flash("All fields are required. Please fill out it.")
        return redirect(url_for('home'))

    # Checking if email already exists in our database
    # Check if the Excel file exists and email already exists
    path = 'users.xlsx'

    email_exists = False  # This is our Default value

    if os.path.exists(path):
        existing_data = pd.read_excel(path, engine='openpyxl')
        
        # Check if 'Email' column exists before looking up values
        if 'Email' in existing_data.columns:
            if email in existing_data['Email'].values:
                email_exists = True

    if email_exists:
        flash("Email already exists. Please try a different one.")
        return redirect(url_for('home'))


    user_data = pd.DataFrame([{
        'Username': username,
        'Gender': gender,
        'Email': email,
        'Password': password,
    }])

    if os.path.exists(path):
        present_data = pd.read_excel(path,engine='openpyxl') #The read_excel() method can read Excel 2007+ (.xlsx) files using the openpyxl Python module
        combined_data = pd.concat([present_data, user_data])  #It will append the  data in existing file
    else:
        combined_data = user_data


    #To write a DataFrame object to a sheet of an Excel file, you can use the to_excel instance method.
    # engine='openpyxl' --->Specifies the backend library used to create Excel files. openpyxl is required for .xlsx support.
    combined_data.to_excel(path,index=False,engine='openpyxl' )
    
    flash("Signup successful! Please login.")
    return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("All fields are required. Please fill out it.")
            return redirect(url_for('login'))
        
        path = 'users.xlsx'

        if not os.path.exists(path):
            flash('No users registered yet!')
            return redirect(url_for('login'))

        try:
            check_data = pd.read_excel(path, engine='openpyxl')

            if username not in check_data['Username'].values:
                flash('Username does not exist.')
                return redirect(url_for('login'))

            user = check_data[check_data['Username'] == username] #check the row in the excel file to match the user data

            if user['Password'].values[0] == password: #check the password from the row which was filtered from the above code
                flash('Login successful!')
                return redirect(url_for('main_page'))  # Redirect to main page after successful login
            else:
                flash("Password doesn't match the username.")
                return redirect(url_for('login'))

        except Exception as e:
            flash("Error during login. Please try again.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/main')  # New route for the main page
def main_page():
    return render_template('page.html')


@app.route('/download-data')
def download_data():
    path = 'users.xlsx'  # Path to your Excel file
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        flash("Data file not found.")
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1',port=8080)