# O.G's PaperTrading Platform

Welcome to O.G's PaperTrading, a sophisticated and interactive simulation platform designed by Ofek Grunfeld. This project aims to offer traders a realistic environment to practice and refine their trading strategies without any financial risk.

## Features

- **Build a Portfolio**: Create and manage a diverse portfolio with various financial instruments including stocks, forex, and commodities.
- **Engage with Live Market Data**: Utilize real-time market data to simulate trades and test your strategies under actual market conditions.
- **Risk-Free Trading**: Practice trading in a completely risk-free environment, allowing you to experiment with different strategies without financial consequences.
- **Use TradingView's Charts**: Leverage the powerful charting tools from TradingView to analyze market trends and make informed decisions.

## Getting Started

### For Users

1. **Visit the Website**: Navigate to the PaperTrading platform's website.
2. **Sign Up**: Create an account by signing up with your details.
3. **Use the Platform**: Start using the platform to build and manage your portfolio, engage in live trading simulations, and analyze your performance.

### For Developers

#### Prerequisites

Ensure you have one of the following:
- **Docker**: Recommended for ease of setup.
- **Python 3.12.1**: If you prefer to run the servers manually.

#### Installation Steps

1. **Generate SSL Certificates** and save them inside `/fastapi-app/https`:
   ```shell
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

2. **For Running In Python**:
   - Modify the `run_app` function's host in `/fastapi-app/main.py` to `127.0.0.1`.

3. **Ensure Environment Files**:
   - **Root `.env`**:
     - Include your ngrok authtoken.
   - **/fastapi-app/.env**:
     - `FASTAPI_PORT`: Port for FastAPI.
     - `START_BALANCE`: Initial balance in USD.
     - `ENCRYPTION_KEY`: Should match the encryption key in the Flask app's `.env`.
     - `ALLOWED_NETWORK`: Set to `127.0.0.1/16` for Python and `172.28.0.0/16` for Docker.
   - **/flask-app/.env**:
     - `FLASK_DEBUG`: Set to `1` or `0` based on whether debugging is needed.
     - `SECRET_KEY`: Secret key for Flask.
     - `ENCRYPTION_KEY`: Should match the encryption key in the FastAPI app's `.env`.
     - `FLASK_PORT`: Port for Flask.
     - `FASTAPI_IP`: Set to `https://fastapi-app` for Docker and `https://localhost` for Python.
     - `FASTAPI_PORT`: Should match the FastAPI port in the `.env`.

   - Ensure ports in the environment files match the ports in `docker-compose` and Dockerfiles.

4. **Create Docker Containers**:
   ```shell
   docker-compose -p ogs-papertrading up -d --build
   ```
   Docker setup will work out-of-the-box following these steps.

## License

- MIT License

## Screenshots

![Homepage](https://i.imgur.com/qH6BS4r.png "Homepage")

![Main Dashboard](https://i.imgur.com/30oKELi.png "Dashboard")

![Portfolio Management](https://i.imgur.com/X5EToXF.png "Portfolio")

![Userpage](https://i.imgur.com/gJWCJGQ.png "Userpage")