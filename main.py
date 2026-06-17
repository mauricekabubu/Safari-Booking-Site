##AdventureBooker Website Backend section
#import necessary modules and libraries
#Flask framework --> Backend framework but it's flexible, reliable and lightweight
#flash -->for flashing messages-->error,info and success messages
#SQLALCHEMY for database to store users info in the database for sqlite3 or Mysql
#Werkzeug.security for password hashing to secure the application
#Sendgrid for email integration
#Openai for Ai integration using Api keys
#Datetime for current time
#OS for file handling and directory management
from flask import Flask,render_template,redirect,request,flash,url_for,session
#Flask_SQLAlchemy for database management
from flask_sqlalchemy import SQLAlchemy
#SQLAlchemy functions for database operations
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash
#Flask-Login for user session management
from flask_login import login_manager, login_user,login_required,logout_user,LoginManager, UserMixin,current_user
#OS module for operating system functionalities
import os
#Datetime module for handling date and time
from datetime import datetime
#Werkzeug utils for secure filename handling
from werkzeug.utils import secure_filename
#Exception handling for large file uploads
from werkzeug.exceptions import RequestEntityTooLarge
#Flask-Mail for email functionality
from flask_mail import Mail,Message
#dotenv for environment variable management
import dotenv
#import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail
#SSL module to handle SSL certificate verification
import ssl
#OpenAI module for AI integration
from openai import OpenAI
#wiki module for Wikipedia integration
from wikipedia import summary, page, search
#for ticket generation
import uuid
#functools for function decorators
from functools import wraps
#Flask-Migrate for database migrations
from flask_migrate import Migrate
#Flask-WTF for CSRF protection and form handling
from flask_wtf import CSRFProtect, FlaskForm
#WTForms for form fields and validation
from wtforms import StringField, PasswordField, SubmitField
#WTForms validators for form validation
from wtforms.validators import DataRequired, Email, Length, EqualTo
from itsdangerous import URLSafeTimedSerializer 


#Disabling SSL to allow Sendgrid functionality
#This is necessary for Sendgrid to work properly in some environments
ssl._create_default_https_context = ssl._create_unverified_context


#dotenv initialization
#Loading environment variables from .env file
dotenv.load_dotenv()

#Setting admin secret key
#This is used to authenticate admin users during registration
ADMIN_SECRET = os.getenv("ADMIN_SECRET","My_secret_key@254")

#CSRF protection initialization
#This is used to protect against Cross-Site Request Forgery attacks
crsf = CSRFProtect()

#Creating a Flask application instance
app = Flask(__name__)

#Image specifications initialization
#Setting up upload directory and allowed extensions
app.config["UPLOAD_DIRECTORY"] = os.path.join(os.getcwd(), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16*1024*1024 #16MB   
app.config["ALLOWED_EXTENSIONS"] = ["png","jpg","webp","jfif","jpeg","gif"]

#Setting up the secret key
#This key is used for session management and security purposes
app.config["SECRET_KEY"] = "My_secret_key254"

#Setting up Mail integration

#Database initialization
#Setting up the database URI and tracking modifications
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Mail initialization
#Mail configuration for sending emails
# ================= MAIL CONFIG =================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("DEL_EMAIL")
app.config["MAIL_PASSWORD"] = os.getenv("PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("SENDGRID_SENDER")

mail = Mail(app)



#Database model initialisation
#Creating a SQLAlchemy database instance
db = SQLAlchemy(app)

#Migrate initialization
migrate = Migrate(app, db)


#Creating a Database model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(300), default="default.jpg") 
    gallery = db.Column(db.String(200), default="default.jpg") 
    trips = db.relationship('Trips', backref='user', lazy=True)
    
    def get_reset_token(self,expires_sec=1800):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        return s.dumps({'user_id':self.id},salt="password-reset")
    
    @staticmethod
    def verify_reset_token(token,expires_sec=1800):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        
        try:
            data = s.loads(
                token,
                salt="password-reset",
                max_age=expires_sec
            )
        except Exception:
            return None
        
        return Users.query.get(data["user_id"])
    
    def __repr__(self):
        return f"< User id={self.id} username={self.username} email={self.email}"


    


#Creating a trip Database Model
class Trips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.String(200), db.ForeignKey('users.id',name="fk_trips_trip_id"), nullable=True)
        

    
    
#Creating a Notification Database Model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(100), nullable=False)
    customer_message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=func.current_timestamp())
    
    
#Creating a Gallery Database Model
class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(200), nullable=False)
    

#Creating a Booking Database Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200),nullable=False)
    customer_email = db.Column(db.String(200),nullable=False)
    customer_phone = db.Column(db.String(100),nullable=False)
    customer_price = db.Column(db.Float,nullable=False)
    trip_date = db.Column(db.Integer,nullable=False)
    payment_options = db.Column(db.String(100),nullable=False)
    

#Creating a Payment Database Model
#class Payment(db.Model):
    #id = db.Model(db.Integer,primary_key=True)
    

#Client database Model
class Clients(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    full_names = db.Column(db.String(400), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    #profile_pic = db.Column(db.String(200), default="default.jpg")
    
    def generate_reset_token(self,expires_sec=1800):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        
        return s.dumps({"user_id":self.id},salt="password_reset")
    
    @staticmethod
    def verify_reset_token(token,expires_sec=1800):
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        try:
            data= s.loads(
                token,
                salt="password_reset",
                max_age=expires_sec                
            )
        except Exception:
            return None
        
        return Clients.query.get(data["user_id"])
    

#Ticket database Model
class Ticket(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    ticket_code = db.Column(db.String(50),unique=True,nullable=False)
    booking_id = db.Column(db.Integer,nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    customer_name = db.Column(db.String(200),nullable=False)
    customer_email = db.Column(db.String(100),nullable=False)
    customer_phone = db.Column(db.String(20),nullable=False)
    customer_price = db.Column(db.Float,nullable=False)
    payment_options = db.Column(db.String(100),nullable=False)
    #created_at = db.column(db.DateTime, default=datetime.utcnow, nullable=False)
    
#Login manager initialization
#Setting up the login manager for user session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    if user:
        return user
    return Clients.query.get(int(user_id))

    
#Creating a seraching route
from sqlalchemy import or_

@app.route("/searching", methods=["POST"])
def searching():
    searched = request.form.get("title")

    results = Trips.query.filter(
        or_(
            Trips.title.ilike(f"%{searched}%"),
            Trips.description.ilike(f"%{searched}%"),
            Trips.date.ilike(f"%{searched}%"),
            Trips.price.ilike(f"%{searched}%")           
        )
    ).all()

    return render_template("index.html", results=results)

# admin login function decorator logic
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if not getattr(current_user, "is_admin", False):
            flash("Admins only", category="danger")
            return redirect(url_for('login'))
        
        return f(*args,**kwargs)
    
    return decorated_function
  
  
def client_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('signup'))

        # block admins from client pages
        if getattr(current_user, "is_admin", False):
            flash("Clients only", category="danger")
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")

#Ai route and Ai integration from openai Api
@app.route("/ai",methods=["GET","POST"])
def ai():
    output = None   

    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()

        if not user_input:
            flash("Input cannot be empty", category="danger")
            return redirect(url_for("ai"))

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
    

        output = response.choices[0].message.content

    return render_template("ai.html", output=output)

#Setting up Booking route
@app.route("/book",methods=["POST","GET"])
def book():
    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        customer_email = request.form.get("customer_email")
        customer_phone = request.form.get("customer_phone")
        customer_price = request.form.get("customer_price")
        trip_date = request.form.get("trip_date")
        payment_options = request.form.get("payment_options")
        
        if len(customer_name)<5:
            flash(f"{customer_name} must exceed 5 characters or be a full name",category="danger")
            
            return redirect(url_for("trips"))
        
        elif not  customer_price :
            flash("Price field cannot be empty", category="danger")
            
            return redirect(url_for("trips"))
        
        
        elif not trip_date:
            flash("Date field cannot be empty", category="danger")
            
            return redirect(url_for("trips"))       
        
        
        elif customer_email != customer_email.lower():
            flash(f"{customer_email} should be in lower case.")
            
            return redirect(url_for("trips"))
    
        
        elif len(customer_phone)<10:
            flash("Phone number must be at least 10 digits", category="danger")
            
            return redirect(url_for("trips"))
        
        try:
            customer_price = float(customer_price)
        except ValueError:
            flash("Invalid price format!",category="danger")
            
            return redirect(url_for("trips"))
        
        else:
            new_booking = Booking(customer_name=customer_name,
                                  customer_email=customer_email,
                                  customer_phone=customer_phone,
                                  customer_price=customer_price,
                                  trip_date=trip_date,
                                  payment_options=payment_options)
            
            db.session.add(new_booking)
            db.session.commit()
            
            flash("Booking successful! you will receive a confirmation message shortly plus \n a code on your email and sms for your ticket with all credentials.", category="success")
            
            ticket = Ticket(
                ticket_code = str(uuid.uuid4())[:8].upper(),
                booking_id = new_booking.id,
                customer_name = customer_name,
                customer_email = customer_email,
                customer_phone = customer_phone,
                customer_price = customer_price,         
                payment_options = payment_options
            )
            
                        
            db.session.add(ticket)
            db.session.commit()
            
            flash(f"Ticket {ticket.ticket_code} generated successfully", category="success")
        
            
            return redirect(url_for("trips"))
        
    return render_template("trips.html")

#Admin's history route for trips
@app.route("/history", methods=["POST","GET"])
@login_required
def history():
    trips = current_user.trips
    return render_template("history.html", trips=trips)

#Setting up a ticket route
@app.route("/ticket", methods=["POST","GET"])
@login_required
def ticket():
    tickets = Ticket.query.filter_by(customer_email=current_user.email).all()
    
    return render_template("tickets.html", tickets=tickets)
    

#Setting up a login route
@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")        
        
        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            
            flash("You have been successfully logged in ",category="success")
            
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid inputs, please try again!",category="danger")
            
            return redirect(url_for("admin"))
        
    return render_template("admin.html")

#Forgot password admin route
@app.route("/forgot",methods=["POST","GET"])
def forgot():
    if request.method=="POST":
        email = request.form.get("email")
        
        user = Users.query.filter_by(email=email).first()
        
        if user and user.email:
            token = user.get_reset_token()
            
            reset_link = url_for(
                "reset",
                token=token,
                _external=True
            )
            
            msg = Message(
                subject="password_reset",
                recipients=[user.email],
                body=f"Hi there {user.username}\n\nTo reset your password you have to click this link {reset_link}\n\nBut incase you did not request for it ignore it."
            )
            mail.send(msg)
            
            flash("The reset link has been send to the existing email given above into your email account.\n",category="success")
            
            return redirect(url_for("login"))
        
        else:
            flash("Email does not exist, use an existing email!",category="danger")
            
            return redirect(url_for("login"))
    return render_template("admin.html")

#Setting up admin reset password route
@app.route("/reset/<token>",methods=["GET","POST"])
def reset(token):
    user = Users.verify_reset_token(token)
    
    if not user:
        flash("Invalid or expired token!",category="danger")
        
        return redirect(url_for("forgot"))
    
    if request.method == "POST":
        password = request.form.get("password")
        password1 = request.form.get("password1")
        
        if password != password1:
            flash("Both passwords should be similar!",category="danger")
            
            return redirect(request.url)
        
        user.password = generate_password_hash(password)
        db.session.commit()
        
        flash("New password updated successfully,you can now login",category="success")
        
        return redirect(url_for("login"))
    
    return render_template("reset.html",token=token)

#Setting up admin profile route
@app.route("/profile", methods=["POST","GET"])
@login_required
def profile():
    return render_template("profile.html", user=current_user)  


#Setting up upload profile photo route
@app.route("/upload_pic", methods=["POST"])
@login_required
def upload_pic():
    file = request.files.get("uploadPic")

    try:
        if not file or file.filename == "":
            flash("File not selected", "danger")
            return redirect(url_for("profile"))

        extension = os.path.splitext(file.filename)[1].lower().lstrip(".")
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format", "danger")
            return redirect(url_for("profile"))

        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"], filename)
        file.save(file_path)

        current_user.profile_pic = f"uploads/{filename}"
        db.session.commit()

        flash("Profile picture updated",category="success")
        return redirect(url_for("profile"))

    except RequestEntityTooLarge:
        flash("File exceeds 16MB",category="danger")
        return redirect(url_for("profile"))


#Setting up upload image file route
@app.route("/upload_image",methods=["POST","GET"])
@login_required
def upload_image():
    image_url = request.files.get("image_url")
    
    try:
        if not image_url or not image_url.filename=="":
            flash("file not selected",category="danger")
            
            return redirect(url_for("add_trip"))
        
        extension = os.path.splitext(image_url.filename)[1].lower().lstrip(".")
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format", category="danger")
            
            return redirect(url_for("add_trip"))
        
        filename = secure_filename(f"trip_{current_user.id}_{image_url.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        image_url.save(file_path)
        
        current_user.image_url = filename
        
        db.session.commit()
        
        flash("image added successfully",category="success")
        
        return redirect(url_for("add_trip"))
    
    except RequestEntityTooLarge:
        flash("file exceeds 16MB", category="danger")
        
        return redirect(url_for("add_trip"))
   
#Setting up a Gallery route
@app.route("/add_gallery",methods=["GET","POST"])
@login_required
def add_gallery():
    images = Gallery.query.all()
    
    return render_template("add_gallery.html",images=images)

#Setting up the add modal gallery route
@app.route("/add_to_gallery", methods=["POST","GET"])
@login_required
def add_to_gallery():
    if request.method == "POST":
        image = request.files.get("image")
        
        try:
            if not image or image.filename=="":
                flash("file not selected", category="danger")
                
                return redirect(url_for("add_gallery"))
            
            extension = os.path.splitext(image.filename)[1].lower().lstrip(".")
            if extension not in app.config["ALLOWED_EXTENSIONS"]:
                flash("Invalid image format", category="danger")
                
                return redirect(url_for("add_gallery"))
            
            filename = secure_filename(f"gallery_{current_user.id}_{image.filename}")
            file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
            image.save(file_path)
            
            new_image = Gallery(image=filename)
            db.session.add(new_image)
            db.session.commit()
            
            flash("Image successfully added to gallery", category="success")
            
            return redirect(url_for("add_gallery"))
        
        except RequestEntityTooLarge:
            flash("file exceeds 16MB", category="danger")
            
            return redirect(url_for("add_gallery"))
        
#Setting up edit gallery route
@app.route("/edit_gallery/<int:id>", methods=["POST","GET"])
@login_required
def edit_gallery(id):
    image = Gallery.query.get_or_404(id)
    
    if request.method == "POST":
        image = request.files.get("image")  
        
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join("static/uploads", filename)
            image.save(image_path)
            image.image = filename
            
        db.session.commit()
        
        flash("Image successfully updated", category="success")
        
        return redirect(url_for("add_gallery"))
    
    return render_template("add_gallery.html", image=image)


#Setting up delete gallery route
@app.route("/delete_image/<int:id>", methods=["POST","GET"])
@login_required
def delete_image(id):
    image = Gallery.query.get_or_404(id)
    
    db.session.delete(image)
    db.session.commit() 
    
    flash("Image successfully deleted from gallery", category="success")
    
    return redirect(url_for("add_gallery"))        
            
    

#Setting up register route
@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":        
        username = request.form.get("username")
        phone = request.form.get("phone")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")
        is_admin = request.form.get("is_admin")
        
        existing_user = Users.query.filter_by(username=username).first()
        existing_email = Users.query.filter_by(email=email).first()
        
        if existing_user and check_password_hash(existing_user.password, password):
            flash("Account already exists !!",category="danger")
            
        elif existing_email:
            flash("Email already exists !!", category="danger")
            
        elif len(username)<4:
            flash("Username is below 4 characters", category="danger")
        
            
        elif len(password)<8:
            flash("Password is less than 8 characters", category="danger")
            
        elif email != email.lower():
            flash("Email should be written in small letters", category="danger")
            
        elif password2 != password:
            flash("wrong password confirmation must be same", category="danger")            
        
        else:
            is_admin = (is_admin == ADMIN_SECRET)
            new_user = Users(username=username,
                             email=email,
                             phone=phone,
                             is_admin = is_admin,
                             password = generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"New account created under the username: {username}", category="success")
            
            return redirect(url_for("admin"))        
        
    return render_template("register.html")


#Setting up logout route
@app.route("/logout")
@login_required
def logout():    
    logout_user()
    flash("You have successfully logged out", category="success")
    
    return redirect(url_for("index"))

#Setting up dashboard route
@app.route("/dashboard",methods=["POST","GET"])
@login_required
def dashboard():    
    booking_count = Booking.query.count()
    notification_count = Notification.query.count()
    #payments_count = Payment.query.count()
    users_count = Clients.query.count()
    
    return render_template("dashboard.html",notification_count=notification_count,booking_count=booking_count,
                           users_count=users_count)


#Setting up notifications route
@app.route("/notify", methods=["POST","GET"])
@login_required
def notify():
    notes = Notification.query.all()
    
    return render_template("notify.html",notes=notes)

#Setting delete notifications 
@app.route("/delete_note/<int:id>",methods=["POST","GET"])
@login_required
def delete_note(id):
    note = Notification.query.get_or_404(id)
    
    db.session.delete(note)
    db.session.commit()
    
    flash("You have successfully deleted the notification",category="success")
    
    return redirect(url_for("notify"))

#Setting up add trip route
@app.route("/add_trip", methods=["POST","GET"])
@login_required
def add_trip():
    items = Trips.query.all()
    
    
    return render_template("add_trip.html",items=items)


#Setting add trip button modal route
@app.route("/add",methods=["POST","GET"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        date = request.form.get("date")
        image_url = request.files.get("image_url")
        
        if not title or not description or not price or not date or not image_url:
            flash("All fields must be filled", category="danger")
            
            return redirect(url_for("add_trip"))
        
        if price:
            try:
                price = float(price)
                
            except ValueError:
                flash("Invalid price format",category="danger")
                
                return render_template("add_trip")
            
        if not image_url or image_url.filename == "":
            flash("file not selected", category="danger")
            
            return redirect(url_for("add_trip"))
            
        extension = os.path.splitext(image_url.filename)[1].lower().lstrip(".")
        if extension not in app.config["ALLOWED_EXTENSIONS"]:
            flash("Invalid image format", category="danger")
            
            return redirect(url_for("add_trip"))
        
        filename = secure_filename(f"trip_{current_user.id}_{image_url.filename}")
        file_path = os.path.join(app.config["UPLOAD_DIRECTORY"],filename)
        image_url.save(file_path)
        
        trip = Trips(title=title, description=description, price=price,
                    date=date, image_url=filename, user_id=current_user.id)
        
        db.session.add(trip)
        db.session.commit()
        
        flash("Items successfully added",category="success")
        
        return redirect(url_for("add_trip"))
    
    return render_template("add_trip.html")
 

#Setting up edit route
@app.route("/edit/<int:id>", methods=["POST","GET"])
@login_required
def edit(id):
    item = Trips.query.get_or_404(id)
    
    if request.method == "POST":
        item.title = request.form.get("title")
        item.description = request.form.get("description")
        item.price = request.form.get("price")
        item.date = request.form.get("date")
        
        image_url = request.files.get("image_url")
        if image_url and image_url.filename:
            filename = secure_filename(image_url.filename)
            image_path = os.path.join("static/uploads", filename)
            image_url.save(image_path)
            item.image_url = filename
            
        db.session.commit()
        
        flash("Items successfully updated", category="success")
        
        return redirect(url_for("add_trip"))
    
    return render_template("add_trip.html", item=item)
            

#Setting up delete route
@app.route("/delete/<int:id>", methods=["POST","GET"])
@login_required
def delete(id):
    item = Trips.query.get_or_404(id)   
    
    db.session.delete(item)
    db.session.commit()
    
    flash("Items successfully deleted", category="success")
    
    return redirect(url_for("add_trip"))         

#Setting up trips route
@app.route("/trips", methods=["POST","GET"])
def trips():
    items = Trips.query.all()
    
    return render_template("trips.html",items=items)

#Setting up about us route
@app.route("/about", methods=["GET","POST"])
def about():
    return render_template("about.html")

#Setting up FAQ route
@app.route("/FAQ", methods=["GET","POST"])
def FAQ():
    return render_template("FAQ.html")

#Setting up gallery route
@app.route("/gallery",methods=["GET","POST"])
def gallery():
    images = Gallery.query.all()
    
    return render_template("gallery.html",images=images)

#Setting up contacts route
@app.route("/contact", methods=["POST","GET"])
def contact():
    if request.method =="POST":
        customer_name = request.form.get("customer_name")
        customer_email = request.form.get("customer_email")
        customer_phone = request.form.get("customer_phone")
        customer_message = request.form.get("customer_message")
        
        if not customer_name or not customer_email or not customer_phone or not customer_message:
            flash("All fields must be filled", category="danger")
            
            return redirect(url_for("contact"))
        
        else:
            new_note = Notification(customer_name=customer_name,
                                    customer_email=customer_email,customer_phone=customer_phone,
                                    customer_message=customer_message)
            db.session.add(new_note)
            db.session.commit()
            
            flash("Message was sent successfully...",category="success")
            
            return redirect(url_for("contact"))
    
    return render_template("contact.html")


#Setting up an admin route
@app.route("/admin", methods=["POST","GET"])
def admin():
    return render_template("admin.html")

##CLIENT'S/CUSTOMER ROUTES  
#Customer/client  signup page route
@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = Clients.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash(f"Welcome again {username} you have logged in successful", category="success")
            
            return redirect(url_for("client_dash"))
        
        else:
            flash("Invalid inputs, please try again",category="danger")
            
            return redirect(url_for("signup"))
        
    return render_template("signup.html")

# Register_client route
@app.route("/register_client", methods=["GET","POST"])
def register_client():
    if request.method == "POST":
        full_names = request.form.get("full_names")
        email = request.form.get("email")
        phone = request.form.get("phone")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password")
        
        exists_user = Clients.query.filter_by(username=username).first()
        exists_email = Clients.query.filter_by(email=email).first()
        
        if exists_user and check_password_hash(exists_user.password,password):
            flash("Account already exists!", category="danger")
            
            return redirect(url_for("signup.html"))
        
        elif exists_email:
            flash("Email already exists!", category="danger")
            
            return redirect(url_for("register_client"))
        
        elif len(username)<4:
            flash("Username must exceed 4 characters", category="danger")
            
            return redirect(url_for("register_client"))
        
        elif len(password)<8:
            flash("Password must exceed 8 characters",category="danger")
            
            return redirect(url_for("register_client"))
        
        elif email != email.lower():
            flash("Email must be in lower case letters",category="danger")
            
            return redirect(url_for("register_client"))
        
        elif password != password2:
            flash("The two passwords must be similar", category="register_client")
            
            return redirect(url_for("register_client"))
        
        else:
            new_user = Clients(full_names=full_names,
                               email=email,phone=phone,
                               password=generate_password_hash(password),
                               username=username
                               )
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"Account created successfully as {username}", category="success")
            
            return redirect(url_for("signup"))
        
    return render_template("register_client.html")

# Forgot_pass route
@app.route("/forgot_pass", methods=["POST","GET"])
def forgot_pass():
    if request.method == "POST":
        email = request.form.get("email")
        user = Clients.query.filter_by(email=email).first()
        
        if user and user.email:
            token = user.generate_reset_token()
            
            reset_link = url_for(
                "reset_pass",
                token=token,
                _external=True
            )
            
            msg = Message(
                subject="password_reset",
                recipients= [user.email],
                body=f"Hi there {user.username}\n\nClick this link {reset_link} to reset your password\n\nIncase you didn't request for it ignore it."
            )
            mail.send(msg)
            
            flash("A reset link has been send to your email account with the above email account given.",category="success")
            
            return redirect(url_for("signup"))
    
        
        else:
            flash("Email does not exists please use an existing email", category="danger")
            
            return redirect(url_for("signup"))
        
    return render_template("signup.html")


@app.route("/reset_pass/<token>",methods=["GET","POST"])
def reset_pass(token):
    user = Clients.verify_reset_token(token)
    
    if not user:
        flash("Expired token please try again!",category="danger")
        
        return redirect(url_for("signup"))
    
    if request.method == "POST":
        password = request.form.get("password")
        password1 = request.form.get("password1")
        
        if password != password1:
            flash("Both passwords should be similar.",category="success")
            
            return redirect(request.url)
        
        user.password = generate_password_hash(password)
        
        db.session.commit()
        
        flash("New password successfully updated, you can now login",category="success")
        
        return redirect(url_for("signup"))
    
    return render_template("reset.html",token=token)
        

#Setting up client/customer logout route
@app.route("/pop",methods=["POST","GET"])
@login_required
def pop():
    logout_user()
    
    flash("You have successfully logged out.",category="success")
    
    return redirect(url_for("index"))

#Setting up Users route
@app.route("/users", methods=["POST","GET"])  
@login_required
def users():
    items = Clients.query.all()
    
    return render_template("users.html",items=items)


#Setting up edit user route
@app.route("/edit_user/<int:id>", methods=["POST","GET"])
@login_required
def edit_user(id):
    item = Clients.query.get_or_404(id)
    
    if request.method == "POST":
        item.full_names = request.form.get("full_names")
        item.email = request.form.get("email")
        item.phone = request.form.get("phone")
        item.username = request.form.get("username")
        
        db.session.commit()
        
        flash("User details successfully updated", category="success")
        
        return redirect(url_for("users"))
    
    return render_template("users.html", item=item) 


#Setting up delete user route
@app.route("/delete_user/<int:id>", methods=["POST","GET"])
@login_required
def delete_user(id):
    item = Clients.query.get_or_404(id)
    
    db.session.delete(item)
    db.session.commit()
    
    flash("User successfully deleted", category="success")
    
    return redirect(url_for("users"))

#Setting up booking admin results route
@app.route("/booking_results", methods=["POST","GET"])
@login_required
def booking_results():
    books = Booking.query.all()
    
    return render_template("book_res.html",books=books)

#Setting up an edit booking route
@app.route("/edit_book/<int:id>", methods=["POST","GET"])
@login_required
def edit_book(id):
    book = Booking.query.get_or_404(id)
    
    if request.method == "POST":
        book.customer_name = request.form.get("customer_name")
        book.customer_email = request.form.get("customer_email")
        book.customer_phone = request.form.get("customer_phone")
        book.customer_price = request.form.get("customer_price")
        book.trip_date = request.form.get("trip_date")
        book.payment_options = request.form.get("payment_options")
        
        db.session.commit()
        
        flash("Booking details successfully updated", category="success")
        
        return redirect(url_for("booking_results"))
    
    return render_template("book_res.html", book=book)

#Setting up delete booking route
@app.route("/delete_book/<int:id>", methods=["POST","GET"])
@login_required
def delete_book(id):
    book = Booking.query.get_or_404(id)
    
    db.session.delete(book)
    db.session.commit()
    
    flash("Booking successfully deleted", category="success")
    
    return redirect(url_for("booking_results"))

# client_dashboard route
@app.route("/client_dash", methods=["POST","GET"])
@login_required
def client_dash():
    bookings = Booking.query.count()
    tickets = Ticket.query.count()
    
    return render_template("client_dash.html",bookings=bookings,tickets=tickets)

#Setting up client profile route
@app.route("/client_profile",methods=["POST","GET"])
@login_required
def client_profile():
    user = Clients.query.filter_by(id=current_user.id).first()

    return render_template("client_profile.html",user=user)

#Setting up edit client profile route
@app.route("/edit_profile",methods=["POST","GET"])
@login_required
def edit_profile():
    user = Clients.query.filter_by(id=current_user.id).first()

    return render_template("client_profile.html", user=user)

#Setting Quickstats route
@app.route("/tickets",methods=["POST","GET"])
@login_required
def tickets():
    user = Ticket.query.filter_by(client_id=current_user.id).all()

    return render_template("tickets.html", user=user)

#Setting up upcoming trips route
@app.route("/upcoming_trips",methods=["POST","GET"])
@login_required
def upcoming_trips():
    b =  Booking.query.filter_by(customer_email=current_user.email).all()
    t = Ticket.query.filter_by(customer_email=current_user.email).all()
    n = Notification.query.filter_by(customer_email=current_user.email).all()

    return render_template("upcoming_trips.html",
                           b=b,
                           t=t,
                           n=n)

#Setting up users_history route
@app.route("/users_history",methods=["POST","GET"])
@login_required
def users_history():
    
    return render_template("users_history")

#Setting up users_payment route
@app.route("/users_payment",methods=["POST","GET"])
@login_required
def users_payment():
    
    return render_template("users_payment.html")


#Mail integration and function route using Sendgrid
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail

@app.route("/mail", methods=["POST"])
def send_mail():
    print("API KEY:", os.getenv("SENDGRID_API_KEY"))
    print("SENDER:", os.getenv("SENDGRID_SENDER"))

    
    username = request.form.get("username")
    subject = request.form.get("subject")
    message = request.form.get("message")
    customer_email = request.form.get("customer_email")

    if not customer_email:
        flash("Customer email is required!", "danger")
        return redirect(url_for("notify"))
    
    html_content = f"""
    <h2>New Message from {username}</h2>
    <p>{message}</p>
    """

    email = SendGridMail(
        from_email=os.getenv("SENDGRID_SENDER"),
        to_emails=customer_email,
        subject=subject,
        plain_text_content=f"From: {username}\n\n{message}",
        html_content=html_content
    )
    
    email.reply_to = os.getenv("SENDGRID_SENDER")


    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(email)
        flash("Message sent successfully!", "success")

    except Exception as e:
        flash(f"Failed to send message: {e}", "danger")

    return redirect(url_for("notify"))

#Using wikipedia module to fetch summary and page url
@app.route("/search_wiki", methods=["POST"])
def search_wiki():

    topic = request.form.get("topic")

    if not topic:
        flash("Please enter a topic",category="danger")
        return redirect(url_for("index"))

    try:
        summary_result = summary(topic, sentences=5)

        page_title = search(topic)[0]
        wiki_page = page(page_title)
        page_url = wiki_page.url

        return render_template(
            "index.html",
            summary_result=summary_result,
            page_url=page_url
        )

    except Exception as e:
        flash(f"Error occurred: {e}", category="danger")
        return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    