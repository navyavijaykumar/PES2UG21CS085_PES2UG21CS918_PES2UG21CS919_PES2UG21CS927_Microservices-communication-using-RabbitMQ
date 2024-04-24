import pika
import time
import mysql.connector
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MySQL connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'shivaji9',
    'database': 'inventory_management'
}

# RabbitMQ connection parameters
rabbitmq_config = {
    'host': 'localhost',
    'port': 5672,
    'username': 'guest',
    'password': 'guest',
    'queue': 'insert_item'
}

# Connect to MySQL
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        logger.info('Connected to MySQL database')
except mysql.connector.Error as e:
    logger.error(f"Error connecting to MySQL database: {e}")
    exit(1)

# Setup RabbitMQ connection
credentials = pika.PlainCredentials(rabbitmq_config['username'], rabbitmq_config['password'])
connection_rabbitmq = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_config['host'], port=rabbitmq_config['port'], credentials=credentials))
channel = connection_rabbitmq.channel()
channel.queue_declare(queue=rabbitmq_config['queue'], durable=True)

def insert_item_into_db(item_data):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO items (name, quantity, description) VALUES (%s, %s, %s)"
        cursor.execute(query, (item_data['name'], item_data['quantity'], item_data['description']))
        connection.commit()
        logger.info("Item saved successfully!")
    except mysql.connector.Error as e:
        logger.error(f"Failed to insert item into database: {e}")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

def callback(ch, method, properties, body):
    try:
        item_data = json.loads(body)
        insert_item_into_db(item_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=rabbitmq_config['queue'], on_message_callback=callback)
logger.info('Started consuming messages from RabbitMQ...')
channel.start_consuming()