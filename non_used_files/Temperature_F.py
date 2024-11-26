from flask import Flask, jsonify
import requests
import pika
import threading
import json

app = Flask(__name__)

port = 5000
temperature_measure = "F"
url = f"http://127.0.0.1:{port}/"

# Global variable to hold the latest temperature in Fahrenheit received
latest_temperature_fahrenheit = None

def callback_fahrenheit(ch, method, properties, body):
    global latest_temperature_fahrenheit
    # Decode the message and update the latest temperature in Fahrenheit
    data = json.loads(body.decode())  # Convert from JSON to dictionary
    if data.get("type") == "F":  # Check if it's temperature in Fahrenheit
        latest_temperature_fahrenheit = data.get("value")
        print(f"Temperatura Fahrenheit recebida: {latest_temperature_fahrenheit} °F")

def consume_temperature_fahrenheit():
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the exchange for temperatures
    channel.exchange_declare(exchange='temperaturas', exchange_type='fanout')

    # Create an exclusive queue for this consumer
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind the queue to the exchange
    channel.queue_bind(exchange='temperaturas', queue=queue_name)

    # Set up a consumer for the Fahrenheit temperature queue
    channel.basic_consume(queue=queue_name, on_message_callback=callback_fahrenheit, auto_ack=True)

    print('Aguardando mensagens de temperatura em Fahrenheit...')
    channel.start_consuming()

@app.route('/', methods=['GET'])
def get_data():
    data = {'key': latest_temperature_fahrenheit} if latest_temperature_fahrenheit else {'key': 'No data received'}
    return jsonify(data)

if __name__ == '__main__':
    data = {"type": temperature_measure, "url": url}
    print(data)
    requests.post("http://127.0.0.1:5020/services", data=data)

    # Start the RabbitMQ consumer in a separate thread
    consumer_thread = threading.Thread(target=consume_temperature_fahrenheit)
    consumer_thread.start()

    # Start the Flask app
    app.run(debug=True, port=port, use_reloader=False)
    