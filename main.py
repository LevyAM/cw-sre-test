from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import threading
import socket
import time
import smtplib
import os
import requests
from flask import Flask, Response, render_template, request
from flask_jwt_extended import jwt_required
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT"))
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
check_interval = int(os.getenv("CHECK_INTERVAL"))
timeout = int(os.getenv("TIMEOUT"))
healthy_threshold = int(os.getenv("HEALTHY_THRESHOLD"))
unhealthy_threshold = int(os.getenv("UNHEALTHY_THRESHOLD"))
http_link = os.getenv("HTTP_HOST")
tcp_link = os.getenv("TCP_HOST")
tcp_port = os.getenv("TCP_PORT")
smtp_api_token = os.getenv("SMTP_API_TOKEN")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")
smtp_username = os.getenv("SMTP_USERNAME")
smtp_password = os.getenv("SMTP_PASSWORD")
auth_token = os.getenv("AUTH_TOKEN")
http_healthy_count = 0
http_unhealthy_count = 0
tcp_healthy_count = 0
tcp_unhealthy_count = 0
http_status = "Unknown"
tcp_status = "Unknown"


def check_http_endpoint(host, auth_token, timeout=timeout):

    url = f"https://{host}/?auth={auth_token}&buf=test"

    try:
        response = requests.get(url, timeout=timeout)

        response.raise_for_status()

        if response.status_code == 200:
            for line in response.iter_lines():
                if b"CLOUDWALK" in line:
                    return True
            return True
        else:
            print("HTTP Response Status Code: " + str(response.status_code))
            return False
    except requests.exceptions.RequestException as err:
        print("HTTP Request Exception: ", err)
        return False


def check_tcp_link(host, port, auth_token, timeout=timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, int(port)))
        auth_message = f"auth {auth_token}".encode()
        sock.sendall(auth_message)
        auth_reply = sock.recv(1024)

        if b"auth ok" in auth_reply:
            test_message = b"Test"
            sock.sendall(test_message)

            test_reply = sock.recv(1024)

            if b"CLOUDWALK" in test_reply:
                return True

    except socket.error as err:
        print("TCP: Connection error:", err)
    finally:
        sock.close()

    return False


def send_email_alert(subject, message, sender=sender_email, receiver=receiver_email, smtp_host=smtp_host, smtp_port=smtp_port, smtp_username=smtp_username, smtp_password=smtp_password, smtp_api_token=smtp_api_token):
    url = "https://api.smtplw.com.br/v1/messages"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "x-auth-token": smtp_api_token,
    }
    data = {
        "subject": subject,
        "body": message,
        "to": receiver,
        "from": sender,
        "headers": {
            "Content-Type": "text/plain; charset=us-ascii"
        },
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201 or response.status_code == 200:
        print("Email sent successfully!")
    else:
        print("Error sending email: {}".format(response.status_code))
        print(response.text)


def check_health():
    global http_healthy_count
    global http_unhealthy_count
    global tcp_healthy_count
    global tcp_unhealthy_count
    global http_status
    global tcp_status

    if check_http_endpoint(http_link, auth_token, timeout):
        http_healthy_count += 1
        http_unhealthy_count = 0
        if http_healthy_count == healthy_threshold and http_status != "Healthy":
            http_status = "Healthy"
            http_healthy_count = 0
            http_unhealthy_count = 0
            print("HTTP Endpoint is Healthy")
            send_email_alert(
                "Tonto HTTP Endpoint is Healthy", "The Tonto HTTP endpoint is now healthy.")
    else:
        http_unhealthy_count += 1
        http_healthy_count = 0
        if http_unhealthy_count == unhealthy_threshold and http_status != "Unknown" and http_status != "Unhealthy":
            http_status = "Unhealthy"
            http_healthy_count = 0
            http_unhealthy_count = 0
            print("HTTP Endpoint is Unhealthy")
            send_email_alert(
                "Tonto HTTP Endpoint is Unhealthy", "The Tonto HTTP endpoint is now unhealthy.")
    if check_tcp_link(tcp_link, tcp_port, auth_token, timeout):
        tcp_healthy_count += 1
        tcp_unhealthy_count = 0
        if tcp_healthy_count == healthy_threshold and tcp_status != "Healthy":
            tcp_status = "Healthy"
            tcp_healthy_count = 0
            tcp_unhealthy_count = 0
            print("TCP Endpoint is Healthy")
            send_email_alert(
                "Tonto TCP Endpoint is Healthy", "The Tonto TCP endpoint is now healthy.")
    else:
        tcp_unhealthy_count += 1
        tcp_healthy_count = 0
        if tcp_unhealthy_count == unhealthy_threshold and tcp_status != "Unhealthy" and tcp_status != "Unknown":
            tcp_status = "Unhealthy"
            tcp_healthy_count = 0
            tcp_unhealthy_count = 0
            print("TCP Endpoint is Unhealthy")
            send_email_alert(
                "Tonto TCP Endpoint is Unhealthy", "The Tonto TCP endpoint is now unhealthy.")
    print("Checking health...")


def start_health_check():
    if __name__ == "__main__":
        # while True:
        print("Starting health check...")
        check_health()
        time.sleep(check_interval)


@app.route("/rss", methods=["GET"])
def rss():

    global http_status
    global tcp_status

    entries = []
    entries.append({
        "title": "Tonto HTTP Health",
        "description": "The current health status of the HTTP Service is " + http_status + ".",
        "link": http_link})
    entries.append({
        "title": "Tonto TCP Health",
        "description": "The current health status of the TCP Service is " + tcp_status + ".",
        "link": tcp_link})

    feed = {
        "title": "Tonto Health Status",
        "entries": entries
    }

    print(http_status)
    print(tcp_status)

    return feed


# Create an authenticated route that needs auth_token to change receiver_email, check_interval, timeout, healthy_threshold, unhealthy_threshold
@app.route("/settings", methods=["POST"])
def settings():

    global receiver_email
    global check_interval
    global timeout
    global healthy_threshold
    global unhealthy_threshold

    new_receiver_email = request.json.get("receiver_email")
    new_check_interval = request.json.get("check_interval")
    new_timeout = request.json.get("timeout")
    new_healthy_threshold = request.json.get("healthy_threshold")
    new_unhealthy_threshold = request.json.get("unhealthy_threshold")

    if receiver_email:
        receiver_email = new_receiver_email

    if check_interval:
        check_interval = new_check_interval

    if timeout:
        timeout = new_timeout

    if healthy_threshold:
        healthy_threshold = new_healthy_threshold

    if unhealthy_threshold:
        unhealthy_threshold = new_unhealthy_threshold

    # Return success message and code 200

    return Response(status=200, response="Settings updated")


@app.route("/", methods=["GET"])
def index():

    global http_status
    global tcp_status
    global http_link
    global tcp_link
    global check_interval
    global timeout
    global healthy_threshold
    global unhealthy_threshold

    return render_template("index.html", http_link=http_link, tcp_link=tcp_link, check_interval=check_interval, timeout=timeout, healthy_threshold=healthy_threshold, unhealthy_threshold=unhealthy_threshold)


if __name__ == "__main__":
    health_check_thread = threading.Thread(target=start_health_check)
    health_check_thread.start()

if __name__ == "__main__":

    app.run("0.0.0.0", port=port, debug=True)
