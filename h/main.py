from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy, SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Gon20557@localhost/final180'
db = SQLAlchemy(app)
app.secret_key = 'shhhh'


class Product(db.Model):
    ProductID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    warranty = db.Column(db.Integer, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    sizes = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)



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
                'image': "path_to_default_image.jpg"
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/edit-product/<int:product_id>', methods=['POST'])
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
    if 'logged_in' in session and session.get('user_type') == 'admin':
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
            return redirect(url_for('home'))
        elif admin_user and admin_user.password == password:
            session['logged_in'] = True
            session['user_type'] = 'admin'  # Set user type as admin
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
    # cart functionality here
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    # checkout functionality here
    return render_template('checkout.html')


@app.route('/vendors')
def vendors():
    return render_template('vendors.html')


@app.route('/login/vendors', methods=['GET', 'POST'])
def vendorlog():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        vendorid_or_username = request.form['email']
        password = request.form['password']
        vendors = (vendor.query.filter((vendor.vendorid == vendorid_or_username) | (vendor.username == vendorid_or_username)).first())

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
        new_product = product(title=title, price=price, img=img, warranty=warranty, description=description, sizes=sizes)
        db.session.add(new_product)
        try:
            db.session.commit()
            return redirect(url_for('product_list'))
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)
    else:
        return "Unauthorized", 403

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
