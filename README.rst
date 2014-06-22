Podyogi
=======

Podyogi is a command line podcatcher: a program to download podcasts.

Target users
------------

Podyogi is intended for users who are comfortable with Python programs.
That's not an apology, just a statement of who I am writing it for.

If you're more comfortable with
Ruby, you might prefer to look at Armangil's Podcatcher. Or if you like
shell scripts, there's Bashpodder. And of course, there are a lot of
GUI programs that claim podcast support.

Installation
------------

Install should be as simple as:

    pip install podyogi

though it isn't yet. For now, it's more like:

    git clone THE_REPO
    cd podyogi
    python setup.py develop

In either case, I highly recommend installing it into a virtualenv.

TEMP MAYBE:

sudo apt-get install python3-dev libtag1-dev
pip install cython

Quick start
-----------

By default, podyogi stores its configuration and status files in
`$HOME/.config/podyogi`. You can override that by passing
`--configdir=ANOTHERPATH`, though for now you'll have to do that
every time it runs.

The first time you run `podyogi`, run it with the `--initialize` flag
to set up the configuration::

    podyogi --initialize

That will create files in the configuration directory. The one to
look at right now is `podcasts.json`, which will now contain a few
example podcast subscriptions. Edit that file to subscribe to the
podcasts you're interested in.

Each podcast is represented by a dictionary with the following keys:

    name: string - a descriptive title for the feed. This is just for your benefit;
        it's only used in podyogi output and logging.
    url: string - the URL of the feed. This is the URL that typically ends with .xml
        or .rss. At any rate, it should point at the XML feed.
    max_downloads: (optional) integer - by default, podyogi will only look
        at the most recent item in the feed (since some feeds list every
        podcast in the last 10 years and it's assumed you don't want to
        download them all). You can use `max_downloads` to tell podyogi to
        look at more of the recent items. For example, if max_downloads is
        2, podyogi will look at the 2 most recent items, and download them
        if it hasn't already.

Now, run podyogi again, without `--initialize` but add `--destdir` and specify
an existing directory where the podcasts should be downloaded. It should
download one (or more - see max_downloads) of the most recent podcasts from
each feed.  By default, it'll download to a file named something like:

    <FEED TITLE> <ITEM TITLE> <DATE>.mp3

Why is it called podyogi
------------------------

Because it's a podcatcher, and Yogi Berra was a catcher. Also,
`pypodder` has already been used a zillion times already.
