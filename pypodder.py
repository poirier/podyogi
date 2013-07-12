import json
import operator
import os
import time

import feedparser
import requests

status_filename = "status.json"
download_dir = "/home/poirier/Dropbox/podcasts"


DEFAULT_MAX_DOWNLOADS = 1

podcasts = [
    {
        'name': "It's All Politics",
        'url': 'http://www.npr.org/rss/podcast.php?id=510068',
    },
    {
        'name': "Skeptoid",
        'url': 'http://skeptoid.com/podcast.xml',
    },
    {
        'name': "Skeptics' Guide to the Universe",
        'url': "http://www.theskepticsguide.org/feed/rss.aspx?feed=SGU",
    },
    {
        'name': 'FFRF',
        'url': "http://ffrf.libsyn.com/rss",
    },
    {'name': 'The Humanist Hour', 'url': "http://feeds.feedburner.com/HNN_Podcast"},
    {'name': 'Diane Rehm Friday News Roundup', 'url': "http://www.npr.org/rss/podcast.php?id=510024&amp;uid=p1qe4e85742c986fdb81d2d38ffa0d5d53"},
    {'name': 'Point of Inquiry', 'url': "http://pointofinquiry.libsyn.com/rss"}
]


def load_status():
    """Return status object"""
    status = None
    if os.path.exists(status_filename):
        try:
            with open(status_filename, "r") as f:
                status = json.load(f)
        except:
            pass
    if not status:
        status = {
            'feeds': {},
        }
    if not 'feeds' in status:
        status['feeds'] = {}
    if 'downloaded_urls' in status:
        del status['downloaded_urls']
    return status


def save_status(status):
    """Save status object"""
    with open(status_filename, "w") as f:
        json.dump(status, f, indent=2)


def do_podcast(podcast, status):
    print("Podcast: %s" % podcast['name'])
    podcast_url = podcast['url']
    feed_status = status['feeds'].get(podcast_url, {
        'downloaded_urls': [],
        'etag': None,
        'modified': None,
    })

    # Get the current feed
    d = feedparser.parse(podcast_url,
                         etag=feed_status['etag'],
                         modified=feed_status['modified'])

    # with open("feed.xml", "rb") as f:
    #     d = feedparser.parse(f, etag=etag, modified=modified)

    if d.get('status', 200) == 304:
        print("Feed not modified, skipping")
        return

    feed_title = d.feed.title
    print("Feed title: %s, there are %d items" % (feed_title, len(d.entries)))
    max_downloads = podcast.get('max_downloads', DEFAULT_MAX_DOWNLOADS)

    entries = d.entries
    # Sort entries by publish date
    entries.sort(key=operator.attrgetter('published_parsed'))
    # Then reverse, so most recent is first
    entries.reverse()

    feed_downloads = 0
    at_max = False
    done = False
    for item in d.entries[:max_downloads]:
        if done:
            break
        item_title = item.title
        item_date = item.published

        possible_times = []
        for time_field in ['published', 'created', 'updated']:
            full_field = time_field + "_parsed"
            if full_field in item:
                possible_times.append(tuple(item[full_field]))

        item_parsed_date = max(possible_times)
        formatted_date = time.strftime("%Y-%m-%d %H:%M:%S", item_parsed_date)

        for e in item.enclosures:
            if done:
                break

            enclosure_type = e['type']
            if enclosure_type in ('audio/mpeg', 'audio/x-mp3'):
                url = e['href']
                if url in feed_status['downloaded_urls']:
                    # print("Previously downloaded %s, skipping" % url)
                    continue
                if at_max:
                    # print("At max, skipping")
                    # Mark this one downloaded so we don't try again
                    feed_status['downloaded_urls'].append(url)
                    continue

                print(repr(e))
                print("length s=%r" % e['length'])
                length = int(e['length'])
                print("%s from %s at %s, %d bytes" % (item_title, item_date, url, length))

                filename = "%s %s %s.mp3" % (feed_title, item_title, formatted_date)
                filename = os.path.join(download_dir, filename)

                if os.path.exists(filename):
                    if length and os.stat(filename).st_size == length:
                        print("File already exists and is the right size, skipping")
                        feed_status['downloaded_urls'].append(url)
                        if feed_downloads >= max_downloads:
                            print("Reached podcast's max downloads (%d)" % max_downloads)
                            at_max = True
                        continue
                    else:
                        print("File exists but is wrong size, will download again")

                # FIXME: if these get too big, will we need to stream them to the file?
                r = requests.get(url, stream=True)
                content_length = int(r.headers['content-length'])
                print("content-length=%d" % content_length)
                if length and content_length != length:
                    raise IOError("content length is wrong!")
                with open(filename, "wb") as f:
                    f.write(r.content)
                file_size = os.stat(filename).st_size
                if length and file_size != length:
                    print("File is wrong size - should be %d bytes, is %d bytes" % (length, file_size))
                    raise IOError("Problem downloading file: %s" % url)
                print("downloaded %s to %s" % (url, filename))
                feed_status['downloaded_urls'].append(url)
                feed_downloads += 1
                if feed_downloads >= max_downloads:
                    print("Reached podcast's max downloads (%d)" % max_downloads)
                    at_max = True
            else:
                print("Unexpected enclosure type: %s" % enclosure_type)

    feed_status['etag'] = d.get('etag', None)
    feed_status['modified'] = d.get('modified', None)
    status['feeds'][podcast_url] = feed_status

status = load_status()
try:
    for podcast in podcasts:
        do_podcast(podcast, status)
finally:
    save_status(status)
