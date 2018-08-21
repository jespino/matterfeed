import feedparser
import click
import requests
import time
import tomd


def entry_to_payload(entry, channel, username, icon_url):
    header = "#### [{}]({})".format(entry['title'], entry['link'])
    date = "Published: _{}_".format(entry['published'])
    body = tomd.convert(entry['description'])
    return {
        "channel": channel,
        "username": username,
        "icon_url": icon_url,
        "text": "\n\n".join([header, date, body])
    }


@click.command()
@click.option('--feed', prompt="Feed url", help="Url to the RSS/Atom feed")
@click.option('--webhook', prompt="Mattermost incomming webhook", help="Url of a Mattermost incomming webhook to publish the rss")
@click.option('--channel', default=None, help="Channel Name where you publish the Feed items (default: incomming webhoook configured channel).")
@click.option('--username', default=None, help="Username to publish the Feed items (default: incomming webhoook configured channel).")
@click.option('--icon-url', default=None, help="Icon url to publish the Feed items (default: incomming webhoook configured channel).")
@click.option('--interval', default=300, help="Number of seconds between checks for updates (default: 300 secons)")
@click.option('--start-date', default=0, help="Only load posts after this Unix EPOCH (default: 0 or last published post)")
def matterfeed(feed, webhook, channel, username, icon_url, interval, start_date):
    try:
        last_published_post = float(open("last_published_post", "r").read())
    except Exception:
        last_published_post = start_date

    while True:
        data = feedparser.parse(feed)
        max_post_date = last_published_post
        for entry in sorted(data.entries, key=lambda x: x['published_parsed']):
            if (time.mktime(entry['published_parsed']) > last_published_post):
                payload = entry_to_payload(entry, channel, username, icon_url)
                requests.post(webhook, json=payload)
                max_post_date = max(time.mktime(entry['published_parsed']), max_post_date)

        last_published_post = max(max_post_date, last_published_post)
        open("last_published_post", "w").write(
            "{}".format(last_published_post)
        )
        time.sleep(interval)


if __name__ == '__main__':
    matterfeed()
