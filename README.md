MatterFeed
==========

MatterFeed is a small script to use in combination with the Mattermost
incomming webhooks to provide rss/atom syndication in mattermost channels.

Build with docker
-----------------

```sh
docker build -t matterfeed .
```

Run with docker
---------------

You can run directly with docker using:

```sh
docker run -v last_published_post:last_published_post \
           -e MATTERFEED_FEED=<your-feed-url> \
           -e MATTERFEED_WEBHOOK=<your-incomming-webhook-url> \
           --rm --name matterfeed jespino/matterfeed
```

You can see the entire help using:

```sh
docker run --rm --name matterfeed jespino/matterfeed python matterfeed.py --help
```

Installation
------------

If you want install it in your machine without using docker, you can.

You need to clone the repository:

```
git clone github.com/jespino/matterfeed.git
cd matterfeed
```

Create your own virtualenv, for example:

```
mkvirtualenv matterfeed
```

Install the requirements

```
pip install -r requirements.txt
```

and run the application:

```
python ./matterfeed.py --help
```

How to Contribute?
------------------

Just open an issue or PR ;)

License
-------

Matteractions is licensed under BSD (2-Clause) license.
