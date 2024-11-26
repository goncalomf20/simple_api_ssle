import time
import psutil
import requests
from prometheus_client import start_http_server, Gauge, Counter
import logging
import time

log_format = '%(asctime)s [%(levelname)s] [prometheus_exporter] %(message)s'
logging.basicConfig(filename='/var/log/prometheus_exporter.log', level=logging.INFO, format=log_format)

cpu_usage_gauge = Gauge('system_cpu_usage_percent', 'Percentage of CPU usage')
memory_usage_gauge = Gauge('system_memory_usage_percent', 'Percentage of memory usage')
http_requests_received_counter = Counter('http_requests_received_total', 'Total number of HTTP requests received', ['method'])
http_requests_sent_counter = Counter('http_requests_sent_total', 'Total number of HTTP requests sent', ['method'])
service_health_gauge = Gauge('external_service_health', 'Health status of external services', ['service'])
request_latency_total_gauge = Gauge('http_request_latency_total_seconds', 'Total time for processing a batch of 10 HTTP requests')
request_latency_avg_gauge = Gauge('http_request_latency_avg_seconds', 'Average time for processing a batch of 10 HTTP requests')

SERVICES = ['http://10.151.101.244:5001/', 'http://10.151.101.43:5020/services']

def check_service_health():
    for service in SERVICES:
        try:
            health_status = requests.get(service)
            if health_status.status_code == 200:
                service_health_gauge.labels(service=service).set(1)
                logging.info(f"Service {service} is up and healthy.")
            else:
                service_health_gauge.labels(service=service).set(0)
                logging.warning(f"Service {service} returned non-200 status: {health_status.status_code}")
        except requests.exceptions.RequestException as e:
            service_health_gauge.labels(service=service).set(0)
            logging.error(f"Service {service} failed with exception: {e}")

def collect_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_usage_gauge.set(cpu_usage)
    logging.info(f"CPU usage: {cpu_usage}%")
    
    if cpu_usage > 90:
        logging.warning(f"High CPU usage detected: {cpu_usage}%")

    memory_usage = psutil.virtual_memory().percent
    memory_usage_gauge.set(memory_usage)
    logging.info(f"Memory usage: {memory_usage}%")
    
    if memory_usage > 90:
        logging.warning(f"High memory usage detected: {memory_usage}%")

def track_http_requests():
    url = "http://10.151.101.244:5001/"
    
    start_time = time.time()

    for _ in range(10):
        response = requests.get(url)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    request_latency_total_gauge.set(elapsed_time)
    avg_latency = elapsed_time / 10
    request_latency_avg_gauge.set(avg_latency)

    if avg_latency > 0.3:
        logging.warning(f"High average request processing time: {avg_latency} seconds per request for 10 requests")

def main():
    start_http_server(8000)
    
    logging.info("Prometheus Exporter started.")
    
    while True:
        check_service_health()
        collect_system_metrics()
        track_http_requests()
        time.sleep(5)

if __name__ == '__main__':
    main()
