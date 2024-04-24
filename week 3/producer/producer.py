import pika
import time
import random
import json

# RabbitMQ connection parameters
rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

def send_message(queue_name, message):
    """Sends a message to the specified queue."""
    channel = rabbit_connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
    print(f" [x] Sent {message} to '{queue_name}' queue")
    channel.close()

def generate_item_data():
    """Generates a message for the item_creation.py consumer."""
    item_data = {
        'name': f'Item{random.randint(1, 100)}',
        'quantity': random.randint(1, 10),
        'description': f'Description of Item{random.randint(1, 100)}'
    }
    return item_data

def generate_stock_update_data():
    """Generates a message for the stock_management.py consumer."""
    stock_update_data = {
        'item_name': f'Item{random.randint(1, 100)}',
        'quantity_change': random.randint(-10, 10)  # Can be positive or negative
    }
    return stock_update_data

def generate_health_check_data():
    """Generates a message for the healthcheck.py consumer."""
    health_check_data = {
        'service': 'Service' + str(random.randint(1, 5)),
        'status': random.choice(['OK', 'FAIL'])
    }
    return health_check_data

def generate_order_data():
    """Generates a message for the order_processing.py consumer."""
    order_data = {
        'order_id': f'Order{random.randint(1, 100)}',
        'items': [f'Item{random.randint(1, 100)}' for _ in range(random.randint(1, 5))]
    }
    return order_data

def main():
    while True:
        send_message('insert_item', generate_item_data())
        send_message('update_stock', generate_stock_update_data())
        send_message('health_check', generate_health_check_data())
        send_message('orders', generate_order_data())
        time.sleep(5)  # Sending messages every 5 seconds

if __name__ == '__main__':
    main()