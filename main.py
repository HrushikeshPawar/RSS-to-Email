from reader import RSSReader
import json
from tqdm import tqdm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import markdown2
import os
import sys

BLOG_PATH = 'blogs.json'
TEST_BLOG_PATH = 'test_blogs.json'
ARTICLE_PATH = 'articles.json'
TODAY = datetime(datetime.today().year, datetime.today().month, datetime.today().day)

try:
    SENDER = os.environ["SENDER"]
    RECIPIENT = os.environ["RECIPIENT"]
    PASSWORD = os.environ["PASSWORD"]
except KeyError:
    sys.exit("Environment variables not set")


def import_blogs(path: str) -> dict:
    with open(path, 'r') as f:
        blogs = json.load(f)
    return blogs


def import_articles(path: str) -> dict:
    try:
        with open(path, 'r') as f:
            articles = json.load(f)

    except FileNotFoundError:
        articles = {}
        # Save articles to json file
        with open(path, 'w') as f:
            json.dump(articles, f)

    return articles


def get_raw_articles(blogs: dict) -> dict:
    raw_articles = dict()

    for blog in tqdm(blogs, desc='Blogs'):

        # Get articles from RSS feed
        rss_reader = RSSReader(blogs[blog])

        # Extract article details from RSS feed
        raw_articles[blog] = rss_reader.articles_dicts

    return raw_articles


def update_articles(raw_articles: dict, articles: list, forDate: datetime = TODAY) -> None:
    for blog in raw_articles:

        # Check if blog is already in the articles json file
        # If not, create a new entry for the blog
        if blog not in articles:
            articles[blog] = dict()

        # Extract article details from RSS feed
        article_details = raw_articles[blog]

        for article in article_details:
            date = datetime.fromtimestamp(article_details[article]["pubdate_parsed"]).astimezone()
            date = datetime(date.year, date.month, date.day)
            # inRange = datetime(2022, 1, 1).astimezone() <= date < datetime(2022, 7, 1).astimezone()
            isDate = date - forDate == timedelta(0)

            if article not in articles[blog] and isDate:
                articles[blog][article] = article_details[article]
                articles[blog][article]['email_sent'] = False

    with open(ARTICLE_PATH, 'w') as f:
        json.dump(articles, f)
    return articles


def articles_to_mail(articles: dict) -> list:
    mail_articles = {}
    for blog in articles:

        if len(articles[blog]) < 1:
            continue

        # Start with Blog name as key
        mail_articles[blog] = dict()

        # Get articles that have not been mailed
        for article in articles[blog]:
            if not articles[blog][article]['email_sent']:
                mail_articles[blog][article] = articles[blog][article]
                articles[blog][article]['email_sent'] = True

        if mail_articles[blog] == {}:
            del mail_articles[blog]

    # Update sent articles in json file
    with open(ARTICLE_PATH, 'w') as f:
        json.dump(articles, f)

    return mail_articles


def get_content_in_html(articles: dict) -> str:

    content = ''
    cnt = 0

    for blog in articles:

        # Start with Blog name as Heading
        new_content = f'# {blog}\n'

        for article in articles[blog]:
            cnt += 1

            # Get article details
            article_details = articles[blog][article]

            # Create article heading
            new_content += f'\n## [{article}]({article_details["url"]})\n'

            # Add article details to content
            date = datetime.fromtimestamp(article_details["pubdate_parsed"]).astimezone()
            new_content += f'**Published on:** {date.strftime("%A, %d %B, %Y")}\n'
            new_content += f'\n{article_details["description"]}\n'
        new_content += u'\n---\n'
        # with open(fr'HTML\{blog}.html', 'w', encoding='utf-8') as f:
        #     f.write(markdown2.markdown(new_content))

        content += markdown2.markdown(new_content)
    # with open(r'HTML\All.html', 'w', encoding='utf-8') as f:
    #     f.write(markdown2.markdown(content))

    return content, cnt


def send_email(mail_articles: dict) -> None:

    # Setup the SMTP server
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.connect(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user=SENDER, password=PASSWORD)

    # Create required Multipart MIME objects
    multipart_msg = MIMEMultipart("alternative")
    multipart_msg["Subject"] = f"Data Science Blogs Update - {datetime.now().strftime('%A, %d %B, %Y')}"
    multipart_msg["From"] = f'Automathographer <{SENDER}>'
    multipart_msg["To"] = f'Hurshikesh <{RECIPIENT}>'

    # Create content for email
    print('\nCreating content for email...')
    content, cnt = get_content_in_html(mail_articles)
    # print(content, '\n\n\n')
    content = MIMEText(content, "html")
    multipart_msg.attach(content)
    print('Content for email created!')

    print('\nSending emails...')
    server.sendmail(SENDER, RECIPIENT, multipart_msg.as_string())
    print('Emails sent!')

    print(f'\nTotal Articles sent: {cnt}')


def check_backlog():

    # Import Blogs
    print('Importing blogs...')
    blogs = import_blogs(BLOG_PATH)
    # blogs = import_blogs(TEST_BLOG_PATH)
    print('Blogs imported!')

    # Create\Load RSS feed json file
    print('\nImporting articles...')
    articles = import_articles(ARTICLE_PATH)
    print('Articles imported!')

    # Get raw articles from RSS feed
    print('\nGetting raw articles...')
    raw_articles = get_raw_articles(blogs)
    print('Raw articles obtained!')

    # Get articles from RSS feed and update the articles json file
    edate = datetime(2022, 8, 3)
    sdate = datetime(2022, 7, 1)
    date_range = [sdate + timedelta(days=x) for x in range((edate - sdate).days)]

    for date in date_range:
        print(f'\n\n\nUpdating articles for {date.strftime("%A, %d %B, %Y")}...')
        print('\nUpdating articles...')
        articles = update_articles(raw_articles, articles, date)
        print('Articles updated!')

        # Sort articles to be mailed
        print('\nSorting articles to be mailed...')
        mail_articles = articles_to_mail(articles)
        print('Articles sorted!')

        # Check if there are articles to be mailed
        if len(mail_articles) > 0:
            # Send emails
            send_email(mail_articles)
        else:
            print('No new articles to be mailed!')

        articles = import_articles(ARTICLE_PATH)


def main():
    # Import Blogs
    print('Importing blogs...')
    blogs = import_blogs(BLOG_PATH)
    print('Blogs imported!')

    # Create\Load RSS feed old json file
    print('\nImporting articles...')
    articles = import_articles(ARTICLE_PATH)
    print('Articles imported!')

    # Get raw articles from (updated) RSS feed
    print('\nGetting raw articles...')
    raw_articles = get_raw_articles(blogs)
    print('Raw articles obtained!')

    # Update the articles json file
    print('\nUpdating articles...')
    articles = update_articles(raw_articles, articles)
    print('Articles updated!')

    # Sort articles to be mailed
    print('\nSorting articles to be mailed...')
    mail_articles = articles_to_mail(articles)
    print('Articles sorted!')

    # Check if there are articles to be mailed
    if len(mail_articles) > 0:
        # Send emails
        send_email(mail_articles)
    else:
        print('No new articles to be mailed!')


if __name__ == "__main__":
    main()
