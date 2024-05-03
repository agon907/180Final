from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/final180'
db = SQLAlchemy(app)
app.secret_key = 'shhhh'


class customer(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    firstname = db.Column(db.Text)
    lastname = db.Column(db.Text)
    email = db.Column(db.Text)
    password = db.Column(db.Text)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['get', 'post'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']
        existing_email = customer.query.filter_by(email=email).first()
        existing_user = customer.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username taken'
            return render_template('signup.html', error=error)
        if existing_email:
            error = 'Email linked to an existing account'
            return render_template('signup.html', error=error)
        new_user = customer(username=username, firstname=firstname, lastname=lastname, password=password, email=email)
        db.session.add(new_user)
        try:
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return "Error: " + str(e)
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])  # New route for the login page
def login():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email_or_username = request.form['email']
        password = request.form['password']
        user = customer.query.filter((customer.email == email_or_username) | (customer.username == email_or_username)).first()

        if user and user.password == password:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/products')
def product_list():
    # products from the database here
    products = []
    return render_template('products.html', products=products)


@app.route('/cart')
def cart():
    # cart functionality here
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    # checkout functionality here
    return render_template('checkout.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('login')


if __name__ == '__main__':
    app.run(debug=True)
