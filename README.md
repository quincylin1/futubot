# FutuBot - An Intraday Trading Robot Using Futu OpenAPI

## Introduction

FUTU (Futu Holdings Limited, NASDAQ: FUTU) is one of the most popular online brokers in Hong Kong. Despite its popularity, there have only been limited attempts to utilize its open-source APIs for algorithmic trading. As such, this project (named **FutuBot**) aims to use Futu APIs to build an intraday trading robot. A dashboard is also provided to show important trading statistics in real time, such as candlestick and indicators graphs, account details, portfolio distribution and trading order activity. Below shows FutuBot in action:

https://user-images.githubusercontent.com/33197366/185895803-d27fdc24-b30a-4b2e-9c80-45f7b6779252.mp4

(Note: For privacy reason, this demo runs in paper trading mode and the order_ids are not shown.)

## About Futu OpenAPI

FutuBot primarily uses the APIs released by Futu for getting real-time market data as well as placing orders. The Futu OpenAPI consists of FutuOpenD and Futu API. The respective function of FutuOpenD and Futu API is outlined below:

- FutuOpenD: The gateway program of Futu API running on user's local computer or cloud server and is responsible for transferring the protocol requests to Futu Server, and returning the processed data.
- Futu API: An API SDK encapsulated by Futu for getting quotations and executing trading actions.

You can read more about the details of FutuOpenD and Futu API and how they interact with each other on the [Futu API Doc website](https://openapi.futunn.com/futu-api-doc/en/intro/intro.html).

**This project assumes you already have a Futu ID and trading account** (please refer to the _Account_ section on [Futu API Doc website](https://openapi.futunn.com/futu-api-doc/en/intro/intro.html) for relevant details). In order to run the Futu API, you must also download FutuOpenD on your local computer. Futu provides two operation modes for FutuOpenD: _visualization_ and _command line_. Please refer to the [Futu API Doc website](https://openapi.futunn.com/futu-api-doc/en/quick/opend-base.html) for installation details of each mode.

## Overview of the Project

The idea of FutuBot is simple: Given a trading strategy, it uses Futu APIs to calculate the relevant technical indicators and place orders when buy and/or sell signals are generated.

### A Modular Approach

FutuBot consists of five main modules:

- `Accounts`: This is where all the useful Futu APIs are encapsulated and allows the APIs to be abstracted from all other modules.
- `Robot`: This implements the main logic of FutuBot including the creation of `StockFrame` and `Portfolio` object as well as orders execution based on indicators' signals.
- `Indicators`: This is where all the indicators are calculated and refreshed.
- `StockFrame`: This module organizes the candlestick data and indicators into a MultiIndex pandas dataframe.
- `Portfolio`: This module contains important imformation of user's Futu account including the total assets, total market value and portfolio distribution. It also contains common evaluation metrics for backtesting such as total PnL value and Sharpe Ratio.

In addition, there is also a `Strategy` folder which contains all the trading strategies that are currently supported, each in a separate `.py` file. Organizing the strategy modules this way allows users to add their own customized strategy (e.g. machine learning) easily by creating a `.py` file for it. You can also learn more about how each strategy works [here](Strategy/README.md).

### Trading Logic

FutuBot currently supports both live and paper trading, as well as market and limit orders. However, since Futu OpenAPI does **not** support market orders for paper trading, orders submitted in paper trading mode may not be filled immediately. In order to prevent pending orders from accumulating, buy and sell signals are only executed when there are no pending orders for the given code. When a buy signal is present for a given code, it buys one lot of shares if there is no holding position for that particular code. Conversely, when a sell signal is present, it sells all the current holdings only if there are holdings for that code.

### Limitations

FutuBot also comes with several limitations:

- Quote Right: Since FutuBot relies on free Futu APIs, it only has quote right for LV2 securities market quotes from the Hong Kong market (You can learn more about Futu quote right on the [official site](https://openapi.futunn.com/futu-api-doc/en/intro/authority.html)).
- Interface Frequency: Each Futu API has its own [frequency limitation rules](https://openapi.futunn.com/futu-api-doc/en/intro/authority.html), and an error is raised if the API is called beyond the frequency limits. For instance, `get_market_snapshot()` only allows a maximum of 60 requests every 30 seconds.
- Real-time Dashboard Update: The Hong Kong market has a one hour lunch break from HKT 12:00:00 to HKT 13:00:00, during which the market is temporarily closed. Unforeseen errors may come up when running the dashboard during this time, and users need to click `Ctrl-C` to stop and restart the robot again. **It is therefore encouraged to run FutuBot during market hours only**. In addition, to avoid producing too much overhead on the real-time dashboard, the update time of the dashboard is set to 10,000 milliseconds (which can be changed depending on user's local computer). This gives rise to a certain level of latency for live graph updates when interacting with the dashboard.

## Installation

Please refer to [INSTALL.md](docs/INSTALL.md) for a detailed description of installing FutuBot along with its virtual environment and dependencies.

## Demo

To verify that FutuBot is successfully installed on your computer, you can run either `demo/main.py` or `demo/app.py` on the terminal. `main.py` simply runs FutuBot and displays results on the terminal, while `app.py` runs FutuBot on the backend and displays results on a Dashboard on browser.

As an example, the command below runs `app.py`:

```shell
python demo/app_demo.py demo/configs/futubot_config_demo.py --display-all-cols
```

where the optional argument `--display-all-cols` is also specified to show all the columns in `StockFrame`.

## Usage

To simplify the process of running FutuBot, a [config file](configs/futubot_config.py) is provided to allow users to specify the necessary parameters for running the robot. These parameters are:

- `filter_trdmarket`: The transaction market. FutuBot currently supports Hong Kong market only as Futu only provides free quote right for Hong Kong securities (Please refer to Authorities and Limitations in [Futu API Doc](<>) for more details).
- `host`: The API listening IP address. Default: 127.0.0.1 for local connections.
- `port`: THe API listening port. Default: 11111.
- `security_firm`: The security firm for intraday trading. Currently only FUTU HK (`FUTUSECURITIES`) is supported.
- `paper_trading`: Whether to activate paper trading mode or not.
- `password`: The password of Futu trading account for placing orders (only necessary for live trading).
- `order_type`: The type of order, which can be either `market` or `limit` (Note: Futu does not support market orders for paper trading).
- `stocks_of_interest`: The stocks we are interested in trading.
- `historical_quote_dates`: The `start_date` and `end_date` over which the `StockFrame` is initialized. Format: `yyyy-MM-dd HH:mm:ss`.
- `indicators`: The parameters of indicators.
- `strategy`: The strategy and parameters used.

Once the parameters are specified, you can then run the scripts in `tools/`. **Since Futu only allows trading during market hours (even for paper trading!), the scripts can only be run during market hours**.

Depending on your preference, you can either run:

```shell
python tools/main.py configs/futubot_config.py --display-all-cols
```

to display results on terminal, or

```shell
python tools/app.py configs/futubot_config.py --display-all-cols
```

which shows the results on a real-time dashboard.

## Contributing

This project is still at a preliminary stage and there is definitely a lot of room for improvement! For example, more indicators can be added, other trading strategies (e.g. machine learning) can be implemented, and the real-time dashboard can be improved (I am no expert in frontend development...). If you would like to contribute to this project, please refer to [CONTRIBUTING.md](docs/CONTRIBUTING.md) for a complete guide to project contribution.

## Acknowledgement

I would like to thank FUTU for generously releasing the APIs, without which this project could not be realized. I would also like to thank Alex Reed ([areed1192](https://github.com/areed1192)) for his incredibly comprehensive [tutorials](https://www.youtube.com/watch?v=QAo0x9fE6ck&list=PLcFcktZ0wnNmdgAdv4-Yl_nzS5LiKnhnn) on python trading robot, from which this project is inspired. I highly recommend his YouTube channel ([SigmaCoding](https://www.youtube.com/c/SigmaCoding)) to anyone who is interested in learning about quantitative finance and algorithmic trading!
