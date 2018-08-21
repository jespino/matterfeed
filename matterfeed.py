import feedparser
import click
import requests
import time
import html2text
import dbm


def entry_to_payload(entry, channel, username, icon_url):
    header = "#### [{}]({})".format(html2text.html2text(entry['title']), entry['link'])
    date = "Published: _{}_".format(entry['published'])
    body = html2text.html2text(entry['description'] or entry['summary'] or "")
    return {
        "channel": channel,
        "username": username,
        "icon_url": icon_url,
        "text": "\n\n".join([header, date, body])
    }


def get_last_published_post_date(dbstring, feed, channel):
    key = "{}-{}".format(feed, channel)
    if dbstring.startswith("file://"):
        with dbm.open(dbstring[7:], 'r') as db:
            return float(db[key]) or 0

    if dbstring.startswith("postgres://"):
        import psycopg2
        conn = psycopg2.connect(dbstring[11:])
        cur = conn.cursor()
        cur.execute("SELECT date FROM matterfeed WHERE feed=%s", (key,))
        feed_date = cur.fetchone()
        return feed_date[0]


def set_last_published_post_date(dbstring, feed, channel, date):
    key = "{}-{}".format(feed, channel)
    if dbstring.startswith("file://"):
        with dbm.open(dbstring[7:], 'c') as db:
            db[key] = str(date)

    if dbstring.startswith("postgres://"):
        import psycopg2
        conn = psycopg2.connect(dbstring[11:])
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS matterfeed(feed varchar UNIQUE, date float);")
        cur.execute("UPDATE matterfeed SET date=%s WHERE feed=%s", (date, key))
        cur.execute(
            "INSERT INTO matterfeed (feed, date) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM matterfeed WHERE feed=%s)", (key, date, key))
        conn.commit()
        cur.close()
        conn.close()


@click.command()
@click.option('--feed', envvar="MATTERFEED_FEED", prompt="Feed url", help="Url to the RSS/Atom feed (Env MATTERFEED_FEED)")
@click.option('--webhook', envvar="MATTERFEED_WEBHOOK", prompt="Mattermost incomming webhook", help="Url of a Mattermost incomming webhook to publish the rss (Env MATTERFEED_WEBHOOK)")
@click.option('--channel', envvar="MATTERFEED_CHANNEL", default=None, help="Channel Name where you publish the Feed items (default: incomming webhoook configured channel). (Env MATTERFEED_CHANNEL)")
@click.option('--username', envvar="MATTERFEED_USERNAME", default=None, help="Username to publish the Feed items (default: incomming webhoook configured channel). (Env MATTERFEED_USERNAME)")
@click.option('--icon-url', envvar="MATTERFEED_ICON_URL", default=None, help="Icon url to publish the Feed items (default: incomming webhoook configured channel). (Env MATTERFEED_ICON_URL)")
@click.option('--interval', envvar="MATTERFEED_INTERVAL", default=300, help="Number of seconds between checks for updates (default: 300 secons) (Env MATTERFEED_INTERVAL)")
@click.option('--start-date', envvar="MATTERFEED_START_DATE", default=0, help="Only load posts after this Unix EPOCH (default: 0 or last published post) (Env MATTERFEED_START_DATE)")
@click.option('--db', envvar="MATTERFEED_DB", default="file://matterfeed.db", help="DB used to store the most recent published post date (Env MATTERFEED_DB)")
def matterfeed(feed, webhook, channel, username, icon_url, interval, start_date, db):
    try:
        last_published_post = get_last_published_post_date(db, feed, channel)
    except Exception:
        last_published_post = start_date

    while True:
        data = feedparser.parse(feed)
        max_post_date = last_published_post
        for entry in sorted(data.entries, key=lambda x: x['published_parsed']):
            if (time.mktime(entry['published_parsed']) > last_published_post):
                payload = entry_to_payload(entry, channel, username, icon_url)
                requests.post(webhook, json=payload)
                max_post_date = max(time.mktime(
                    entry['published_parsed']), max_post_date)

        last_published_post = max(max_post_date, last_published_post)
        set_last_published_post_date(db, feed, channel, last_published_post)
        time.sleep(interval)


if __name__ == '__main__':
    matterfeed()
