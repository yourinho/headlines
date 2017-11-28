"""
Used APIs:
   https://openweathermap.org/api
   https://docs.openexchangerates.org
"""

# Import for the new library.
import feedparser
from flask import Flask
from flask import render_template
from flask import request
# We'll use this lib for JSON parsing.
import json
# We'll use this lib to correctly encode URL parameters.
import urllib
# We'll use this lib to download the data from the web.
import urllib.request as urllib2
import urllib.parse
import datetime
# We'll user this lib to work with cookies (now we can add additional parameters to response).
from flask import make_response

app = Flask(__name__)

# Build a Python dict with all our RSS feeds.
RSS_FEEDS = {'habr': 'https://habrahabr.ru/rss/hubs/all/',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'rbk': 'feed://static.feed.rbc.ru/rbc/logical/footer/news.rss',
             'lenta': 'feed:https://lenta.ru/rss/news',
             'vc': 'feed:https://vc.ru/rss/all'}

DEFAULTS = {'publication': 'habr',
            'city': 'Saint Petersburg, RU',
            'currency_from': 'USD',
            'currency_to': 'RUB'}

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/" \
                  "find?q={}&units=metric&appid=0cce66ee8aae26d43e25af39e9d1c133"

CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=55331f91a49a4b79a6453fa5188fcb3b"


@app.route("/")
def home():
    # Get customized headlines, based on user input or from cookies or defaults.
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)
    # Get customized weather, based on user input or from cookies or defaults.
    city = get_value_with_fallback('city')
    weather = get_weather(city)
    # Get currency rate, based on user input or from cookies or defaults.
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    # Ask for tuple with all data about currencies.
    rate, currencies = get_rate(currency_from, currency_to)
    # Prepare our response object.
    response = make_response(render_template('home.html',
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))
    # Add some cookie data to our response.
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS['publication']
    else:
        publication = query.lower()
    # Parse the feed. Function will download the feed, parses it and returns a Python dictionary.
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


# Get weather report.
def get_weather(query):
    # URLs can not have spaces. This fun handles this for us (it substitute spaces for "%20").
    query = urllib.parse.quote(query)
    url = WEATHER_API_URL.format(query)
    # Load the data over HTTP into a Python string.
    json_data = urllib2.urlopen(url).read()
    # Converting the JSON string that we downloaded into a Python dictionary.
    parsed = json.loads(json_data)
    weather = None
    if parsed.get("list"):
        weather = {"temperature": parsed["list"][0]["main"]["temp"],
                   "city": parsed["list"][0]["name"],
                   "description": parsed["list"][0]["weather"][0]["description"],
                   "country": parsed["list"][0]['sys']['country']}
    return weather


# Get current currency.
def get_rate(currency_from, currency_to):
    all_currency_json = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency_json).get('rates')
    frm_rate = parsed.get(currency_from.upper())
    to_rate = parsed.get(currency_to.upper())
    # return tuple
    return to_rate / frm_rate, parsed.keys()


# Get data from user input or cookies or default values.
def get_value_with_fallback(key):
    # Case when user input some data to choose:
    if request.args.get(key):
        return request.args.get(key)
    # Case when user don't made any input. We are trying to get default values from cookies:
    if request.cookies.get(key):
        return request.cookies.get(key)
    # Case when user don't made any input and we have empty cookies. We are using default hardcoded values:
    return DEFAULTS[key]

if __name__ == '__main__':
    app.run(port=5000, debug=True)
