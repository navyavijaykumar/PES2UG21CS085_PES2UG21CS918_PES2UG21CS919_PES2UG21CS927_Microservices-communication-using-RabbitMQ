from flask import Flask, request, jsonify
import pika
import json

app = Flask(__name__)

# RabbitMQ connection parameters
credentials = pika.PlainCredentials('guest', 'guest')
rabbit_connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = rabbit_connection.channel()
channel.queue_declare(queue='orders', durable=True)

@app.route('/orders', methods=['POST'])
def create_order():
    """Creates a new order."""
    try:
        data = request.get_json()
        order_id = data['order_id']
        items = data['items']
        # Publish order to RabbitMQ
        order_data = {
            'order_id': order_id,
            'items': items
        }
        channel.basic_publish(exchange='', routing_key='orders', body=json.dumps(order_data), properties=pika.BasicProperties(delivery_mode=2))
        return "Order created successfully", 201
    except Exception as e:
        return f"Failed to create order: {e}", 500

@app.route('/orders', methods=['GET'])
def get_orders():
    return "Order created successfully."

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return "The requested URL was not found on the server.", 404

if __name__ == '__main__':
    app.run(debug=True)
