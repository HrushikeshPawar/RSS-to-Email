import feedparser
from datetime import datetime


class RSSReader:

    def __init__(self, url: str) -> None:
        self.url = url

        # Parse the RSS feed
        self.feed = feedparser.parse(self.url)

        # Get the articles from the feed
        self.articles = self.feed.entries

        # Create Article dict
        self.articles_dicts = {
            a.title : {
                'url': a.link,
                'description': a.description if 'description' in a else None,
                'pubdate': a.published,
                'pubdate_parsed': (a.published_parsed[0], a.published_parsed[1], a.published_parsed[2])
            } for a in self.articles
        }

    def print_info(self):
        for article in self.articles_dicts:
            print(self.articles_dicts[article]['pubdate'], '|', self.articles_dicts[article]['pubdate_parsed'],  '|', article)

    def print_article_by_date(self, date: datetime = datetime.now()):
        for i in range(len(self.articles_dicts)):
            if self.articles_dicts[i]['pubdate_parsed'] >= date:
                print(self.articles_dicts[i]['pubdate'], '|', self.articles_dicts[i]['title'])


if __name__ == '__main__':

    links = [
        'https://www.deepmind.com/blog/rss.xml',  # DeepMind Blog
        'https://blogs.nvidia.com/feed/',  # Nvidia Blog
        'https://blog.ml.cmu.edu/feed/',  # CMU Machine Learning Blog
        'https://blog.tensorflow.org/feeds/posts/default?alt=rss',  # TensorFlow Blog
        'https://machinelearningmastery.com/feed/',  # Machine Learning Mastery Blog
        'https://colah.github.io/rss.xml',  # colah's blog
        'https://www.amazon.science/index.rss',  # Amazon's blog
        'https://bair.berkeley.edu/blog/feed.xml',  # The Berkeley Artificial Intelligence Research Blog
        'https://blog.google/technology/ai/rss/',  # Google's AI blog
        'https://openai.com/blog/rss/',  # OpenAI's blog
        'https://machinelearning.apple.com/rss.xml',  # Apple's Machine Learning blog
        'https://feeds.feedburner.com/towards-ai/',  # Towards AI blog
        'https://www.louisbouchard.ai/rss/',  # Louis Bouchard's blog
        'https://computational-intelligence.blogspot.com/feeds/posts/default',  # Computational Intelligence blog
        'https://www.topbots.com/feed/',  # TopBots blog
    ]

    feed = RSSReader('https://lilianweng.github.io/index.xml')
    # for url in feed.urls:
    #     print(url)
    feed.print_info()
    # feed.print_article_by_date(date=datetime(2022, 7, 19))
    # print(feed.articles_dicts)
