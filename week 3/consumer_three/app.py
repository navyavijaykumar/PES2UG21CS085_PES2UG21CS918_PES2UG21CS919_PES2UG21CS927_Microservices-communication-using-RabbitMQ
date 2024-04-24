from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shivaji9',
    'database': 'inventory_management'
}

def connect_to_db():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    return "Welcome to the Inventory Management API"

@app.route('/stock', methods=['GET'])
def get_stock():
    """Fetches all items in stock."""
    try:
        connection = connect_to_db()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM items")
            items = cursor.fetchall()
            connection.close()
            return jsonify(items)
        else:
            return "Failed to connect to the database", 500
    except Error as e:
        return f"Error retrieving stock: {e}", 500

@app.route('/stock', methods=['POST'])
def add_item():
    """Adds a new item to the stock."""
    try:
        data = request.json
        item_name = data['name']
        quantity = data['quantity']
        description = data['description']

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO items (name, quantity, description) VALUES (%s, %s, %s)"
            cursor.execute(query, (item_name, quantity, description))
            connection.commit()
            connection.close()
            return "Item added successfully", 201
        else:
            return "Failed to connect to the database", 500
    except Error as e:
        return f"Failed to add item: {e}", 500

@app.route('/stock/<string:item_name>', methods=['PUT'])
def update_item(item_name):
    """Updates quantity of an item."""
    try:
        data = request.json
        quantity_change = data['quantity_change']

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            query = "UPDATE items SET quantity = quantity + %s WHERE name = %s"
            cursor.execute(query, (quantity_change, item_name))
            connection.commit()
            if cursor.rowcount > 0:
                connection.close()
                return "Item updated successfully", 200
            else:
                connection.close()
                return "No item found with the given name", 404
        else:
            return "Failed to connect to the database", 500
    except Error as e:
        return f"Failed to update item: {e}", 500

@app.route('/stock/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Deletes an item from the stock."""
    try:
        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            query = "DELETE FROM items WHERE id = %s"
            cursor.execute(query, (item_id,))
            connection.commit()
            if cursor.rowcount > 0:
                connection.close()
                return "Item deleted successfully", 200
            else:
                connection.close()
                return "No item found with the given ID", 404
        else:
            return "Failed to connect to the database", 500
    except Error as e:
        return f"Failed to delete item: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)