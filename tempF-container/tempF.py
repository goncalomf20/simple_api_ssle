from flask import Flask, jsonify, request
import requests
import pika
import threading
import json
import re
import datetime

app = Flask(__name__)

port = 5001
list_of_data = []
temperature_measure = "F"
url = f"http://10.151.101.248:{port}/"

latest_temperature_fahrenheit = None

shellshock_log_path = '/var/log/shellshock.log'

def callback_fahrenheit(ch, method, properties, body):
    global latest_temperature_fahrenheit
    data = json.loads(body.decode())
    if data.get("type") == "F":
        latest_temperature_fahrenheit = data.get("value")
        print(f"Temperatura Fahrenheit recebida: {latest_temperature_fahrenheit} °F")
        list_of_data.append(data)

def log_shellshock_attack(details):
    with open(shellshock_log_path, 'a') as log_file:
        log_file.write(details + '\n')

@app.before_request
def detect_shellshock_attack():
    pattern = r'\(\)\s*{.*};'
    for header, value in request.headers.items():
        if re.search(pattern, value):
            log_entry = create_apache_log_entry(header, value)
            print(log_entry)
            log_shellshock_attack(log_entry)

def create_apache_log_entry(header, value):
    ip_address = request.remote_addr or "-"
    user = "-"
    date_time = datetime.datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
    method = request.method
    path = request.path
    http_version = request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    status_code = 200
    size = "-"
    referer = request.headers.get("Referer", "-")
    user_agent = f"{header}: {value}"

    log_entry = f'{ip_address} {user} {user} [{date_time}] "{method} {path} {http_version}" {status_code} {size} "{referer}" "{user_agent}"'
    return log_entry

def consume_temperature_fahrenheit():
    rabbitmq_host = '10.151.101.137'
    rabbitmq_port = 5672

    credentials = pika.PlainCredentials("ssle", "ssle")
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host,
        port=rabbitmq_port,
        virtual_host='/',
        credentials=credentials
    ))

    channel = connection.channel()

    channel.exchange_declare(exchange='temperaturas', exchange_type='fanout')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='temperaturas', queue=queue_name)

    channel.basic_consume(queue=queue_name, on_message_callback=callback_fahrenheit, auto_ack=True)

    print('Aguardando mensagens de temperatura em Fahrenheit...')
    channel.start_consuming()

@app.route('/', methods=['GET'])
def get_data():
    return jsonify(list_of_data)

if __name__ == '__main__':
    data = {"type": temperature_measure, "url": url}
    print(data)
    requests.post("http://10.151.101.43:5020/services", data=data)

    consumer_thread = threading.Thread(target=consume_temperature_fahrenheit)
    consumer_thread.start()

    app.run(host='0.0.0.0', debug=True, port=port, use_reloader=False)
