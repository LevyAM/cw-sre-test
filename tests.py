import unittest
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

    @patch("smtplib.SMTP")
    def test_send_email(self, mock_smtp):
        smtp_instance = mock_smtp.return_value

        subject = "Test Subject"
        message = "Test Message"
        sender = "from@example.com"
        recipient = "to@example.com"

        send_email(subject, message, sender, recipient)

        # Assert SMTP method calls
        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with(
            "your-email@example.com", "your-password")
        smtp_instance.send_message.assert_called_once()
        smtp_instance.quit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
