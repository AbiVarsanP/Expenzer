import sqlite3
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from datetime import datetime
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key in production
CORS(app)

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id TEXT PRIMARY KEY, date TEXT, category TEXT, amount REAL, description TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (name TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS budgets
                 (category TEXT PRIMARY KEY, amount REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (mobile TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS gpay_transactions
                 (id TEXT PRIMARY KEY, mobile TEXT, date TEXT, amount REAL, description TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    mobile = data['mobile']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (mobile, password) VALUES (?, ?)", (mobile, password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Mobile number already registered"}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    mobile = data['mobile']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE mobile = ? AND password = ?", (mobile, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['mobile'] = mobile
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.get_json()
    id = str(uuid.uuid4())
    date = data['date']
    category = data['category']
    amount = float(data['amount'])
    description = data['description']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT INTO expenses (id, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
              (id, date, category, amount, description))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense added successfully", "id": id}), 201

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM expenses")
    expenses = [{"id": row[0], "date": row[1], "category": row[2], "amount": row[3], "description": row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(expenses), 200

@app.route('/api/expenses/<id>', methods=['PUT'])
def update_expense(id):
    data = request.get_json()
    date = data['date']
    category = data['category']
    amount = float(data['amount'])
    description = data['description']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("UPDATE expenses SET date = ?, category = ?, amount = ?, description = ? WHERE id = ?",
              (date, category, amount, description, id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense updated successfully"}), 200

@app.route('/api/expenses/<id>', methods=['DELETE'])
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Expense deleted successfully"}), 200

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT name FROM categories")
    categories = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(categories), 200

@app.route('/api/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    category = data['name']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Category added successfully"}), 201

@app.route('/api/budgets', methods=['POST'])
def set_budget():
    data = request.get_json()
    category = data['category']
    amount = float(data['amount'])
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO budgets (category, amount) VALUES (?, ?)", (category, amount))
    conn.commit()
    conn.close()
    return jsonify({"message": "Budget set successfully"}), 201

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM budgets")
    budgets = [{"category": row[0], "amount": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(budgets), 200

@app.route('/api/reports', methods=['GET'])
def get_reports():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) as total FROM expenses GROUP BY category")
    report = [{"category": row[0], "total": row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(report), 200

@app.route('/api/gpay_transactions', methods=['GET'])
def get_gpay_transactions():
    if 'mobile' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    mobile = session['mobile']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT id, date, amount, description FROM gpay_transactions WHERE mobile = ?", (mobile,))
    transactions = [{"id": row[0], "date": row[1], "amount": row[2], "description": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(transactions), 200

# Simulated GPay transaction data for demo purposes
@app.route('/api/gpay_transactions/sync', methods=['POST'])
def sync_gpay_transactions():
    if 'mobile' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    mobile = session['mobile']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    # Simulated data
    transactions = [
        (str(uuid.uuid4()), mobile, datetime.now().strftime('%Y-%m-%d'), 50.0, "Coffee Shop"),
        (str(uuid.uuid4()), mobile, datetime.now().strftime('%Y-%m-%d'), 120.0, "Grocery Store")
    ]
    c.executemany("INSERT INTO gpay_transactions (id, mobile, date, amount, description) VALUES (?, ?, ?, ?, ?)", transactions)
    conn.commit()
    conn.close()
    return jsonify({"message": "GPay transactions synced"}), 200

if __name__ == '__main__':
    init_db()
    # Prepopulate categories for demo
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    default_categories = [('Food',), ('Transport',), ('Entertainment',), ('Bills',), ('Other',)]
    c.executemany("INSERT OR IGNORE INTO categories (name) VALUES (?)", default_categories)
    conn.commit()
    conn.close()
    app.run(debug=True)