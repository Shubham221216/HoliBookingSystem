from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text function
import razorpay
from flask_mail import Mail, Message
from sqlalchemy import inspect
from datetime import timedelta
import qrcode
import uuid
import math
from flask_migrate import Migrate
from io import BytesIO
import base64


app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nESoqHxQRFPlcUziHcBQgIxTTDbdoRAT@gondola.proxy.rlwy.net:48132/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# # 🔑 Replace with your Razorpay API Keys
RAZORPAY_KEY_ID = "rzp_live_LrhkqxYpvBkWBI"
RAZORPAY_KEY_SECRET = "Ag9Lt8kiiJvMyXKGGCgpMqVt"


# RAZORPAY_KEY_ID = "rzp_live_cXy0lZ4QA7cOjC"
# RAZORPAY_KEY_SECRET = "56lL0KRLjD4gngA43btNCOoW"

db = SQLAlchemy(app)


migrate = Migrate(app, db)

# Function to check database connection
def check_db_connection():
    try:
        db.session.execute(text('SELECT 1'))  # Explicitly using text()
        print("Database connected successfully!")
    except Exception as e:
        print(f"Error connecting to the database: {e}")





@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# Razorpay API Keys (Replace with your actual keys)
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))



# ✉️ Configure Flask-Mail (Use your email credentials)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chowdhurydevhelp22@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'ciuwztxgnxqfqbqc'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] ='chowdhurydevhelp22@gmail.com'

mail = Mail(app)



# Define the Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)
    num_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    plan_type = db.Column(db.String(50),nullable=False)
    payment_status = db.Column(db.Enum('Pending', 'Paid'), default='Pending')
    booking_count = db.Column(db.Integer, default=0)  # New Column
    # qr_code = db.Column(db.String(10000), unique=True, nullable=True)  # New column to store QR code URL
    qr_code = db.Column(db.Text, unique=True)  # Change from String(255) to Text

    entry_status = db.Column(db.Enum('Not Scanned', 'Scanned'), default='Not Scanned')  # New column for scan status


# Initialize the Database
with app.app_context():
    db.create_all()
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()  # Correct method
        print("Tables in the database:", tables)

        
         # Loop through each table and print its columns
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"Columns in table '{table}':")
            for col in columns:
                print(f" - {col['name']} ({col['type']})")

    except Exception as e:
        print(f"Error fetching tables: {e}")

    check_db_connection()

    

@app.route('/')
def index():
    total_booked = db.session.query(db.func.sum(Booking.num_tickets)).scalar() or 0
    available_tickets = 1500 - total_booked
    return render_template('index.html', available_tickets=available_tickets)


@app.route('/book', methods=['GET', 'POST'])
def book():

    print("This is book() function")

    if request.method == 'POST':
        num_tickets = int(request.form['num_tickets'])

        # Calculate the total booked tickets
        # total_booked = db.session.query(db.func.sum(Booking.num_tickets)).scalar() or 0

        # Check if total booked tickets exceed 1500
        # if total_booked + num_tickets > 1500:
        #     return "Booking limit exceeded! No more tickets available."

        session['num_tickets'] = num_tickets

        return render_template('plans.html', num_tickets=num_tickets)

    return render_template('index.html')






# @app.route('/plan', methods=['POST'])
# def plan():

#     print("This is plan() function")

#     email = request.form.get('email', 'Unknown')  
#     session['email'] = email  # Store email in session

#     plan_type = request.form.get('plan_type')  

#     if plan_type not in ["Plan 1", "Plan 2", "Plan 3"]:
#         return "Invalid Plan Selected!", 400  # Handle invalid plan selection

#     session['plan_type'] = plan_type  # Store plan type in session
#     num_tickets = int(session.get('num_tickets', 1))

#     # Plan Pricing
#     plan_prices = {"Plan 1": 1, "Plan 2": 2, "Plan 3": 3}
#     amount = num_tickets * plan_prices[plan_type]  # Calculate total price
#     session['amount'] = amount  # Store amount in session

#     print(f"Plan Type Stored in Session: {session.get('plan_type')}")
#     print(f"Amount Stored in Session: {session.get('amount')}")


#     # Create Razorpay order for LIVE mode
#     order = razorpay_client.order.create({
#         "amount": amount * 100,  # Convert to paisa
#         "currency": "INR",
#         "payment_capture": "1"  # Auto capture payment
#     })


#     return render_template('booking.html', order_id=order['id'], amount=amount, key_id=RAZORPAY_KEY_ID,email=email,plan_type=plan_type,num_tickets=num_tickets)


@app.route('/payment', methods=['POST'])
def payment():

    print("This is payment() function")

    email = request.form.get('email', 'Unknown')  # Use `.get()` to prevent errors
    session['email'] = email  # Store in session
    print(f"Email stored in session: {session.get('email')}")  # Debugging


    phone_number = request.form.get('phone','Unknown')
    session['phone'] = phone_number
    print(f"Phone Number stored in session: {session.get('phone')}")  # Debugging

    plan_type = request.form.get('plan_type', 'Unknown')  # Default Plan 1
    session['plan_type'] = plan_type
    print(f"Plan type is {session.get('plan_type')}")



    num_tickets = int(request.form.get('num_tickets', 0))
    session['num_tickets'] = num_tickets  
    print(f"Number of tickets: {num_tickets}")

    # # Plan Pricing
    # plan_prices = {"Plan 1": 1, "Plan 2": 2, "Plan 3": 3}

    plan_prices = {"1": 1, "2":2}  # Make the keys match the values from HTML
    amount = num_tickets * plan_prices[plan_type]  # Calculate total price
    session['amount'] = amount
    print(f"Amount is {session.get('amount')}")


    rounded_price_per_ticket = math.ceil(amount/num_tickets)
    print("Rounded amount is ")

    # ✅ Store multiple names in session as a list
    # names = [request.form.get(f'name_{i}') for i in range(1, int(session.get('num_tickets', 1)) + 1)]
    # session['names'] = names  # Store names in session

    name = request.form.get('name','Unknown')
    session['name']=name
    print(f"Names stored in session: {session.get('name')}")  # Debugging


    
    # amount = num_tickets * 1 # ₹500 per ticket
    # session['amount'] = amount

    # Create Razorpay order for LIVE mode
    order = razorpay_client.order.create({
        "amount": amount * 100,  # Convert to paisa
        "currency": "INR",
        "payment_capture": "1"  # Auto capture payment
    })

    return render_template('payment.html', order_id=order['id'], amount=amount, key_id=RAZORPAY_KEY_ID,email=email,name=name,phone_number=phone_number,plan_type=plan_type,num_tickets=num_tickets,rounded_price=rounded_price_per_ticket)



@app.route('/payment_success', methods=['POST'])
def payment_success():
    
    print("This is payment_success() function")

    email = session.get('email','Unknown')
    print(f"Retrieved Email in /payment_success: {email}")  # Debugging
    
    names = session.get('name', 'Unknown')
    session['name'] = names
    print(f"Names stored in session: {session.get('name')}")  # Debugging

    phone = session.get('phone', 'Unknown')
    session['phone'] = phone
    print(f"Phone Stored in session")

    amount = session.get('amount', 0)
    session['amount'] =  amount
    print(f"Amount stored in session: {session.get('amount')}")  # Debugging


    num_tickets = session.get('num_tickets', 0)
    session['num_tickets'] = num_tickets
    print(f"Number Tickets stored in session: {session.get('num_tickets')}")  # Debugging


    plan_type = session.get('plan_type', 'Unknown')
    session['plan_type'] = num_tickets
    print(f"Plan Type stored in session: {session.get('plan_type')}")  # Debugging

   

    # Get Razorpay Payment Details from frontend
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    signature = request.form.get('razorpay_signature')


    # Generate Unique QR Code URL
    # qr_data = f"Name: {names}\nEmail: {email}\nPhone: {phone}\nPlan: {plan_type}\nTickets: {num_tickets}\nAmount: {amount}\nPayment ID: {payment_id}"
    
    # Generate a unique verification link
    # unique_qr_url = f"https://holibookingsystem.onrender.com/verify_qr/{payment_id}"

    qr_code_data = f"https://holibookingsystem.onrender.com/verify_qr/{payment_id}"  # ✅ Link only to payment ID


    # Create QR Code
    qr = qrcode.make(qr_code_data)
    qr_io = BytesIO()
    qr.save(qr_io, format="PNG")
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')  # Convert to base64
    print(f'This is base64:-{base64}')


    # ✅ Verify Payment with Razorpay
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        # 🚀 Razorpay verification (only proceed if this passes)
        razorpay_client.utility.verify_payment_signature(params_dict)
        print("✅ Payment verified successfully.")

        # ✅ Check total booked tickets before storing the booking
        # total_booked = db.session.query(db.func.sum(Booking.num_tickets)).scalar() or 0
        # if total_booked + num_tickets > 1500:
        #     return "❌ Booking limit exceeded! No more tickets available."

        # ✅ Store booking details in database
        new_booking = Booking(
            user_email=email,
            num_tickets=num_tickets,
            total_price=amount,
            plan_type=plan_type,
            payment_status='Paid',
            qr_code=payment_id,  # ✅ Store only the payment_id
            entry_status='Not Scanned'
        )
        try:
            db.session.add(new_booking)
            db.session.commit()
            print("✅ Booking saved successfully.")
        except Exception as e:
            db.session.rollback()  # Rollback if an error occurs
            print("❌ Database error:", e)


        # ✅ Send invoice email to user
        send_invoice_email(email, names,phone,num_tickets, amount, payment_id,plan_type,qr_base64)

        # return render_template('success.html', email=email, names=names, plan_type=plan_type,qr_base64=qr_base64)
        # return render_template('success.html', email=email,names=names,plan_type=plan_type,phone=phone,amount=amount,num_tickets=num_tickets,payment_id=payment_id,qrcode=qr_base64)
        return jsonify({
            "email": email,
            "names": names,
            "plan_type": plan_type,
            "phone": phone,
            "amount": amount,
            "num_tickets": num_tickets,
            "payment_id": payment_id,
            "qrcode": qr_base64  # ✅ Send QR code in JSON response
        })


    except razorpay.errors.SignatureVerificationError:
        return "❌ Payment verification failed!", 400


@app.route('/success')
def success():
    print("This is success() function")
    email = session.get('email','Unknown')
    print(f"Retrieved Email : {email}")  # Debugging

    names = session.get('name', 'Unknown')  # Retrieve names
    print(f"Retrieved Names : {names}")  # Debugging

    plan_type = session.get('plan_type','Unknown')
    print(f'Plan Type is {plan_type}')

    phone = session.get('phone', 'Unknown')
    print(f"Phone Stored in session:{phone}")

    amount = session.get('amount', 0)
    session['amount'] =  amount
    print(f"Amount stored in session: {session.get('amount')}")  # Debugging


    num_tickets = session.get('num_tickets', 0)
    session['num_tickets'] = num_tickets
    print(f"Number Tickets stored in session: {session.get('num_tickets')}")  # Debugging

    payment_id = session.get('razorpay_payment_id')
    print(f"Payment Id:{payment_id}")


    # Generate a unique verification link
    unique_qr_url = f"https://holibookingsystem.onrender.com/verify_qr/{payment_id}"

    # # Create QR Code
    qr = qrcode.make(unique_qr_url)
    qr_io = BytesIO()
    qr.save(qr_io, format="PNG")
    qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')  # Convert to base64

    qr_code = request.args.get('qrcode','')

    print("This is base64 in success function",qr_base64)

    if not qr_code:
        print("❌ No QR Code Found")
    else:
        print("✅ QR Code Found:", qr_code)

    
    return render_template('success.html'
                           , email=email,names=names,plan_type=plan_type,
                           phone=phone,amount=amount,num_tickets=num_tickets,
                           payment_id=payment_id,qrcode=qr_base64
                           )







@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # ✅ Hardcoded admin credentials (you can store in DB)
        if username == "holination" and password == "theredcarpet":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))  # Redirect to dashboard after login
        else:
            return "❌ Invalid Admin Credentials!"

    return render_template('admin_login.html')  # Create an admin login page




@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)  # Remove admin session
    return redirect(url_for('admin_login'))




@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))

    bookings = Booking.query.all()
    return render_template('admin_dashboard.html', bookings=bookings)




@app.route('/verify_qr/<string:qr_code>', methods=['GET'])
def verify_qr(qr_code):

    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))  # Redirect to admin login if not logged in
    
    # Search for the QR Code in the database
    booking = Booking.query.filter_by(qr_code=qr_code).first()

    if not booking:
        return render_template('verify_qr.html', status="error", message="❌ Invalid QR Code!")

    if booking.entry_status == 'Scanned':
        return render_template('verify_qr.html', status="error", message="🚫 This QR Code has already been used for entry!")

    # Update the entry status
    booking.entry_status = 'Scanned'
    db.session.commit()

    return f"✅ Welcome {booking.user_email}! You have successfully entered the event."


def send_invoice_email(email, names,phone,num_tickets, amount, payment_id,plan_type,qr_code):
    subject = "Your Booking Invoice"
    body = f"""
    Hello {names},

    Thank you for your booking. Here are your details:
    
    Plan Type: {plan_type}

    Names:{names}

    Email:{email}

    Phone:{phone}

    Number of Tickets: {num_tickets}

    Total Amount Paid: ₹{amount}

    Scan the QR code below at the event entry.

    Payment ID: {payment_id}

    Best regards,
    HoliNation
    """
    msg = Message(subject, recipients=[email])
    msg.body = body
    # Attach QR Code as an image
    qr_img = base64.b64decode(qr_code)
    msg.attach("qr_code.png", "image/png", qr_img)

    
    

    try:
        mail.send(msg)
        print(f"Invoice sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")





if __name__ == '__main__':
    app.run(debug=True)


