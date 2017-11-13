# Import for the new library.
import feedparser
from flask import Flask
from flask import render_template
from flask import request


app = Flask(__name__)

# Build a Python dict with all our RSS feeds.
RSS_FEEDS = {'habr': 'https://habrahabr.ru/rss/hubs/all/',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest'}


# We can have more than one decorator per function.
@app.route("/")
def get_news():
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = "habr"
    else:
        publication = query.lower()
    # Parse the feed. Function will download the feed, parses it and returns a Python dictionary.
    feed = feedparser.parse(RSS_FEEDS[publication])
    # Rendering our template with parameters (send data to view).
    return render_template("home.html", articles=feed['entries'], count=len(feed['entries']))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
