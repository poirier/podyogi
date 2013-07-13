import json
import logging
import os
import sys


log = logging.getLogger()

def save_status(status, filename):
    """Save status object"""
    with open(filename, "w") as f:
        json.dump(status, f, indent=2)


def create_example_podcasts_file(filename):
    podcasts = [
        {
            'name': "It's All Politics",
            'url': 'http://www.npr.org/rss/podcast.php?id=510068',
        },
        {
            'name': 'Diane Rehm Friday News Roundup',
            'url': "http://www.npr.org/rss/podcast.php?id=510024&amp;uid=p1qe4e85742c986fdb81d2d38ffa0d5d53",
            'max_downloads': 2,   # 2 podcasts released on same day
        },
    ]
    with open(filename, "w") as f:
        json.dump(podcasts, f, indent=2)


def load_status(filename):
    """Return status object"""

    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                status = json.load(f)
        except IOError:
            log.exception("Error reading status file: %s" % filename)
            sys.exit(1)
    else:
        log.error("Status file does not exist: %s, starting with "
                  "initial status" % filename)
        status = {
            'feeds': {},
        }

    return status
