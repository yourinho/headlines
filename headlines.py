# Import for the new library.
import feedparser
from flask import Flask

app = Flask(__name__)

# Build a Python dict with all our RSS feeds.
RSS_FEEDS = {'habr': 'https://habrahabr.ru/rss/hubs/all/',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest'}


# We can have more than one decorator per function.
@app.route("/")
@app.route("/<publication>")
# We keep our default value for the publication parameter.
def get_news(publication="habr"):
    # Parse the feed. Function will download the feed, parses it and returns a Python dictionary.
    feed = feedparser.parse(RSS_FEEDS[publication])
    # Get the first item of feed.
    first_article = feed['entries'][0]
    if not first_article:
        return "no news is good news"
    else:
        return """<html>
                        <body>
                            <h1> Headlines </h1>
                            <b>{0}</b> <br/>
                            <i>{1}</i> <br/>
                            <p>{2}</p> <br/>
                        </body>
                    </html>""".format(first_article.get("title"),
                                      first_article.get("published"),
                                      first_article.get("summary"))


if __name__ == '__main__':
    app.run(port=5000, debug=True)
