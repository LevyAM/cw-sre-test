from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import time
import requests
import feedparser
import smtplib
import socket

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration parameters
email_address = os.getenv("EMAIL_ADDRESS")
check_interval = int(os.getenv("CHECK_INTERVAL", 60))
timeout = int(os.getenv("TIMEOUT", 10))
healthy_threshold = int(os.getenv("HEALTHY_THRESHOLD", 3))
unhealthy_threshold = int(os.getenv("UNHEALTHY_THRESHOLD", 3))
token = os.getenv("TOKEN")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
tcp_host = os.getenv("TCP_HOST")
tcp_port = int(os.getenv("TCP_PORT", 3000))
http_host = os.getenv("HTTP_HOST")
http_port = int(os.getenv("HTTP_PORT"))

# State variables
healthy_count = 0
unhealthy_count = 0


def check_tcp_endpoint(host, port, auth_token):
    try:
        # Create TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)

        # Connect to TCP server
        s.connect((host, port))

        # Send auth token
        s.sendall(auth_token.encode())

        # Receive response
        response = s.recv(1024)

        # Close the socket
        s.close()

        if response == b"OK":
            return True
        else:
            return False
    except Exception as e:
        print("Failed to check TCP endpoint:", str(e))
        return False

def check_http_endpoint(host, port, auth_token):

def monitor_endpoints():
    global healthy_count, unhealthy_count

    while True:
        # Check first endpoint
        endpoint1_status = check_tcp_endpoint(tcp_host, tcp_port, token)
        if endpoint1_status:
            healthy_count += 1
            unhealthy_count = 0
            if healthy_count >= healthy_threshold:
                # Service is considered healthy
                # send_email("Service Status: Healthy",
                #            "The service is now healthy.")
        else:
            unhealthy_count += 1
            healthy_count = 0
            if unhealthy_count >= unhealthy_threshold:
                # Service is considered unhealthy
                # send_email("Service Status: Unhealthy",
                #            "The service is now unhealthy.")

        # Check second endpoint
        endpoint2_status = check_endpoint( 
            "https://tonto-http.cloudwalk.io?auth=" + token)
        if endpoint2_status:
            healthy_count += 1
            unhealthy_count = 0
            if healthy_count >= healthy_threshold:
                # Service is considered healthy
                # send_email("Service Status: Healthy",
                #            "The service is now healthy.")
        else:
            unhealthy_count += 1
            healthy_count = 0
            if unhealthy_count >= unhealthy_threshold:
                # Service is considered unhealthy
                # send_email("Service Status: Unhealthy",
                #            "The service is now unhealthy.")

        time.sleep(check_interval)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Update configuration with form data
        email_address = request.form['email_address']
        check_interval = int(request.form['check_interval'])
        timeout = int(request.form['timeout'])
        healthy_threshold = int(request.form['healthy_threshold'])
        unhealthy_threshold = int(request.form['unhealthy_threshold'])

    return render_template('index.html',
                           email_address=email_address,
                           check_interval=check_interval,
                           timeout=timeout,
                           healthy_threshold=healthy_threshold,
                           unhealthy_threshold=unhealthy_threshold)


if __name__ == "__main__":
    monitor_endpoints()
    app.run()
