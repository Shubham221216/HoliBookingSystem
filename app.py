from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Import text function
import razorpay
from flask_mail import Mail, Message
from sqlalchemy import inspect


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:nESoqHxQRFPlcUziHcBQgIxTTDbdoRAT@gondola.proxy.rlwy.net:48132/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# 🔑 Replace with your Razorpay API Keys
RAZORPAY_KEY_ID = "rzp_live_LrhkqxYpvBkWBI"
RAZORPAY_KEY_SECRET = "Ag9Lt8kiiJvMyXKGGCgpMqVt"

db = SQLAlchemy(app)


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
    payment_status = db.Column(db.Enum('Pending', 'Paid'), default='Pending')
    booking_count = db.Column(db.Integer, default=0)  # New Column


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
    if request.method == 'POST':
        num_tickets = int(request.form['num_tickets'])

        # Calculate the total booked tickets
        total_booked = db.session.query(db.func.sum(Booking.num_tickets)).scalar() or 0

        # Check if total booked tickets exceed 1500
        if total_booked + num_tickets > 1500:
            return "Booking limit exceeded! No more tickets available."

        session['num_tickets'] = num_tickets
        return render_template('booking.html', num_tickets=num_tickets)

    return render_template('index.html')



# @app.route('/payment', methods=['POST'])
# def payment():
#     names = [request.form[f'name_{i}'] for i in range(1, int(session['num_tickets']) + 1)]
    
#     email = request.form['email']
#     amount = session['num_tickets'] * 500  # ₹500 per ticket
    
#     session['email'] = email
#     session['names'] = names
#     session['amount'] = amount

#     # Redirect user to Razorpay.me payment link
#     return redirect("https://razorpay.me/@shubham5352")


# @app.route('/payment', methods=['POST'])
# def payment():
#     num_tickets = int(session.get('num_tickets', 1))
#     amount = num_tickets * 500  # ₹500 per ticket

#     session['amount'] = amount

#     # Create Razorpay order
#     order = razorpay_client.order.create({
#         "amount": amount * 100,  # Convert to paisa
#         "currency": "INR",
#         "payment_capture": "1"  # Auto capture payment
#     })

#     return render_template('payment.html', order_id=order['id'], amount=amount, key_id=RAZORPAY_KEY_ID)


@app.route('/payment', methods=['POST'])
def payment():
    num_tickets = int(session.get('num_tickets', 1))
    amount = num_tickets * 5  # ₹500 per ticket
    session['amount'] = amount

    # Create Razorpay order for LIVE mode
    order = razorpay_client.order.create({
        "amount": amount * 100,  # Convert to paisa
        "currency": "INR",
        "payment_capture": "1"  # Auto capture payment
    })

    return render_template('payment.html', order_id=order['id'], amount=amount, key_id=RAZORPAY_KEY_ID)


    # Create Razorpay QR Code
    # Remove or modify the Razorpay QR Code section (Only for test mode)
    # qr_code = razorpay_client.qrcode.create({
    #     "type": "upi_qr",
    #     "name": "Ticket Payment",
    #     "usage": "single_use",
    #     "fixed_amount": True,
    #     "payment_amount": amount * 100,
    #     "description": "Ticket Booking Payment",
    #     "order_id": order['id']
    # })


    # return render_template('payment.html', order_id=order['id'], qr_code=qr_code['image_url'], amount=amount, key_id=RAZORPAY_KEY_ID)



# @app.route('/payment-success', methods=['GET'])
# def payment_success():
#     # Since there's no automatic verification, you must manually check payments in Razorpay dashboard.
#     new_booking = Booking(
#         user_email=session.get('email'),
#         num_tickets=session.get('num_tickets'),
#         total_price=session.get('amount'),
#         payment_status='Pending'  # Change to 'Paid' manually after checking Razorpay dashboard
#     )
#     db.session.add(new_booking)
#     db.session.commit()

#     return render_template('success.html', email=session.get('email'))

@app.route('/payment-success', methods=['POST'])
def payment_success():
    email = session.get('email')
    names = session.get('names', [])
    amount = session.get('amount', 0)
    payment_id = request.args.get('payment_id', 'N/A')  # Razorpay sends payment_id in query params

    # Store booking details
    new_booking = Booking(
        user_email=email,
        num_tickets=session.get('num_tickets'),
        total_price=amount,
        payment_status='Pending'  # Change to 'Paid' manually after checking Razorpay dashboard
    )
    db.session.add(new_booking)
    db.session.commit()

    # Send invoice email
    send_invoice_email(email, session.get('names', []), amount, payment_id)
    return render_template('success.html', email=email)



def send_invoice_email(email, names, amount, payment_id):
    subject = "Your Booking Invoice"
    body = f"""
    Hello,

    Thank you for your booking. Here are your details:

    Names:
    {', '.join(names)}

    Total Amount Paid: ₹{amount}
    Payment ID: {payment_id}

    Best regards,
    Your Company Name
    """

    msg = Message(subject, recipients=[email])
    msg.body = body

    try:
        mail.send(msg)
        print(f"Invoice sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")





if __name__ == '__main__':
    app.run(debug=True)


