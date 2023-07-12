from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import time
import requests
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration parameters
check_interval = int(os.getenv("CHECK_INTERVAL", 60))
timeout = int(os.getenv("TIMEOUT", 10))
healthy_threshold = int(os.getenv("HEALTHY_THRESHOLD", 3))
unhealthy_threshold = int(os.getenv("UNHEALTHY_THRESHOLD", 3))

email_address = os.getenv("EMAIL_ADDRESS")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT", 587))
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")

tcp_host = os.getenv("TCP_HOST")
tcp_port = int(os.getenv("TCP_PORT", 3000))
http_host = os.getenv("HTTP_HOST")
http_port = int(os.getenv("HTTP_PORT", 443))
auth_token = os.getenv("AUTH_TOKEN")

# State variables
healthy_count = 0
unhealthy_count = 0

# Send Email Function


def send_email(subject, message, sender, recipient):

    # Create the email message
    email = MIMEMultipart()
    email["Subject"] = subject
    email["From"] = sender
    email["To"] = recipient

    # Attach the message body
    body = MIMEText(message)
    email.attach(body)

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.sendmail(sender, recipient, email.as_string())
        smtp.quit()

# Check HTTP endpoint


def test_http(host, auth_token):
    url = f"https://{host}/?auth={auth_token}&buf=test"

    try:
        response = requests.get(url)

        # Raise an exception if the response status code is not 200
        response.raise_for_status()

        # Get the response body
        lines = response.iter_lines()

        # Check if the response body contains the expected message

        if response.status_code == 200:
            for line in lines:
                if b"CLOUDWALK" in line:
                    return True
            return False
        else:
            print("HTTP: response status:", response.status_code)
            return False

    except requests.exceptions.RequestException as err:
        print("HTTP: request error:", err)
        return False

# Check TCP endpoint


def test_tcp(host, port, auth_token):
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the Tonto TCP service
        sock.connect((host, int(port)))

        # Send the authentication
        auth_message = f"auth {auth_token}".encode()
        sock.sendall(auth_message)

        # Receive the authentication reply
        auth_reply = sock.recv(1024)

        if b"auth ok" in auth_reply:
            # Send the testing message
            test_message = b"Test"
            sock.sendall(test_message)

            # Receive the testing reply
            test_reply = sock.recv(1024)

            if b"CLOUDWALK" in test_reply:
                return True

    except socket.error as err:
        print("TCP: Connection error:", err)
    finally:
        # Close the socket connection
        sock.close()

    return False


def monitor_endpoints():
    global healthy_count
    global unhealthy_count

    while True:
        # Check HTTP endpoint
        http_endpoint_status = test_http(http_host, auth_token)
        if http_endpoint_status:
            healthy_count += 1
            unhealthy_count = 0
            if healthy_count >= healthy_threshold:
                print("HTTP Service Status: Healthy")
                # Service is considered healthy
                # send_email("Service Status: Healthy",
                #            "The service is now healthy.")
        else:
            unhealthy_count += 1
            healthy_count = 0
            if unhealthy_count >= unhealthy_threshold:
                print("HTTP Service Status: Unhealthy")
                # Service is considered unhealthy
                # send_email("Service Status: Unhealthy",
                #            "The service is now unhealthy.")

        # Check TCP endpoint
        tcp_endpoint_status = test_tcp(tcp_host, tcp_port, auth_token)
        if tcp_endpoint_status:
            healthy_count += 1
            unhealthy_count = 0
            if healthy_count >= healthy_threshold:
                print("TCP Service Status: Healthy")
                # Service is considered healthy
                # send_email("Service Status: Healthy",
                #            "The service is now healthy.")
        else:
            unhealthy_count += 1
            healthy_count = 0
            if unhealthy_count >= unhealthy_threshold:
                print("TCP Service Status: Unhealthy")
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
