# Papertrading by Ofek Grunfeld

Welcome to PaperTrading, a comprehensive and interactive simulation platform designed by Ofek Grunfeld for traders who want to practice their trading strategies without financial risk. This project aims to provide a realistic trading environment where you can test your ideas, learn from the experience, and improve your trading skills.

## Features

- **Real-Time Market Simulation**: Experience trading with real-time market data to test your strategies under market conditions.
- **Diverse Financial Instruments**: Trade a variety of financial instruments including stocks, forex, commodities, and more.
- **Portfolio Management**: Track your investments and adjust your strategies with an intuitive portfolio management interface.
- **Risk-Free Environment**: Practice trading in a completely risk-free environment to learn and grow as a trader.
- **Strategy Analytics**: Analyze the performance of your trading strategies with comprehensive analytics tools.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Any modern web browser
- Docker

### Installation
- Generate a certificate from openssl or use either Let's Encrypt or Certify The Web. <br>
In order to generate a certificate from openssl, you can download openssl and enter this:
```shell
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
````
- Put your env variables
- Create docker containers: 
```dockerfile
docker-compose -p ogs-papertrading  up -d --build 
```


If you want to run the servers with python instead of docker containers remove the add_middleware comment on /papertrading/main.py/run_app
<br>
and change the .env allowed network to be localnetowrk (either 0.0.0.0 or 127.0.0.1)
<br>
also run the uvicorn server on 127.0.0.1 instead of 0.0.0.0
<br>
thats it
