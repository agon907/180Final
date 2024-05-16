from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/final180'
db = SQLAlchemy(app)
app.secret_key = 'shhhh'


class shopping_cart(db.Model):
    productid = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Text, default=1)
    userid = db.Column(db.Text)
    cartid = db.Column(db.Text)


class Product(db.Model):
    ProductID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    warranty = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    sizes = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    img = db.Column(db.Text)


class customer(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True,)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    role = db.Column(db.String(50), default='customer')


class admin(db.Model):
    AdminID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    password = db.Column(db.Text)


@app.route('/admin/add-product', methods=['POST'])
def add_product():
    try:
        new_product = Product(
            title=request.form['title'],
            description=request.form['description'],
            warranty=int(request.form['warranty']),
            colors=request.form['colors'],
            sizes=request.form['sizes'],
            img=request.form['img'],
            price=float(request.form['price'])
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify({
            'success': True,
            'product': {
                'ProductID': new_product.ProductID,
                'title': new_product.title,
                'description': new_product.description,
                'price': new_product.price,
                'image': new_product.img
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/edit-product'
           '/<int:product_id>', methods=['POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        product.title = request.form['title']
        product.description = request.form['description']
        product.warranty = int(request.form['warranty'])
        product.colors = request.form['colors']
        product.sizes = request.form['sizes']
        product.price = float(request.form['price'])
        db.session.commit()
        return jsonify({'success': True, 'message': 'Product updated successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/admin/product-details/<int:product_id>', methods=['GET'])
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    product_data = {
        'ProductID': product.ProductID,
        'title': product.title,
        'description': product.description,
        'warranty': product.warranty,
        'colors': product.colors,
        'sizes': product.sizes,
        'price': product.price
    }
    return jsonify(product_data)


@app.route('/products/data')
def products_data():
    products = Product.query.all()
    products_list = [{
        'ProductID': product.ProductID,
        'title': product.title,
        'description': product.description,
        'price': float(product.price),
        'warranty': product.warranty,
        'colors': product.colors,
        'sizes': product.sizes
    } for product in products]
    return jsonify(products_list)


@app.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'logged_in' in session and session.get('username') == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('login'))


class vendor(db.Model):
    VendorID = db.Column(db.Text, unique=True, primary_key=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']

        if role == 'admin':
            existing_admin = admin.query.filter_by(username=username).first()
            if existing_admin:
                error = 'Username taken'
                return render_template('signup.html', error=error)
            new_admin = admin(username=username, firstname=firstname, lastname=lastname, password=password)
            db.session.add(new_admin)
        else:
            email = request.form['email']
            existing_customer_username = customer.query.filter_by(username=username).first()
            existing_customer_email = customer.query.filter_by(email=email).first()
            if existing_customer_username:
                error = 'Username taken'
                return render_template('signup.html', error=error)
            if existing_customer_email:
                error = 'Email linked to an existing account'
                return render_template('signup.html', error=error)
            new_customer = customer(username=username, firstname=firstname, lastname=lastname, password=password,
                                    email=email)
            db.session.add(new_customer)

        try:
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']
        customer_user = customer.query.filter(
            (customer.email == email_or_username) | (customer.username == email_or_username)
        ).first()
        admin_user = admin.query.filter_by(username=email_or_username).first()
        if customer_user and customer_user.password == password:
            session['logged_in'] = True
            session['username'] = 'customer'
            session['user_id'] = customer_user.UserID  # Set user ID in session
            return redirect(url_for('home'))
        elif admin_user and admin_user.password == password:
            session['logged_in'] = True
            session['username'] = 'admin'  # Set user type as admin
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route('/products')
def product_list():
    # products from the database here
    products = Product.query.all()
    return render_template('products.html', products=products)


@app.route('/cart')
def cart():
    if 'logged_in' in session:
        if session['username'] == 'customer':
            user_id = session['user_id']
            cart_items = shopping_cart.query.filter_by(userid=user_id).all()

            cart_details = []
            subtotal = 0
            for item in cart_items:
                product = Product.query.get(item.productid)
                item_total = product.price * int(item.quantity)
                subtotal += item_total
                cart_details.append({
                    'product_id': item.productid,
                    'title': product.title,
                    'price': product.price,
                    'quantity': item.quantity,
                    'subtotal': item_total
                })

            tax = round(subtotal * 0.06, 2)
            shipping_cost = 4
            total_price = subtotal + tax + shipping_cost

            return render_template('cart.html', cart_details=cart_details, total_price=total_price, tax=tax, shipping_cost=shipping_cost, subtotal=subtotal)
        elif session['username'] == 'admin':
            return redirect(url_for('admin_dashboard'))  # Redirect admins to the admin dashboard
    else:
        flash('Please log in to view your cart.', 'error')
        return redirect(url_for('login'))



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'logged_in' in session and session['username'] == 'customer':
        product_id = request.form['product_id']
        user_id = session['user_id']

        existing_item = shopping_cart.query.filter_by(productid=product_id, userid=user_id).first()
        if existing_item:
            existing_item.quantity = int(existing_item.quantity) + 1
        else:
            new_item = shopping_cart(productid=product_id, userid=user_id)
            db.session.add(new_item)

        db.session.commit()
        flash('Item added to cart successfully.', 'success')
        return redirect(url_for('product_list'))
    else:
        flash('Please login to add items to your cart.', 'error')
        return redirect(url_for('login'))


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'logged_in' in session and session['username'] == 'customer':
        user_id = session['user_id']
        item_to_remove = shopping_cart.query.filter_by(userid=user_id, productid=product_id).first()
        if item_to_remove:
            item_to_remove.quantity = int(item_to_remove.quantity)
            if item_to_remove.quantity > 1:
                item_to_remove.quantity -= 1
                item_to_remove.quantity = str(item_to_remove.quantity)
            else:
                db.session.delete(item_to_remove)
            db.session.commit()
            flash('Item removed from cart successfully.', 'success')
        else:
            flash('Item not found in cart.', 'error')
    else:
        flash('Please log in to perform this action.', 'error')
    return redirect(url_for('cart'))



@app.route('/checkout', methods=['POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/receipt', methods=['GET', 'POST'])
def receipt():
    current_date = datetime.now().strftime('%Y-%m-%d')

    user_id = session['user_id']
    cart_items = shopping_cart.query.filter_by(userid=user_id).all()
    receipt_data = []
    for item in cart_items:
        product = Product.query.get(item.productid)
        receipt_data.append({
            'title': product.title,
            'price': product.price,
            'quantity': item.quantity,
            'subtotal': product.price * int(item.quantity)
        })

    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    return render_template('receipt.html', receipt_data=receipt_data, current_date=current_date)


@app.route('/vendors')
def vendors():
    return render_template('vendors.html')


@app.route('/login/vendors', methods=['GET', 'POST'])
def vendorlog():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        VendorID_or_username = request.form['email']
        password = request.form['password']
        vendors = (vendor.query.filter((vendor.VendorID == VendorID_or_username) | (vendor.username == VendorID_or_username)).first())

        if vendors and vendors.password == password:
            session['logged_in'] = True
            session['username'] = 'vendor'
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/vendors/add', methods=['POST'])
def add_vendor_product():
    if session.get('username') == 'vendor':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']
        warranty = request.form['warranty']
        img = request.form['img']
        sizes = request.form['sizes']
        new_product = Product(title=title, price=price, img=img, warranty=warranty, description=description, sizes=sizes)
        db.session.add(new_product)
        try:
            db.session.commit()
            return redirect(url_for('product_list'))
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)
    else:
        return "Unauthorized"


@app.route('/vendors/remove/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    if session.get('username') == 'vendor':
        remove = Product.query.get(product_id)
        if remove:
            db.session.delete(remove)
            try:
                db.session.commit()
                return redirect(url_for('product_list'))
            except Exception as e:
                db.session.rollback()
                return "Error: " + str(e)
        else:
            return "Product not found"
    else:
        return "Unauthorized"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('login')


@app.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        products = Product.query.filter(Product.title.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()
    return render_template('products.html', products=products)


if __name__ == '__main__':
    app.run(debug=True)
    print(session)
