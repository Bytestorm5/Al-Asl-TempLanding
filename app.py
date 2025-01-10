from flask import Flask, render_template, request, redirect, flash, g
from flask_babel import Babel, gettext as _, lazy_gettext as _l
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

def get_locale():
    # Use the locale from user settings or the browser's accept-language header
    if 'lang' in request.args:
        return request.args['lang']
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    return request.accept_languages.best_match(['en', 'ur'])

def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)

@app.context_processor
def inject_locale():
    return {'locale': get_locale()}

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
        flash(_("Invalid email address. Please try again."), "danger")
        return redirect('/')

    try:
        # Add to waitlist
        add_waitlist(first_name, last_name, email)
        flash(_("Successfully added to the waitlist!"), "success")
    except Exception as e:
        flash(_("An error occurred: {error}").format(error=str(e)), "danger")

    return redirect('/')

if __name__ == '__main__':
    if platform.system() == 'Windows':
        app.run(debug=True, port=5000)
    else:
        app.run(port=80, host='0.0.0.0')
