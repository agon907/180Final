from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')  # New route for the login page
def login():
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

if __name__ == '__main__':
    app.run(debug=True)
