import time
import random
import pika
import json

# Function to measure temperature in Celsius
def medir_temperatura_celsius():
    return round(random.uniform(15.0, 30.0), 2)

# Function to convert Celsius to Fahrenheit
def celsius_para_fahrenheit(celsius):
    return round((celsius * 9/5) + 32, 2)

# Main function for the simulated temperature sensor
def sensor_temperatura_simulado():
    try:
        # Connection to RabbitMQ
        print("Attempting to connect to RabbitMQ...")
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            "10.151.101.137",
            5672,
            '/',
            pika.PlainCredentials("ssle", "ssle")
        ))
        channel = connection.channel()

        # Declare an exchange of type 'fanout'
        channel.exchange_declare(exchange='temperaturas', exchange_type='fanout')
        print("Connected and exchange declared successfully.")

        while True:
            celsius = medir_temperatura_celsius()
            fahrenheit = celsius_para_fahrenheit(celsius)
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            temperatura_celsius = {"type": "C", "value": celsius,"timestamp":current_time}
            temperatura_fahrenheit = {"type": "F", "value": fahrenheit,"timestamp":current_time}

            # Convert dictionaries to JSON
            message_celsius = json.dumps(temperatura_celsius)
            message_fahrenheit = json.dumps(temperatura_fahrenheit)

            # Publish temperature messages
            channel.basic_publish(exchange='temperaturas', routing_key='', body=message_celsius)
            print(f"Published Celsius: {message_celsius}")

            channel.basic_publish(exchange='temperaturas', routing_key='', body=message_fahrenheit)
            print(f"Published Fahrenheit: {message_fahrenheit}")

            time.sleep(30)
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            print("Connection closed.")

if __name__ == "__main__":
    sensor_temperatura_simulado()