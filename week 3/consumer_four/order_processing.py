import pika
import json
import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shivaji9',
    'database': 'inventory_management'
}

# RabbitMQ connection parameters
credentials = pika.PlainCredentials('guest', 'guest')
rabbit_connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = rabbit_connection.channel()
channel.queue_declare(queue='orders', durable=True)

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

def update_inventory(connection, item_name, quantity_change):
    """Updates the inventory based on the order."""
    try:
        cursor = connection.cursor()
        query = "UPDATE items SET quantity = quantity - %s WHERE name = %s"
        cursor.execute(query, (quantity_change, item_name))
        connection.commit()
        if cursor.rowcount > 0:
            print(f"Inventory updated for '{item_name}'")
        else:
            print(f"No item found with the name '{item_name}' to update.")
    except Error as e:
        print(f"Failed to update inventory: {e}")
    finally:
        cursor.close()

def process_order(ch, method, properties, body):
    """Processes incoming orders."""
    order_data = json.loads(body.decode())
    print("Received order:", order_data)
    connection = connect_to_db()
    if connection:
        for item in order_data['items']:
            print("Processing item:", item)
            update_inventory(connection, item, 1)  # Assuming each order adds 1 item to the inventory
        connection.close()
    else:
        print("Failed to connect to the database. Inventory update aborted.")
    # Acknowledge the order
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    print('Consumer_four (Order Processor) connecting to server ...')
    print('Waiting for orders. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='orders', on_message_callback=process_order)
    channel.start_consuming()

if __name__ == '__main__':
    main()