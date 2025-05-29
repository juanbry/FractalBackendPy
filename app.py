from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os

from models import db, Product, Order, OrderProduct

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://fractal_db_aigs_user:BMpWDLHWYmE3Xg8u7VsAZlYtFK5pa4mL@dpg-d0rk7rruibrs73dap6g0-a.oregon-postgres.render.com/fractal_db_aigs')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.context_processor
def inject_datetime():
    return {'datetime': datetime}

@app.route('/')
def index():
    return redirect(url_for('my_orders'))

@app.route('/my-orders')
def my_orders():
    orders = Order.query.all()
    return render_template('my_orders.html', orders=orders)

@app.route('/add-order')
@app.route('/add-order/<int:order_id>')
def add_order(order_id=None):
    order = None
    order_products = []
    products = Product.query.all()
    
    if order_id:
        order = Order.query.get_or_404(order_id)
        order_products = OrderProduct.query.filter_by(order_id=order_id).all()
    
    return render_template('add_order.html', order=order, order_products=order_products, products=products)

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/save-order', methods=['POST'])
def save_order():
    order_id = request.form.get('order_id')
    order_number = request.form.get('order_number')
    
    if order_id:
        order = Order.query.get_or_404(order_id)
        if order.status == 'Completed':
            flash('Cannot edit completed orders')
            return redirect(url_for('my_orders'))
        order.order_number = order_number
        db.session.commit()
        return redirect(url_for('my_orders'))
    else:
        order = Order(order_number=order_number)
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('add_order', order_id=order.id))

@app.route('/delete-order/<int:order_id>')
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    OrderProduct.query.filter_by(order_id=order_id).delete()
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('my_orders'))

@app.route('/add-product-to-order', methods=['POST'])
def add_product_to_order():
    order_id = request.form.get('order_id')
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    
    order = Order.query.get_or_404(order_id)
    if order.status == 'Completed':
        return jsonify({'error': 'Cannot modify completed orders'})
    
    product = Product.query.get_or_404(product_id)
    total_price = product.unit_price * quantity
    
    existing = OrderProduct.query.filter_by(order_id=order_id, product_id=product_id).first()
    if existing:
        existing.quantity = quantity
        existing.total_price = total_price
    else:
        order_product = OrderProduct(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(order_product)
    
    update_order_totals(order_id)
    db.session.commit()
    
    return redirect(url_for('add_order', order_id=order_id))

@app.route('/remove-product-from-order/<int:order_product_id>')
def remove_product_from_order(order_product_id):
    order_product = OrderProduct.query.get_or_404(order_product_id)
    order_id = order_product.order_id
    
    order = Order.query.get_or_404(order_id)
    if order.status == 'Completed':
        flash('Cannot modify completed orders')
        return redirect(url_for('add_order', order_id=order_id))
    
    db.session.delete(order_product)
    update_order_totals(order_id)
    db.session.commit()
    
    return redirect(url_for('add_order', order_id=order_id))

@app.route('/change-order-status/<int:order_id>/<status>')
def change_order_status(order_id, status):
    order = Order.query.get_or_404(order_id)
    if status in ['Pending', 'InProgress', 'Completed']:
        order.status = status
        db.session.commit()
    return redirect(url_for('my_orders'))

@app.route('/add-product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    unit_price = float(request.form.get('unit_price'))
    
    product = Product(name=name, unit_price=unit_price)
    db.session.add(product)
    db.session.commit()
    
    return redirect(url_for('products'))

@app.route('/delete-product/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

def update_order_totals(order_id):
    order = Order.query.get(order_id)
    order_products = OrderProduct.query.filter_by(order_id=order_id).all()
    
    order.final_price = sum(op.total_price for op in order_products)

def init_db():
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            products = [
                Product(name='Chocolate', unit_price=8.5),
                Product(name='Leche Gloria', unit_price=5.5),
                Product(name='Avena 3 Ositos', unit_price=2.5),
                Product(name='Jugo Liber', unit_price=1.5)
            ]
            for product in products:
                db.session.add(product)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por Render
    app.run(host="0.0.0.0", port=port, debug=True)
