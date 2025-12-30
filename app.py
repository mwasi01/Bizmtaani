from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import csv
import io
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# For Render, we'll use a relative path in the file system
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'business_data.json')

def load_data():
    """Load business data from JSON file"""
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                data = validate_data(data)
                return data
        else:
            # Create default data file
            default_data = get_default_data()
            save_data(default_data)
            return default_data
    except Exception as e:
        print(f"Error loading data: {e}")
        return get_default_data()

def get_default_data():
    """Return default data structure"""
    return {
        "products": [
            {"id": 1, "name": "250ltrs open plastic Drum", "price": 2900, "stock": 10, 
             "cost": 2000, "category": "Drums", "supplier": "Plastic Works Ltd", 
             "min_stock": 2, "max_stock": 50, "barcode": "DRUM250OP", "unit": "piece",
             "sku": "DRUM-001", "description": "High-quality 250-liter open plastic drum",
             "status": "active", "last_updated": datetime.now().isoformat()},
            {"id": 2, "name": "250lts close Drum", "price": 3000, "stock": 8, 
             "cost": 2100, "category": "Drums", "supplier": "Plastic Works Ltd",
             "min_stock": 2, "max_stock": 40, "barcode": "DRUM250CL", "unit": "piece",
             "sku": "DRUM-002", "description": "250-liter closed plastic drum",
             "status": "active", "last_updated": datetime.now().isoformat()},
            {"id": 3, "name": "170lts Drum", "price": 2200, "stock": 15, 
             "cost": 1500, "category": "Drums", "supplier": "Container Solutions",
             "min_stock": 3, "max_stock": 60, "barcode": "DRUM170", "unit": "piece",
             "sku": "DRUM-003", "description": "170-liter plastic drum",
             "status": "active", "last_updated": datetime.now().isoformat()},
            {"id": 4, "name": "120lts Plastic Drum", "price": 1500, "stock": 12, 
             "cost": 1000, "category": "Drums", "supplier": "Container Solutions",
             "min_stock": 5, "max_stock": 80, "barcode": "DRUM120", "unit": "piece",
             "sku": "DRUM-004", "description": "120-liter plastic drum",
             "status": "active", "last_updated": datetime.now().isoformat()},
            {"id": 5, "name": "80lts Plastic Drum", "price": 1000, "stock": 20, 
             "cost": 700, "category": "Drums", "supplier": "Plastic Works Ltd",
             "min_stock": 5, "max_stock": 100, "barcode": "DRUM80", "unit": "piece",
             "sku": "DRUM-005", "description": "80-liter plastic drum",
             "status": "active", "last_updated": datetime.now().isoformat()}
        ],
        "transactions": [
            {"id": 1, "date": "2024-01-15 10:30:00", "type": "sale", 
             "amount": 5800, "customer": "John Doe", 
             "items": [{"name": "250ltrs open plastic Drum", "quantity": 2, "price": 2900}],
             "description": "2 drums sale", "payment_method": "M-Pesa", "status": "completed"},
            {"id": 2, "date": "2024-01-16 14:20:00", "type": "purchase", 
             "amount": 4200, "supplier": "Plastic Works Ltd", 
             "description": "Restock drums", "payment_method": "Bank Transfer", "status": "completed"},
            {"id": 3, "date": "2024-01-17 09:15:00", "type": "sale", 
             "amount": 2200, "customer": "Jane Smith", 
             "items": [{"name": "170lts Drum", "quantity": 1, "price": 2200}],
             "description": "Single drum sale", "payment_method": "Cash", "status": "completed"},
            {"id": 4, "date": "2024-01-18 11:45:00", "type": "refund", 
             "amount": 1500, "customer": "John Doe", 
             "description": "Returned damaged drum", "payment_method": "M-Pesa", "status": "completed"},
            {"id": 5, "date": "2024-01-19 16:30:00", "type": "expense", 
             "amount": 5000, "supplier": "Office Supplies Ltd", 
             "description": "Office rent", "payment_method": "Bank Transfer", "status": "completed"}
        ],
        "customers": [
            {"id": 1, "name": "John Doe", "contact": "0712345678", 
             "email": "john@example.com", "total_spent": 5800, "total_orders": 12,
             "last_order": "2024-01-15", "type": "VIP", "address": "123 Main St, Nairobi",
             "city": "Nairobi", "country": "Kenya", "status": "active", 
             "join_date": "2023-05-10"},
            {"id": 2, "name": "Jane Smith", "contact": "0723456789", 
             "email": "jane@example.com", "total_spent": 2200, "total_orders": 5,
             "last_order": "2024-01-17", "type": "Regular", "address": "456 Park Ave, Mombasa",
             "city": "Mombasa", "country": "Kenya", "status": "active", 
             "join_date": "2023-08-22"},
            {"id": 3, "name": "Tech Solutions Ltd", "contact": "0734567890", 
             "email": "info@techsolutions.co.ke", "total_spent": 320000, "total_orders": 8,
             "last_order": "2024-01-12", "type": "Corporate", "address": "789 Business Park, Nairobi",
             "city": "Nairobi", "country": "Kenya", "status": "active", 
             "join_date": "2023-03-15"},
            {"id": 4, "name": "Maria Garcia", "contact": "0745678901", 
             "email": "maria@example.com", "total_spent": 75000, "total_orders": 3,
             "last_order": "2023-12-05", "type": "Wholesale", "address": "101 Market St, Kisumu",
             "city": "Kisumu", "country": "Kenya", "status": "inactive", 
             "join_date": "2023-10-01"},
            {"id": 5, "name": "Robert Kimani", "contact": "0756789012", 
             "email": "robert@example.com", "total_spent": 189000, "total_orders": 7,
             "last_order": "2024-01-14", "type": "Regular", "address": "202 River Rd, Nairobi",
             "city": "Nairobi", "country": "Kenya", "status": "active", 
             "join_date": "2023-07-18"}
        ],
        "suppliers": [
            {"id": 1, "name": "Plastic Works Ltd", "contact": "David Wangari", 
             "email": "david@plasticworks.co.ke", "phone": "0711223344",
             "products": ["250ltrs open plastic Drum", "250lts close Drum", "80lts Plastic Drum"],
             "status": "active", "address": "Industrial Area, Nairobi"},
            {"id": 2, "name": "Container Solutions", "contact": "Susan Atieno", 
             "email": "susan@containers.co.ke", "phone": "0722334455",
             "products": ["170lts Drum", "120lts Plastic Drum"],
             "status": "active", "address": "Mombasa Road, Nairobi"},
            {"id": 3, "name": "Office Supplies Ltd", "contact": "James Omondi", 
             "email": "james@officesupplies.co.ke", "phone": "0733445566",
             "products": ["Office Furniture", "Stationery"],
             "status": "active", "address": "Westlands, Nairobi"}
        ],
        "notes": [
            {"id": "1", "title": "Meeting with Plastic Works Ltd", 
             "content": "Discuss new product line and pricing for Q2 2024", 
             "category": "Meeting", "priority": "high", 
             "created_at": "2024-01-10T09:00:00", "updated_at": "2024-01-10T09:00:00"},
            {"id": "2", "title": "Inventory Audit", 
             "content": "Need to conduct physical inventory count by end of month", 
             "category": "Task", "priority": "medium", 
             "created_at": "2024-01-08T14:30:00", "updated_at": "2024-01-08T14:30:00"},
            {"id": "3", "title": "Marketing Campaign", 
             "content": "Plan for social media campaign targeting corporate clients", 
             "category": "Idea", "priority": "low", 
             "created_at": "2024-01-05T11:15:00", "updated_at": "2024-01-05T11:15:00"}
        ],
        "settings": {"tax_rate": 16.0, "currency": "KES", "company_name": "Business Suite Pro"}
    }

def validate_data(data):
    """Validate and fix data structure"""
    required_keys = ["products", "transactions", "customers", "suppliers", "notes", "settings"]
    for key in required_keys:
        if key not in data:
            default_data = get_default_data()
            data[key] = default_data[key] if key in default_data else []
    
    # Validate products
    for product in data["products"]:
        product.setdefault("price", 0)
        product.setdefault("stock", 0)
        product.setdefault("cost", 0)
        product.setdefault("category", "")
        product.setdefault("supplier", "")
        product.setdefault("min_stock", 5)
        product.setdefault("max_stock", 100)
        product.setdefault("sku", "")
        product.setdefault("description", "")
        product.setdefault("status", "active")
        product.setdefault("last_updated", datetime.now().isoformat())
        
        numeric_fields = ["price", "stock", "cost", "min_stock", "max_stock"]
        for field in numeric_fields:
            if field in product and isinstance(product[field], str):
                try:
                    if field == "stock":
                        product[field] = int(float(product[field]))
                    else:
                        product[field] = float(product[field])
                except:
                    product[field] = 0
    
    # Validate customers
    for customer in data["customers"]:
        customer.setdefault("total_spent", 0)
        customer.setdefault("total_orders", 0)
        customer.setdefault("last_order", "")
        customer.setdefault("type", "Regular")
        customer.setdefault("address", "")
        customer.setdefault("city", "")
        customer.setdefault("country", "Kenya")
        customer.setdefault("status", "active")
        customer.setdefault("join_date", datetime.now().strftime("%Y-%m-%d"))
        
        if isinstance(customer.get("total_spent"), str):
            try:
                customer["total_spent"] = float(customer["total_spent"])
            except:
                customer["total_spent"] = 0
        
        if isinstance(customer.get("total_orders"), str):
            try:
                customer["total_orders"] = int(customer["total_orders"])
            except:
                customer["total_orders"] = 0
    
    # Validate transactions
    for transaction in data["transactions"]:
        transaction.setdefault("amount", 0)
        transaction.setdefault("customer", "")
        transaction.setdefault("supplier", "")
        transaction.setdefault("description", "")
        transaction.setdefault("items", [])
        transaction.setdefault("payment_method", "Cash")
        transaction.setdefault("status", "completed")
        
        if isinstance(transaction.get("amount"), str):
            try:
                transaction["amount"] = float(transaction["amount"])
            except:
                transaction["amount"] = 0
    
    # Validate suppliers
    for supplier in data["suppliers"]:
        supplier.setdefault("products", [])
        supplier.setdefault("status", "active")
        supplier.setdefault("address", "")
        supplier.setdefault("phone", "")
    
    # Validate notes
    for note in data["notes"]:
        note.setdefault("category", "General")
        note.setdefault("priority", "medium")
        note.setdefault("created_at", datetime.now().isoformat())
        note.setdefault("updated_at", datetime.now().isoformat())
    
    return data

def save_data(data):
    """Save business data to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Products API
@app.route('/api/products', methods=['GET'])
def get_products():
    data = load_data()
    return jsonify(data['products'])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = load_data()
    product = request.json
    
    product.setdefault("price", 0)
    product.setdefault("stock", 0)
    product.setdefault("cost", 0)
    product.setdefault("category", "")
    product.setdefault("supplier", "")
    product.setdefault("min_stock", 5)
    product.setdefault("max_stock", 100)
    product.setdefault("sku", f"PROD-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    product.setdefault("description", "")
    product.setdefault("status", "active")
    
    numeric_fields = ["price", "stock", "cost", "min_stock", "max_stock"]
    for field in numeric_fields:
        if field in product and isinstance(product[field], str):
            try:
                if field == "stock":
                    product[field] = int(float(product[field]))
                else:
                    product[field] = float(product[field])
            except:
                product[field] = 0
    
    product['id'] = max([p['id'] for p in data['products']], default=0) + 1
    product['last_updated'] = datetime.now().isoformat()
    data['products'].append(product)
    save_data(data)
    return jsonify(product), 201

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    data = load_data()
    data['products'] = [p for p in data['products'] if p['id'] != product_id]
    save_data(data)
    return jsonify({"message": "Product deleted"}), 200

# Customers API
@app.route('/api/customers', methods=['GET'])
def get_customers():
    data = load_data()
    return jsonify(data['customers'])

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = load_data()
    customer = request.json
    
    customer.setdefault("total_spent", 0)
    customer.setdefault("total_orders", 0)
    customer.setdefault("last_order", "")
    customer.setdefault("type", "Regular")
    customer.setdefault("address", "")
    customer.setdefault("city", "")
    customer.setdefault("country", "Kenya")
    customer.setdefault("status", "active")
    customer.setdefault("join_date", datetime.now().strftime("%Y-%m-%d"))
    
    customer['id'] = max([c['id'] for c in data['customers']], default=0) + 1
    data['customers'].append(customer)
    save_data(data)
    return jsonify(customer), 201

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    data = load_data()
    data['customers'] = [c for c in data['customers'] if c['id'] != customer_id]
    save_data(data)
    return jsonify({"message": "Customer deleted"}), 200

# Transactions API
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    data = load_data()
    return jsonify(data['transactions'])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = load_data()
    transaction = request.json
    
    transaction.setdefault("amount", 0)
    transaction.setdefault("customer", "")
    transaction.setdefault("supplier", "")
    transaction.setdefault("description", "")
    transaction.setdefault("items", [])
    transaction.setdefault("payment_method", "Cash")
    transaction.setdefault("status", "completed")
    
    try:
        transaction["amount"] = float(transaction["amount"])
    except:
        transaction["amount"] = 0
    
    transaction['id'] = max([t['id'] for t in data['transactions']], default=0) + 1
    transaction['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['transactions'].append(transaction)
    save_data(data)
    return jsonify(transaction), 201

# Suppliers API
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    data = load_data()
    return jsonify(data['suppliers'])

# Analytics API
@app.route('/api/analytics/sales')
def get_sales_analytics():
    data = load_data()
    days = int(request.args.get('days', 30))
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    daily_sales = {}
    product_sales = defaultdict(float)
    
    for transaction in data['transactions']:
        if transaction['type'] == 'sale':
            try:
                trans_date = datetime.strptime(transaction['date'], '%Y-%m-%d %H:%M:%S')
                if start_date <= trans_date <= end_date:
                    date_str = trans_date.strftime('%Y-%m-%d')
                    daily_sales[date_str] = daily_sales.get(date_str, 0) + transaction.get('amount', 0)
                    
                    if 'items' in transaction:
                        for item in transaction['items']:
                            quantity = item.get('quantity', 1)
                            price = item.get('price', 0)
                            product_sales[item.get('name', 'Unknown')] += quantity * price
            except:
                continue
    
    dates = []
    sales = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        dates.append(date_str)
        sales.append(daily_sales.get(date_str, 0))
        current_date += timedelta(days=1)
    
    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return jsonify({
        'dates': dates,
        'sales': sales,
        'top_products': top_products,
        'total_sales': sum(sales),
        'avg_daily_sales': sum(sales) / len(sales) if sales else 0
    })

@app.route('/api/analytics/balance')
def get_balance():
    data = load_data()
    
    try:
        income = sum(t.get('amount', 0) for t in data['transactions'] if t.get('type') == 'sale')
        expenses = sum(t.get('amount', 0) for t in data['transactions'] if t.get('type') in ['purchase', 'expense'])
        stock_value = sum(p.get('price', 0) * p.get('stock', 0) for p in data['products'])
        active_customers = len([c for c in data['customers'] if c.get('status') == 'active'])
        gross_profit = income - expenses
        
        return jsonify({
            'income': income,
            'expenses': expenses,
            'stock_value': stock_value,
            'gross_profit': gross_profit,
            'total_customers': len(data['customers']),
            'total_active_customers': active_customers,
            'total_products': len(data['products'])
        })
    except:
        return jsonify({
            'income': 0,
            'expenses': 0,
            'stock_value': 0,
            'gross_profit': 0,
            'total_customers': 0,
            'total_active_customers': 0,
            'total_products': 0
        })

# Notes API
@app.route('/api/notes', methods=['GET'])
def get_notes():
    data = load_data()
    return jsonify(data['notes'])

@app.route('/api/notes', methods=['POST'])
def add_note():
    data = load_data()
    note = request.json
    
    if not note.get('title'):
        return jsonify({"error": "Note title is required"}), 400
    
    note['id'] = str(uuid.uuid4())
    note['created_at'] = datetime.now().isoformat()
    note['updated_at'] = note['created_at']
    note.setdefault('content', '')
    note.setdefault('category', 'General')
    
    data['notes'].append(note)
    save_data(data)
    return jsonify(note), 201

@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    data = load_data()
    data['notes'] = [n for n in data['notes'] if n['id'] != note_id]
    save_data(data)
    return jsonify({"message": "Note deleted"}), 200

# Export API
@app.route('/api/export/csv/<export_type>')
def export_csv(export_type):
    data = load_data()
    
    if export_type == 'products':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'name', 'category', 'price', 'stock', 'cost', 'supplier'])
        writer.writeheader()
        for product in data['products']:
            row = {
                'id': product.get('id', ''),
                'name': product.get('name', ''),
                'category': product.get('category', ''),
                'price': product.get('price', 0),
                'stock': product.get('stock', 0),
                'cost': product.get('cost', 0),
                'supplier': product.get('supplier', '')
            }
            writer.writerow(row)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='products_export.csv'
        )
    
    elif export_type == 'customers':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'name', 'email', 'phone', 'type', 'total_orders', 'total_spent', 'status'])
        writer.writeheader()
        for customer in data['customers']:
            row = {
                'id': customer.get('id', ''),
                'name': customer.get('name', ''),
                'email': customer.get('email', ''),
                'phone': customer.get('contact', ''),
                'type': customer.get('type', 'Regular'),
                'total_orders': customer.get('total_orders', 0),
                'total_spent': customer.get('total_spent', 0),
                'status': customer.get('status', 'active')
            }
            writer.writerow(row)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='customers_export.csv'
        )
    
    elif export_type == 'transactions':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['id', 'date', 'type', 'amount', 'customer', 'supplier', 'description'])
        writer.writeheader()
        for transaction in data['transactions']:
            row = {
                'id': transaction.get('id', ''),
                'date': transaction.get('date', ''),
                'type': transaction.get('type', ''),
                'amount': transaction.get('amount', 0),
                'customer': transaction.get('customer', ''),
                'supplier': transaction.get('supplier', ''),
                'description': transaction.get('description', '')
            }
            writer.writerow(row)
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='transactions_export.csv'
        )
    
    return jsonify({"error": "Invalid export type"}), 400

# Backup API
@app.route('/api/backup')
def backup_data():
    data = load_data()
    backup_bytes = json.dumps(data, indent=2).encode('utf-8')
    
    return send_file(
        io.BytesIO(backup_bytes),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'business_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )

@app.route('/api/restore', methods=['POST'])
def restore_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file and file.filename.endswith('.json'):
        try:
            data = json.load(file)
            validated_data = validate_data(data)
            save_data(validated_data)
            return jsonify({"message": "Data restored successfully"}), 200
        except:
            return jsonify({"error": "Invalid JSON file"}), 400
    
    return jsonify({"error": "Invalid file format. Please upload a JSON file"}), 400

# Dashboard API
@app.route('/api/dashboard')
def get_dashboard_data():
    data = load_data()
    
    total_sales = sum(t.get('amount', 0) for t in data['transactions'] if t.get('type') == 'sale')
    active_customers = len([c for c in data['customers'] if c.get('status') == 'active'])
    stock_value = sum(p.get('price', 0) * p.get('stock', 0) for p in data['products'])
    expenses = sum(t.get('amount', 0) for t in data['transactions'] if t.get('type') in ['purchase', 'expense'])
    gross_profit = total_sales - expenses
    
    recent_transactions = sorted(data['transactions'], key=lambda x: x.get('date', ''), reverse=True)[:5]
    top_customers = sorted(data['customers'], key=lambda x: x.get('total_spent', 0), reverse=True)[:5]
    
    stock_alerts = []
    for product in data['products']:
        stock = product.get('stock', 0)
        min_stock = product.get('min_stock', 5)
        if stock <= min_stock:
            alert = {
                'name': product.get('name', ''),
                'stock': stock,
                'min_stock': min_stock,
                'status': 'Out of Stock' if stock == 0 else 'Low Stock'
            }
            stock_alerts.append(alert)
    
    return jsonify({
        'stats': {
            'total_sales': total_sales,
            'total_products': len(data['products']),
            'total_customers': active_customers,
            'stock_value': stock_value,
            'gross_profit': gross_profit
        },
        'recent_transactions': recent_transactions,
        'top_customers': top_customers,
        'stock_alerts': stock_alerts
    })

# Customer Analytics API
@app.route('/api/analytics/customers')
def get_customer_analytics():
    data = load_data()
    
    customer_types = defaultdict(int)
    for customer in data['customers']:
        customer_type = customer.get('type', 'Regular')
        customer_types[customer_type] += 1
    
    repeat_customers = len([c for c in data['customers'] if c.get('total_orders', 0) > 1])
    repeat_rate = (repeat_customers / len(data['customers']) * 100) if data['customers'] else 0
    
    total_spent = sum(c.get('total_spent', 0) for c in data['customers'])
    total_orders = sum(c.get('total_orders', 0) for c in data['customers'])
    avg_order_value = total_spent / total_orders if total_orders > 0 else 0
    
    top_customers = sorted(data['customers'], key=lambda x: x.get('total_spent', 0), reverse=True)[:5]
    top_customers_list = [
        {"name": c['name'], "total_spent": c.get('total_spent', 0), "total_orders": c.get('total_orders', 0)}
        for c in top_customers
    ]
    
    return jsonify({
        'customer_distribution': dict(customer_types),
        'repeat_rate': repeat_rate,
        'avg_order_value': avg_order_value,
        'top_customers': top_customers_list,
        'growth_rate': 12.5
    })

if __name__ == '__main__':
    # Ensure necessary directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Load data to initialize
    load_data()
    
    # For Render, use the port provided by the environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
