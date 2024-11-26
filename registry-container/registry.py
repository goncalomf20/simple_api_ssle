from flask import Flask, jsonify, request, abort
import pika
import json

app = Flask(__name__)

# RabbitMQ connection parameters
rabbitmq_host = '10.151.101.137' 
username = 'ssle'  
password = 'ssle'  
users_list = []


credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=rabbitmq_host,     
    port=5672,              
    virtual_host='/',       
    credentials=credentials 
))
channel = connection.channel()

# Declare the exchange
channel.exchange_declare(exchange='services_exchange', exchange_type='fanout')

port = 5020


# Function to publish data to RabbitMQ
def publish_to_rabbitmq(data):
    message = json.dumps(data)
    channel.basic_publish(exchange='services_exchange', routing_key='', body=message)
    print(f"Published to RabbitMQ: {data}")


@app.route('/services', methods=['POST'])
def register():
    data = request.form.to_dict()
    users_list.append(data)
    # Ensure service data is not empty
    if not data:
        return jsonify({"error": "No data provided"}), 400

    return "Success", 201


@app.route('/services', methods=['GET'])
def get_services():
    return users_list

@app.route('/services/<int:id>', methods=['GET'])
def get_one_service(id):
    return jsonify({"message": f"Service {id} would be retrieved here"})


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=port)