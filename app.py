from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, Product, Sale, SaleItem
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    total_products = Product.query.count()
    total_sales = Sale.query.count()
    low_stock_products = Product.query.filter(Product.stock_quantity < 10).count()
    
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(5).all()
    total_revenue = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
    
    return render_template('index.html', 
                         total_products=total_products,
                         total_sales=total_sales,
                         low_stock_products=low_stock_products,
                         recent_sales=recent_sales,
                         total_revenue=total_revenue)

@app.route('/inventory')
def inventory():
    products = Product.query.order_by(Product.name).all()
    return render_template('inventory.html', products=products)

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=float(data['price']),
        stock_quantity=int(data['stock_quantity'])
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data['name']
    product.description = data.get('description', '')
    product.price = float(data['price'])
    product.stock_quantity = int(data['stock_quantity'])
    
    db.session.commit()
    
    return jsonify(product.to_dict())

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/sales')
def sales():
    products = Product.query.filter(Product.stock_quantity > 0).order_by(Product.name).all()
    return render_template('sales.html', products=products)

@app.route('/api/sales', methods=['POST'])
def process_sale():
    data = request.get_json()
    items = data.get('items', [])
    
    if not items:
        return jsonify({'error': 'No items in sale'}), 400
    
    total_amount = 0
    sale_items = []
    
    for item in items:
        product = Product.query.get(item['product_id'])
        if not product:
            return jsonify({'error': f'Product {item["product_id"]} not found'}), 404
        
        quantity = int(item['quantity'])
        if product.stock_quantity < quantity:
            return jsonify({'error': f'Insufficient stock for {product.name}'}), 400
        
        product.stock_quantity -= quantity
        subtotal = product.price * quantity
        total_amount += subtotal
        
        sale_item = SaleItem(
            product_id=product.id,
            quantity=quantity,
            price_at_sale=product.price
        )
        sale_items.append(sale_item)
    
    sale = Sale(total_amount=total_amount)
    db.session.add(sale)
    db.session.flush()
    
    for sale_item in sale_items:
        sale_item.sale_id = sale.id
        db.session.add(sale_item)
    
    db.session.commit()
    
    return jsonify(sale.to_dict()), 201

@app.route('/history')
def history():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('history.html', sales=sales)

@app.route('/api/sales', methods=['GET'])
def get_sales():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return jsonify([sale.to_dict() for sale in sales])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
