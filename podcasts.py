import logging
import operator
import os
import sys
import time
import feedparser
import requests


log = logging.getLogger()


def do_podcast(podcast, status, destdir, default_max_downloads):

    log.info("Podcast: %s" % podcast['name'])

    podcast_url = podcast['url']
    feed_status = status['feeds'].get(podcast_url, {
        'downloaded_urls': [],
        'etag': None,
        'modified': None,
    })

    headers = {}
    if feed_status['etag']:
        headers['If-None-Match'] = feed_status['etag']
        print("Using etag")
    if feed_status['modified']:
        headers['If-Modified-Since'] = feed_status['modified']
        print("Using modified")
    kwargs = {}
    if 'userid' in podcast:
        kwargs['auth'] = (podcast['userid'], podcast['password'])
    r = requests.get(podcast_url,
                     headers=headers,
                     **kwargs)
    if r.status_code == 304:
        log.debug("Feed not modified, skipping")
        #print("Feed not modified, skipping")
        return

    xml = r.content

    # Get the current feed
    d = feedparser.parse(xml)

    feed_title = d.feed.get('title', 'NO TITLE')
    log.debug("Feed title: %s, there are %d items" % (feed_title, len(d.entries)))
    max_downloads = podcast.get('max_downloads', default_max_downloads)

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
                    # log.debug("Previously downloaded %s, skipping" % url)
                    # print("Previously downloaded %s, skipping" % url)
                    continue
                if at_max:
                    # log.debug("At max, skipping")
                    print("At max, skipping (and marking downloaded)")
                    # Mark this one downloaded so we don't try again
                    feed_status['downloaded_urls'].append(url)
                    continue

                log.debug(repr(e))
                log.debug("length s=%r" % e['length'])
                length = int(e['length'])
                log.debug("%s from %s at %s, %d bytes" % (item_title, item_date, url, length))

                filename = "%s %s %s.mp3" % (feed_title, item_title, formatted_date)
                filename = os.path.join(destdir, filename)

                if os.path.exists(filename):
                    if length and os.stat(filename).st_size == length:
                        log.debug("File %s already exists and is the right size, skipping" % filename)
                        print("File %s already exists and is the right size, skipping" % filename)
                        feed_status['downloaded_urls'].append(url)
                        if feed_downloads >= max_downloads:
                            log.debug("Reached podcast's max downloads (%d)" % max_downloads)
                            print("Reached podcast's max downloads (%d)" % max_downloads)
                            at_max = True
                        continue
                    else:
                        log.debug("File %s exists but is wrong size, will download again" % filename)
                        print("File %s exists but is wrong size, will download again" % filename)

                # FIXME: if these get too big, will we need to stream them to the file?
                r = requests.get(url, stream=True)
                content_length = int(r.headers['content-length'])
                log.debug("content-length=%d" % content_length)
                if length and length != 100000 and content_length != length:
                    print("WARNING: content length is wrong! length=%d, content_length=%d" % (length, content_length))
                with open(filename, "wb") as f:
                    f.write(r.content)
                file_size = os.stat(filename).st_size
                if not file_size:
                    print("PROBLEM downloading file: file is empty! %s" % filename)
                    os.remove(filename)
                    continue
                if length and length != 100000 and file_size != length:
                    log.debug("File is wrong size - should be %d bytes, is %d bytes" % (length, file_size))
                    print("Problem downloading file (wrong size): %s" % url)
                log.info("Downloaded %s to %s" % (item_title, filename))
                feed_status['downloaded_urls'].append(url)
                feed_downloads += 1
                if feed_downloads >= max_downloads:
                    log.debug("Reached podcast's max downloads (%d)" % max_downloads)
                    at_max = True
            else:
                log.error("Unexpected enclosure type: %s" % enclosure_type)
                continue
                #sys.exit(1)

    feed_status['etag'] = r.headers.get('etag', None)
    feed_status['modified'] = r.headers.get('modified', None)
    status['feeds'][podcast_url] = feed_status
