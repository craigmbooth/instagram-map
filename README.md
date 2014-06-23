# instagram-map

Python code to mine data from Instagram and animate heatmaps of this data.

## Initial setup

The code expects that there is a MongoDB daemon running on localhost port 27017.  Additionally, the following three environment variables need to be set:

   * ``INSTAGRAM_CLIENT_ID`` -- Client ID for your application, generated at [instagram.com](http://www.instagram.com/developer)
   * ``INSTAGRAM_CLIENT_SECRET`` -- Client secret for your application, generated at [instagram.com](http://www.instagram.com/developer)
   * ``GEONAMES_USERNAME`` -- Username for your account on [geonames.org](http://www.geonames.org)

## Collection

Collect tagged photos by running ``instagram_map_collect.py``.  This is a simple program that when executed will run forever, querying Instagram for photographs with a specific tag, and dumping the results into MongoDB.  Specifically, into the database ``instagram`` and the collection ``ig``.

   * logfile
   * tag
   * delay

## Visualization

Generate map visualizations by running ``instagram_map_visualize.py``.

   * minutes_step
   * region
   * add_timezones
   * data_dir
   * logfile

## An example run

set -x PYTHONPATH /usr/local/lib/python2.7/site-packages/ $PYTHONPATH
