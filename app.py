from flask import Flask, render_template, request, redirect, flash
import os
import resend
import re
from dotenv import load_dotenv
import platform

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

def add_waitlist(first_name: str, last_name: str, email: str):
    params: resend.Contacts.CreateParams = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "unsubscribed": False,
        "audience_id": os.environ["RESEND_AUDIENCE"],
    }

    return resend.Contacts.create(params)

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

def validate_email(email):
    # Simple regex for email validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/waitlist', methods=['POST'])
def waitlist():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')

    # Validate email
    if not validate_email(email):
        #print("Invalid email address. Please try again.")
        flash("Invalid email address. Please try again.", "danger")
        return redirect('/')

    try:
        # Add to waitlist
        add_waitlist(first_name, last_name, email)
        flash("Successfully added to the waitlist!", "success")
        #print("Successfully added to the waitlist!")
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        print(f"An error occurred: {str(e)}")

    return redirect('/')

if __name__ == '__main__':
    if platform.system() == 'Windows':
        app.run(debug=True, port=5000)
    else:
        app.run(port=80, host='0.0.0.0')
