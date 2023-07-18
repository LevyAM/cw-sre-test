# Tonto Services Monitor

This app provides a health check for two endpoints: a HTTP endpoint and a TCP endpoint. The health of each endpoint is determined by a number of factors, including the response code from the HTTP endpoint and the response from the TCP endpoint. If an endpoint is unhealthy, an email alert is sent to the administrator.

The app is deployed on Heroku. The Procfile specifies that the app should be run using the Gunicorn WSGI server.

## Endpoints

The application can be accessed at `https://cw-sre-7471da4f6848.herokuapp.com`.

The following endpoints and verbs are supported:

- `/` - GET - Returns the values of the environment variables.
- `/rss` - GET - Returns an RSS feed with the status of the endpoints.
- `/settings` - POST - Set parameters for the monitoring process.

## Setup

1. Clone the repository or download the code files.
2. Create a `.env` file in the project directory and configure the necessary environment variables.
3. Replace the placeholder values with your actual configuration details.
4. The HOST and PORT are automatically set by Heroku, so you can leave them as is when running the application.

## Usage

1. Start the application by running `python main.py`.
2. The application will monitor the HTTP and TCP endpoints based on the configured intervals and thresholds.
3. If an endpoint becomes unhealthy, an email notification will be sent to the configured email address.
4. A rss feed is also provided with the status of the endpoints.

## Customization

- Modify the monitoring parameters (interval, thresholds) by updating the environment variables in the `.env` file.
- Customize the email configuration (SMTP details, recipient address) by updating the environment variables.

## Dependencies

- Flask
- python-dotenv
- requests
- feedgenerator
- smtplib
- socket
- gunicorn

Make sure to install these dependencies before running the application.