import unittest
from unittest import mock
from unittest.mock import patch
from main import test_http, test_tcp, send_email


class AppTests(unittest.TestCase):

    def test_http_with_valid_response(self):
        host = "example.com"
        auth_token = "AUTH_TOKEN"

        with patch("requests.get") as mock_get:
            mock_response = mock_get.return_value
            mock_response.status_code = 200
            mock_response.iter_lines.return_value = iter([b"CLOUDWALK test"])
            result = test_http(host, auth_token)
            print("HTTP valid test:", result)
            self.assertTrue(result)

    def test_http_with_invalid_response(self):
        host = "example.com"
        auth_token = "AUTH_TOKEN"

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            result = test_http(host, auth_token)
            print("HTTP invalid test:", result)
            self.assertFalse(result)

    def test_tcp_with_valid_response(self):
        host = "example.com"
        port = 3000
        auth_token = "AUTH_TOKEN"

        with patch("socket.socket") as mock_socket:
            mock_connect = mock_socket.return_value.connect
            mock_sendall = mock_socket.return_value.sendall
            mock_recv = mock_socket.return_value.recv

            mock_connect.return_value = None
            mock_sendall.return_value = None
            mock_recv.side_effect = [b"auth ok", b"CLOUDWALK"]

            result = test_tcp(host, port, auth_token)
            print("TCP valid test:", result)
            self.assertTrue(result)

    def test_tcp_with_invalid_response(self):
        host = "example.com"
        port = 3000
        auth_token = "AUTH_TOKEN"

        with patch("socket.socket") as mock_socket:
            mock_connect = mock_socket.return_value.connect
            mock_sendall = mock_socket.return_value.sendall
            mock_recv = mock_socket.return_value.recv

            mock_connect.return_value = None
            mock_sendall.return_value = None
            mock_recv.side_effect = [b"auth error", b"Invalid"]

            result = test_tcp(host, port, auth_token)
            print("TCP invalid test:", result)
            self.assertFalse(result)

    @mock.patch('main.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        subject = "Test Subject"
        message = "Test Message"
        sender = "sender@example.com"
        recipient = "recipient@example.com"
        smtp_host = "smtp.example.com"
        smtp_port = 587
        smtp_username = "smtp_username"
        smtp_password = "smtp_password"

        # Call the function
        send_email(subject, message, sender, recipient, smtp_host,
                   smtp_port, smtp_username, smtp_password)

        # Assertions
        mock_smtp.assert_called_once_with(smtp_host, smtp_port)
        mock_smtp.return_value.__enter__.assert_called_once()
        mock_smtp.return_value.__enter__.return_value.login.assert_called_once_with(
            smtp_username, smtp_password)
        mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once_with(
            sender, recipient, mock.ANY)
        mock_smtp.return_value.__enter__.return_value.starttls.assert_called_once()
        mock_smtp.return_value.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
