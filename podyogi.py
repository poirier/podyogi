import argparse
import json
import logging
import os
import sys

from misc_io import save_status, load_status, create_example_podcasts_file
from podcasts import do_podcast


HOME = os.environ['HOME']

log_level_names = [x for x in logging._levelNames
                   if isinstance(x, str) and x != 'NOTSET']

parser = argparse.ArgumentParser(description="Download some podcasts")
parser.add_argument("--configdir", dest="configdir",
                    help="Directory where configuration and status files "
                         "are stored (default: $HOME/.config/podyogi)",
                    default=os.path.join(HOME, ".config/podyogi"))
parser.add_argument("--destdir", dest="destdir",
                    help="Directory where podcasts are downloaded",
                    required=True)
parser.add_argument("--initialize", dest="initialize",
                    action='store_true',
                    help="Create CONFIGDIR and/or example podcasts file "
                         "(CONFIGDIR/podcasts.json) if none found",
                    default=False)
parser.add_argument("--loglevel", dest="loglevel",
                    choices=log_level_names,
                    default='INFO',
                    help="Output level - default=INFO")
parser.add_argument("--max-downloads", dest="max_downloads",
                    default=1,
                    type=int,
                    help="Default limit to how many of the most recent "
                         "items in the feed will be considered. Individual "
                         "podcasts can override.")
args = parser.parse_args()

log = logging.getLogger()
log.setLevel(args.loglevel)
log.addHandler(logging.StreamHandler())

if not os.path.isdir(args.configdir):
    if args.initialize:
        os.makedirs(args.configdir)
    else:
        log.error("Config dir does not exist and --initialize not specified:"
                  " %s" % args.configdir)
        sys.exit(1)

if not os.path.isdir(args.destdir):
    # To ensure we don't try creating a directory that we shouldn't (e.g.
    # if destdir points into a file system that ought to be mounted but
    # isn't), don't create the destination directory; just fail.
    log.error("Destination dir %s does not exist." % args.destdir)
    sys.exit(1)

podcasts_file = os.path.join(args.configdir, "podcasts.json")
if not os.path.exists(podcasts_file):
    if args.initialize:
        create_example_podcasts_file(podcasts_file)
        print("Created example podcasts file %s, please review and edit"
              % podcasts_file)
    else:
        log.error("Podcasts file %s not found, pass --initialize to "
                  "create example file" % podcasts_file)
    sys.exit(1)

with open(os.path.join(podcasts_file, "r")) as f:
    podcasts = json.load(f)

status_filename = os.path.join(args.configdir, "status.json")
status = load_status(status_filename)

try:
    for podcast in podcasts:
        do_podcast(podcast, status, args.destdir, args.max_downloads)
finally:
    save_status(status, status_filename)
