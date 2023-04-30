import requests
import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILO_AUTH_TOKEN")

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


stock_params = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
stock_data = response.json()

dt = datetime.datetime.now()
weekday = dt.isoweekday()

yesterday = datetime.date.today() - datetime.timedelta(days=2)
yest_weekday = yesterday.isoweekday()

# A day before yesterday
db_yest = datetime.date.today() - datetime.timedelta(days=3)
db_yest_weekday = db_yest.isoweekday()

if yest_weekday >= 1 or yest_weekday <= 5 and db_yest_weekday >=1 or db_yest_weekday <= 5:
    yest_stock = stock_data["Time Series (Daily)"][str(yesterday)]["4. close"]
    print(yest_stock)
    db_yest_closing_stock = stock_data["Time Series (Daily)"][str(db_yest)]["4. close"]
    print(db_yest_closing_stock)
else:
    print("No Stocks on Weekends!")


difference = float(yest_stock) - float(db_yest_closing_stock)
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

diff_percent = round((difference / float(yest_stock)) * 100)
print(diff_percent)

if abs(diff_percent) > 0.1:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    three_articles = articles[:3]
    print(three_articles)

    formatted_articles = [f"{STOCK}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_='+14302224091',
            to= YOUR_NUMBER
        )

    print(message.status)

