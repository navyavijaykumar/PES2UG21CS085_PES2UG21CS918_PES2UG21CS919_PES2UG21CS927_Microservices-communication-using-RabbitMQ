import pika
import json
from app import connect_to_db

def callback(ch, method, properties, body):
    """Processes messages from RabbitMQ for stock updates."""
    print("Received a stock update message.")
    try:
        message = json.loads(body.decode())
        item_name = message.get('item_name')
        quantity_change = message.get('quantity_change')

        if item_name is None or quantity_change is None:
            print("Invalid message format.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor()
            query = "UPDATE items SET quantity = quantity + %s WHERE name = %s"
            cursor.execute(query, (quantity_change, item_name))
            connection.commit()
            if cursor.rowcount > 0:
                print(f"Item '{item_name}' updated successfully")
            else:
                print(f"No item found with the name '{item_name}'")
            connection.close()
        else:
            print("Failed to connect to the database. Message processing aborted.")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    print('Consumer_two (Stock Updater) connecting to server ...')
    credentials = pika.PlainCredentials('guest', 'guest')
    rabbit_connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', credentials=credentials))

    channel = rabbit_connection.channel()
    channel.queue_declare(queue='update_stock', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='update_stock', on_message_callback=callback)

    print('Waiting for stock update messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    main()