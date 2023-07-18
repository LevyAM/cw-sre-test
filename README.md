# Tonto Services Monitor

This is a Flask application that monitors the status of HTTP and TCP endpoints and sends email notifications based on their health.

## Endpoints

The application can be accessed at `NOT DEFINED YET`.

The following endpoints and verbs are supported:

- `/` - GET - Returns the status of the application.
- `/` - POST - Set parameters for the monitoring process.
- `/rss` - GET - Returns an RSS feed with the status of the endpoints.

## Setup

1. Clone the repository or download the code files.
2. Create a `.env` file in the project directory and configure the necessary environment variables.
3. Replace the placeholder values with your actual configuration details.

## Usage

1. Start the application by running `python main.py`.
2. The application will monitor the HTTP and TCP endpoints based on the configured intervals and thresholds.
3. If an endpoint becomes unhealthy, an email notification will be sent to the configured email address.
4. A rss feed is also provided with the status of the endpoints.

## Customization

- Modify the monitoring parameters (interval, thresholds) by updating the environment variables in the `.env` file.
- Customize the email configuration (SMTP details, recipient address) by updating the environment variables.
- The application provides an RSS feed with the status of the TCP and HTTP endpoints. Access it at `NOT DEFINED YET`

## Dependencies

- Flask
- python-dotenv
- requests
- feedgenerator
- smtplib
- socket

Make sure to install these dependencies before running the application.