import unittest
import mock
import requests

from main import check_http_endpoint, check_tcp_link, send_email_alert


class TestCheckHttpEndpoint(unittest.TestCase):

    def test_check_http_endpoint_with_healthy_response(self):
        url = "example.com"
        timeout = 5
        token = "test_token"
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            self.assertTrue(check_http_endpoint(url, token, timeout))

    def test_check_http_endpoint_with_unhealthy_response(self):
        url = "example.com"
        timeout = 5
        token = "test_token"
        with mock.patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            self.assertFalse(check_http_endpoint(url, token, timeout))

    @unittest.expectedFailure
    def test_check_http_endpoint_with_connection_error(self):
        url = "example.com"
        timeout = 5
        token = "test_token"
        with mock.patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            self.assertFalse(check_http_endpoint(url, token, timeout))


class TestCheckTcpLink(unittest.TestCase):

    def test_check_tcp_link_with_successful_connection(self):
        url = "example.com"
        port = 3000
        timeout = 20
        token = "test_token"
        with mock.patch("socket.socket") as mock_socket:
            mock_socket.return_value.connect = mock.Mock(return_value=True)
            self.assertTrue(check_tcp_link(url, port, token, timeout))

    def test_check_tcp_link_with_failed_connection(self):
        url = "example.com"
        port = 3000
        timeout = 5
        token = "test_token"
        with mock.patch("socket.socket") as mock_socket:
            mock_socket.return_value.connect = mock.Mock(return_value=False)
            self.assertFalse(check_tcp_link(url, port, token, timeout))

    @unittest.expectedFailure
    def test_check_tcp_link_with_socket_error(self):
        url = "example.com"
        port = 3000
        timeout = 5
        token = "test_token"
        with mock.patch("socket.socket") as mock_socket:
            mock_socket.side_effect = socket.error()
            self.assertFalse(check_tcp_link(url, port, token, timeout))


class TestSendEmailAlert(unittest.TestCase):

    def test_send_email_alert(self):
        subject = "test_subject"
        message = "test_body"
        with mock.patch("smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.sendmail = mock.Mock(return_value=True)
            self.assertTrue(send_email_alert(subject, message))


if __name__ == "__main__":
    unittest.main()
