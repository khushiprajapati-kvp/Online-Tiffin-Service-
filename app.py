from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import os
from werkzeug.utils import secure_filename
import re
from datetime import datetime
from flask import flash, redirect, url_for, render_template, request
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Set it in your .env file.")

# ================= DATABASE =================
conn = pymysql.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_NAME", "ots"),
    port=int(os.environ.get("DB_PORT", "3306")),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

# ================= IMAGE UPLOAD SETTINGS =================
UPLOAD_FOLDER = "static/gallery"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================= HOME =================
@app.route('/')
def home():
    return render_template('home.html')

# ================= CONTACT =================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    user = None
    if 'user_id' in session:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT name, email, contact FROM users WHERE id=%s", (session['user_id'],))
        user = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_no = request.form['contact']
        message = request.form['message']

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, contact, message, date_posted) VALUES (%s, %s, %s, %s, NOW())",
            (name, email, contact_no, message)
        )
        conn.commit()
        return render_template('contact.html', message_sent=True)

    return render_template('contact.html', user=user, message_sent=False)

# ================= VIEW CONTACTS MESSAGE=================
@app.route('/view_contacts')
def view_contacts():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact_messages ORDER BY id ASC")
    messages = cursor.fetchall()
    return render_template("view_contacts.html", messages=messages)

# ================= DELETE CONTACTS MESSAGE =================
@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    if 'admin_id' not in session:
        flash("Please login as admin")
        return redirect(url_for('login'))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contact_messages WHERE id=%s", (message_id,))
    conn.commit()
    flash("Message deleted successfully")
    return redirect(url_for('view_contacts'))

# ================= ABOUT =================
@app.route('/about')
def about():
    return render_template('about.html')

# ================= REGISTER =================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']

        # 🔹 Fetch separate address fields
        house_no = request.form['house_no']
        street = request.form['street']
        area = request.form['area']
        city = request.form['city']
        pincode = request.form['pincode']

        # 🔹 Combine into one address string for DB
        address = f"{house_no}, {street}, {area}, {city} - {pincode}"

        # 🔐 Password validation
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(pattern, password):
            flash("❌ Password must contain uppercase, lowercase, number & special character")
            return redirect(url_for('register'))

        cursor = conn.cursor()

        # 🔍 Check existing email
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing = cursor.fetchone()

        if existing:
            flash("❌ Email already registered")
            return redirect(url_for('login'))

        # ✅ Insert user
        cursor.execute(
            "INSERT INTO users (name,email,password,contact,address) VALUES (%s,%s,%s,%s,%s)",
            (name, email, password, contact, address)
        )
        conn.commit()

        # 🎉 Success message
        flash("✅ Registration successful")
        return redirect(url_for('login'))

    return render_template('register.html')

# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 🔍 Check email
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            flash("Email is not valid", "error")
            return render_template('login.html')

        # 🔐 Check password
        if user['password'] != password:
            flash("Password is not valid", "error")
            return render_template('login.html')

        # ✅ Login success
        session['user_id'] = user['id']
        session['user_name'] = user['name']

        flash("Login successful", "success")
        return redirect(url_for('home'))

    return render_template('login.html')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('home'))

# ================= MENU =================
@app.route('/menu')
def menu():
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT m.*, 
               IFNULL(AVG(r.rate), 0) AS rating
        FROM menu m
        LEFT JOIN ratings r ON m.id = r.menu_id
        GROUP BY m.id
    """)

    items = cursor.fetchall()
    return render_template('menu.html', items=items)

# ================= ADD STAFF =================
@app.route('/add_staff', methods=['GET','POST'])
def add_staff():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        role = request.form['role'].strip()

        allowed_roles = ['Delivery Staff', 'Chef', 'Manager', 'Tiffin Packer']
        if role not in allowed_roles:
            flash("Invalid role selected!")
            return redirect(url_for('add_staff'))

        cursor.execute("SELECT * FROM staff WHERE s_email=%s", (email,))
        if cursor.fetchone():
            flash("Email already exists!")
            return redirect(url_for('add_staff'))

        cursor.execute(
            "INSERT INTO staff (s_name,s_email,s_phone,s_role) VALUES (%s,%s,%s,%s)",
            (name,email,phone,role)
        )
        conn.commit()
        flash("Staff added successfully")
        return redirect(url_for('view_staff'))

    return render_template("add_staff.html")

# ================= VIEW STAFF =================
@app.route('/view_staff')
def view_staff():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM staff ORDER BY s_id ASC")
    staff = cursor.fetchall()
    return render_template("view_staff.html", staff=staff)

# ================= EDIT STAFF =================
@app.route('/edit_staff/<int:id>', methods=['GET','POST'])
def edit_staff(id):

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch existing data
    cursor.execute("SELECT * FROM staff WHERE s_id=%s", (id,))
    staff = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        role = request.form['role']

        cursor.execute("""
            UPDATE staff 
            SET s_name=%s, s_email=%s, s_phone=%s, s_role=%s
            WHERE s_id=%s
        """, (name, email, phone, role, id))

        conn.commit()
        flash("Staff updated successfully")
        return redirect(url_for('view_staff'))

    return render_template("edit_staff.html", staff=staff)

# ================= DELETE STAFF =================
@app.route('/delete_staff/<int:id>')
def delete_staff(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE s_id=%s", (id,))
    conn.commit()
    flash("Staff deleted successfully")
    return redirect(url_for('view_staff'))

# ================= ADMIN DASHBOARD =================
@app.route('/admin_dashboard')
def admin_dashboard():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor()

    # Menu
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()

    # Orders
    cursor.execute("""
    SELECT b.id,
           u.name AS user_name,
           m.name AS dish_name,
           m.price,
           b.status,
           b.booking_date
    FROM bookings b
    JOIN users u ON b.user_id = u.id
    JOIN menu m ON b.menu_id = m.id
    ORDER BY b.id DESC
    """)
    orders = cursor.fetchall()

    # Messages
    cursor.execute("SELECT * FROM contact_messages ORDER BY id DESC")
    messages = cursor.fetchall()

    # ✅ COUNTS FIXED
    cursor.execute("SELECT COUNT(*) AS total FROM staff")
    staff_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM users")
    users_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM bookings")
    orders_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM menu")
    menu_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM ratings")
    rating_count = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM contact_messages")
    contact_count = cursor.fetchone()['total']

    return render_template(
        "admin_dashboard.html",
        menu_items=menu_items,
        orders=orders,
        messages=messages,
        staff_count=staff_count,
        users_count=users_count,
        orders_count=orders_count,
        menu_count=menu_count,
        rating_count=rating_count,
        contact_count=contact_count
    )
# ================= VIEW ORDERS =================
@app.route('/view_orders')
def view_orders():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT 
            b.id,
            u.name AS user_name,
            u.email,
            m.name AS dish,
            m.price,
            b.quantity,
            b.status,
            b.booking_date,
            s.s_name AS delivery_name   -- ✅ NEW
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN menu m ON b.menu_id = m.id
        LEFT JOIN staff s ON b.assigned_to = s.s_id   -- ✅ NEW
        ORDER BY b.id ASC
    """)

    orders = cursor.fetchall()

    # Fetch delivery staffs
    cursor.execute("SELECT s_id AS id, s_name AS name FROM staff WHERE s_role='Delivery Staff'")
    delivery_boys = cursor.fetchall()

    return render_template("view_orders.html", orders=orders, delivery_boys=delivery_boys)

# ================= UPDATE STATUS =================
@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):

    if 'admin_id' not in session and 'staff_id' not in session:
        flash("Unauthorized access")
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 🔥 Get current status + assigned delivery
    cursor.execute("SELECT status, assigned_to FROM bookings WHERE id=%s", (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("Order not found")
        return redirect(request.referrer)

    current_status = order['status']
    assigned_to = order['assigned_to']
    new_status = request.form['status']

    # 🔴 LOCK
    if current_status in ['Delivered', 'Rejected']:
        flash("Order locked! Cannot update.")
        return redirect(request.referrer)

    # 🔴 FLOW CONTROL
    if current_status == 'Accepted' and new_status == 'Pending':
        flash("❌ Accepted → Pending not allowed")
        return redirect(request.referrer)

    if current_status == 'Out for Delivery' and new_status in ['Pending', 'Accepted']:
        flash("❌ Invalid status change!")
        return redirect(request.referrer)

    # 🔥 NEW RULE (IMPORTANT)
    # ❌ Don't allow Out for Delivery if delivery not assigned
    if new_status == 'Out for Delivery' and not assigned_to:
        flash("⚠ Please assign delivery staff first")
        return redirect(request.referrer)

    # ✅ UPDATE
    # ADMIN
    if 'admin_id' in session:
        cursor.execute(
            "UPDATE bookings SET status=%s WHERE id=%s",
            (new_status, order_id)
        )

    # STAFF
    elif 'staff_id' in session:
        cursor.execute("""
            UPDATE bookings 
            SET status=%s 
            WHERE id=%s AND assigned_to=%s
        """, (new_status, order_id, session['staff_id']))

    conn.commit()
    conn.ping(reconnect=True)

    flash("Status updated successfully")
    return redirect(request.referrer)

# ================= ASSIGN DELIVERY =================
@app.route('/assign_delivery/<int:order_id>', methods=['POST'])
def assign_delivery(order_id):

    if 'admin_id' not in session:
        flash("Only admin allowed")
        return redirect(url_for('admin_login'))

    delivery_boy_id = request.form['delivery_boy_id']

    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET assigned_to=%s WHERE id=%s", (delivery_boy_id, order_id))
    conn.commit()

    flash("Delivery Staff assigned successfully")
    return redirect(url_for('view_orders'))

# ================= ACCEPT / REJECT / CANCEL =================
@app.route('/accept_order/<int:order_id>')
def accept_order(order_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status='Accepted' WHERE id=%s", (order_id,))
    conn.commit()
    flash("Order accepted successfully")
    return redirect(url_for('view_orders'))

@app.route('/reject_order/<int:order_id>')
def reject_order(order_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status='Rejected' WHERE id=%s", (order_id,))
    conn.commit()
    flash("Order rejected successfully")
    return redirect(url_for('view_orders'))

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):

    if 'user_id' not in session and 'admin_id' not in session:
        flash("Please login first")
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 🔍 Check order status
    cursor.execute("SELECT status, user_id FROM bookings WHERE id=%s", (order_id,))
    order = cursor.fetchone()

    if not order:
        flash("Order not found")
        return redirect(request.referrer)

    # ❌ Accepted ke baad cancel nahi hoga
    if order['status'] in ['Accepted', 'Out for Delivery', 'Delivered']:
        flash("❌ Cannot cancel after order is accepted")
        return redirect(request.referrer)

    try:
        # ✅ ADMIN → delete any order
        if 'admin_id' in session:
            cursor.execute("DELETE FROM bookings WHERE id=%s", (order_id,))

        # ✅ USER → only own order delete
        elif 'user_id' in session:
            cursor.execute(
                "DELETE FROM bookings WHERE id=%s AND user_id=%s",
                (order_id, session['user_id'])
            )

        conn.commit()
        flash("Order cancelled successfully")

    except Exception as e:
        print("Error deleting order:", e)
        flash("Something went wrong while deleting order")

    # 🔁 Redirect
    if 'admin_id' in session:
        return redirect(url_for('view_orders'))
    else:
        return redirect(url_for('mybookings'))

# ================= USER DASHBOARD =================
@app.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    return render_template("user_dashboard.html", menu=menu)

# ================= MY BOOKINGS =================
@app.route('/mybookings')
def mybookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT 
            b.id,
            m.name AS menu_name,
            m.price AS price,
            b.quantity AS quantity,
            b.status,
            b.booking_date
        FROM bookings b
        JOIN menu m ON b.menu_id = m.id
        WHERE b.user_id = %s
        ORDER BY b.id ASC
    """, (session['user_id'],))
    
    orders = cursor.fetchall()

    return render_template("mybooking.html", orders=orders)


# ================= BOOK ORDER =================
@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    menu_id = request.form.get('menu_id')
    quantity = request.form.get('quantity')   # 👈 NEW LINE

    if not menu_id or not quantity:
        return "Data missing!", 400

    status = 'Pending'
    booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (user_id, menu_id, quantity, booking_date, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (session['user_id'], menu_id, quantity, booking_date, status))
    
    conn.commit()

    return redirect(url_for('mybookings'))

# ================= INVOICE =================
@app.route('/invoice/<int:order_id>')
def invoice(order_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # ✅ Fetch quantity along with other order details
    cursor.execute("""
        SELECT 
            b.id,
            b.status,
            b.booking_date,
            b.quantity,  -- quantity added
            u.name AS user_name,
            u.email AS user_email,
            m.name AS dish_name,
            m.price
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN menu m ON b.menu_id = m.id
        WHERE b.id=%s AND b.user_id=%s
    """, (order_id, session['user_id']))

    order = cursor.fetchone()

    if not order:
        flash("Order not found!")
        return redirect(url_for('mybookings'))

    return render_template("invoice.html", order=order)

# ================= RATE ORDER =================
@app.route('/rate_order/<int:order_id>', methods=['GET','POST'])
def rate_order(order_id):

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
    SELECT b.id, b.menu_id, m.name AS menu_name
    FROM bookings b
    JOIN menu m ON b.menu_id = m.id
    WHERE b.id = %s
""", (order_id,))

    order = cursor.fetchone()

    if request.method == 'POST':
        rate = request.form['rating']
        comment = request.form['feedback']

        cursor.execute("""
    INSERT INTO ratings (user_id, menu_id, rate, comment)
    VALUES (%s,%s,%s,%s)
""", (session['user_id'], order['menu_id'], rate, comment))

        conn.commit()
        flash("Thanks for your feedback!")

        return redirect(url_for('mybookings'))

    return render_template("rate_order.html", order=order)

# ================= ADMIN_LOGIN =================
@app.route('/admin')
def admin():
    return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET','POST'])
def admin_login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        # 🔐 Strong password pattern
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'

        # ❌ Pattern fail
        if not re.match(pattern, password):
            flash("Password must be strong (Uppercase, lowercase, number, special char)")
            return render_template("admin_login.html")

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 🔍 Step 1: Check email
        cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
        admin = cursor.fetchone()

        # ❌ Email not found
        if not admin:
            cursor.execute("SELECT * FROM admin WHERE password=%s", (password,))
            pass_check = cursor.fetchone()

            if not pass_check:
                flash("Email and Password both are incorrect")
            else:
                flash("Email is not valid")

            return render_template("admin_login.html")

        # ❌ Password wrong
        if admin['password'] != password:
            flash("Password is not valid")
            return render_template("admin_login.html")

        # ✅ Success
        session['admin_id'] = admin['id']
        session['admin_name'] = admin['name']

        flash("Admin Login Successful")
        return redirect(url_for('admin_dashboard'))

    return render_template("admin_login.html")


@app.route('/admin_logout')
def admin_logout():

    session.pop('admin_id', None)
    flash("Admin Logged Out")

    return redirect(url_for('admin_login'))

# ================= View Users =================
@app.route('/view_users')
def view_users():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template("view_users.html", users=users)

# ================= VIEW MENU =================
@app.route('/view_menu')
def view_menu():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    return render_template("view_menu.html", menu=menu)

# ================= DELETE MENU =================
@app.route('/delete_menu/<int:id>', methods=['POST'])
def delete_menu(id):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id = %s", (id,))
    conn.commit()

    cursor.close() 

    return redirect(url_for('view_menu'))

# ================= ADD MENU =================
@app.route('/add_menu', methods=['GET', 'POST'])
def add_menu():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        description = request.form['description']  # <-- NEW
        price = request.form['price']

        # Handle image upload
        file = request.files['image']
        filename = ''
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Insert into DB
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu (name, description, price, image) VALUES (%s, %s, %s, %s)",
            (name, description, price, filename)
        )
        conn.commit()

        return redirect(url_for('view_menu'))

    return render_template('add_menu.html')

# ================= EDIT MENU =================
@app.route('/edit_menu/<int:id>', methods=['GET','POST'])
def edit_menu(id):
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch existing menu data
    cursor.execute("SELECT * FROM menu WHERE id=%s", (id,))
    menu = cursor.fetchone()

    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        description = request.form['description']  # <-- NEW
        price = request.form['price']

        # Check if a new image is uploaded
        file = request.files.get('image')

        if file and file.filename != "":
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Update all fields including new image
            cursor.execute(
                "UPDATE menu SET name=%s, description=%s, price=%s, image=%s WHERE id=%s",
                (name, description, price, filename, id)
            )
        else:
            # Update fields without changing image
            cursor.execute(
                "UPDATE menu SET name=%s, description=%s, price=%s WHERE id=%s",
                (name, description, price, id)
            )

        conn.commit()
        return redirect(url_for('view_menu'))

    # Render edit menu page with existing data
    return render_template('edit_menu.html', menu=menu)

# ================= VIEW RATE =================
@app.route('/view_rate')
def view_rate():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, u.name AS user_name, r.rate, r.comment, r.rating_date
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.id ASC
    """)
    ratings = cursor.fetchall()
    return render_template("view_rate.html", ratings=ratings)

# ================= DELETE RATE =================
@app.route('/delete_rating/<int:rating_id>', methods=['POST'])
def delete_rating(rating_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ratings WHERE id=%s", (rating_id,))
    conn.commit()
    flash("Rating deleted successfully")
    return redirect(url_for('view_rate'))

# ===================== Display User Profile =====================
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    # Initialize address fields
    user['house_no'] = user['street'] = user['area'] = user['city'] = user['pincode'] = ''

    if user.get('address'):
        # Expected format: "12, MG Road, Andheri, Mumbai - 400053"
        parts = [p.strip() for p in user['address'].split(',')]
        if len(parts) >= 1: user['house_no'] = parts[0]
        if len(parts) >= 2: user['street'] = parts[1]
        if len(parts) >= 3: user['area'] = parts[2]
        if len(parts) >= 4:
            city_pincode = parts[3]
            if '-' in city_pincode:
                city, pincode = city_pincode.split('-', 1)
                user['city'] = city.strip()
                user['pincode'] = pincode.strip()
            else:
                user['city'] = city_pincode.strip()
                user['pincode'] = ''

    return render_template("user_profile.html", user=user)


# ===================== Update User Profile =====================
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    email = request.form.get('email', '').strip()
    contact = request.form.get('contact', '').strip()
    password = request.form.get('password', '').strip()

    # Fetch separate address fields from form
    house_no = request.form.get('house_no', '').strip()
    street = request.form.get('street', '').strip()
    area = request.form.get('area', '').strip()
    city = request.form.get('city', '').strip()
    pincode = request.form.get('pincode', '').strip()

    # Combine into single address string for DB
    address = f"{house_no}, {street}, {area}, {city} - {pincode}"

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET email=%s, contact=%s, address=%s, password=%s
        WHERE id=%s
    """, (email, contact, address, password, session['user_id']))
    conn.commit()

    flash("✅ Profile updated successfully")
    return redirect(url_for('profile'))

# ================= ADMIN PROFILE =================
@app.route('/admin_profile')
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin WHERE id=%s", (session['admin_id'],))
    admin = cursor.fetchone()

    return render_template("admin_profile.html", admin=admin)

# ================= EDIT ADMIN PROFILE =================
@app.route('/update_admin_profile', methods=['POST'])
def update_admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    email = request.form['email']
    password = request.form['password']

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE admin 
        SET email=%s, password=%s
        WHERE id=%s
    """, (email, password, session['admin_id']))

    conn.commit()

    flash("Admin profile updated successfully")
    return redirect(url_for('admin_profile'))

# ================= DELIVERY DASHBOARD =================
@app.route('/delivery_dashboard')
def delivery_dashboard():

    if 'staff_id' not in session:
        return redirect(url_for('staff_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # check role
    cursor.execute("SELECT * FROM staff WHERE s_id=%s", (session['staff_id'],))
    staff = cursor.fetchone()

    if not staff or staff['s_role'] != 'Delivery Staff':
        flash("Access denied!")
        return redirect(url_for('staff_login'))

    # ✅ FETCH ORDERS WITH PRICE, QUANTITY, FULL ADDRESS, AND CONTACT
    cursor.execute("""
        SELECT 
            b.id,
            u.name AS user_name,
            u.contact AS contact,
            u.address AS address,
            m.name AS dish,
            m.price,                
            b.quantity,
            b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN menu m ON b.menu_id = m.id
        WHERE b.assigned_to = %s
        ORDER BY b.id DESC
    """, (session['staff_id'],))

    orders = cursor.fetchall()

    return render_template("delivery_dashboard.html", orders=orders)

# ================= STAFF LOGIN =================
@app.route('/staff_login', methods=['GET','POST'])
def staff_login():

    if request.method == 'POST':
        email = request.form['email']

        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # ✅ UPDATED ROLE
        cursor.execute("SELECT * FROM staff WHERE s_email=%s AND s_role='Delivery Staff'", (email,))
        staff = cursor.fetchone()

        if staff:
            session['staff_id'] = staff['s_id']
            session['staff_name'] = staff['s_name']

            flash("Login successful")
            return redirect(url_for('delivery_dashboard'))
        else:
            flash("Only delivery staff can login!")

    return render_template("staff_login.html")

# ================= STAFF LOGOUT =================
@app.route('/staff_logout')
def staff_logout():
    session.pop('staff_id', None)
    session.pop('staff_name', None)
    flash("Logged out successfully")
    return redirect(url_for('staff_login'))

# ================= USER REPORT =================
@app.route('/user_report', methods=['GET','POST'])
def user_report():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = "SELECT * FROM users WHERE 1=1"
    params = []

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if start_date:
            query += " AND DATE(created_at) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(created_at) <= %s"
            params.append(end_date)

    cursor.execute(query, params)
    users = cursor.fetchall()

    return render_template("user_report.html", users=users)

# ================= ORDER REPORT =================
@app.route('/order_report', methods=['GET','POST'])
def order_report():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Base query
    query = """
        SELECT b.id, u.name AS user_name, m.name AS dish,
               m.price, b.quantity, b.status, b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN menu m ON b.menu_id = m.id
        WHERE 1=1
    """

    params = []

    # 🔍 FILTER LOGIC
    if request.method == 'POST':
        start = request.form.get('start_date')
        end = request.form.get('end_date')
        status = request.form.get('status')

        # Date filter
        if start and end:
            query += " AND DATE(b.booking_date) BETWEEN %s AND %s"
            params.extend([start, end])

        # Status filter
        if status:
            query += " AND b.status = %s"
            params.append(status)

    # Execute query
    cursor.execute(query, params)
    orders = cursor.fetchall()

    return render_template("booking_report.html", orders=orders)


# ================= FEEDBACK REPORT =================
@app.route('/feedback_report', methods=['GET','POST'])
def feedback_report():

    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT id, name, email, contact, message, date_posted
        FROM contact_messages
        WHERE 1=1
    """
    params = []

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if start_date:
            query += " AND DATE(date_posted) >= %s"
            params.append(start_date)

        if end_date:
            query += " AND DATE(date_posted) <= %s"
            params.append(end_date)

    cursor.execute(query, params)
    messages = cursor.fetchall()

    return render_template("feedback_report.html", messages=messages)

# ================= RUN SERVER =================
if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        port=int(os.environ.get("PORT", "5500"))
    )