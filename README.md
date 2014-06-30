# instagram-map

This is code that collates data from instagram and stores it in MongoDB, then uses that data to generate heatmaps using the geo coordinates from the images.

This is not supposed to be a code for generic heatmap generation, it is a project I did to visualize the locations of instagram images on the globe.  With that said, I did make an effort to keep things generic, so maybe it will be useful to somebody else.  If what you want to do is the following:

   * Plot data in a semitransparent heatmap over a flat-colored geographical map

Then maybe this will be of interest to you...

## Initial setup

The code expects that there is a MongoDB daemon running on localhost port 27017.  Additionally, the following three environment variables need to be set:

   * ``INSTAGRAM_CLIENT_ID`` -- Client ID for your application, generated at [instagram.com/developer](http://www.instagram.com/developer)
   * ``INSTAGRAM_CLIENT_SECRET`` -- Client secret for your application, generated at [instagram.com/developer](http://www.instagram.com/developer)
   * ``GEONAMES_USERNAME`` -- Username for your account on [geonames.org](http://www.geonames.org)

## Collection

Collect tagged photos by running ``instagram_map_collect.py``.  This is a simple program that when executed will run forever, querying Instagram for photographs with a specific tag, and dumping the results into MongoDB.  Specifically, into the database ``instagram`` and the collection ``ig``.

   * *logfile*:  Filename for the logfile
   * *tag*:  The tag to query for
   * *delay*:  The delay, in seconds, between hits to Instagram's API (default: 30)

## Visualization

Generate map visualizations by running ``instagram_map_visualize.py``.  A single run of this script will generate a move over a 24 hour period on the specified region of the world.  This script accepts the following command line options

   * *minutes_step*:  Number of minutes to advance by between frames
   * *region*: Which region to generate results for.  Valid regions are those in ``configs.py``
   * *data_dir*: Directory to dump results to (default is the current working directory)
   * *logfile*: Name of logfile to write to (default is ``instagram_map.log``)
   * *add_timezones*: If this flag is present then hit the geonames API to add timezone information to any of the photos that are not yet tagged with this.
   * *normalize_map*: If this flag is present then generate the move twice.  First time through, calculate the integrated intensities of each pixel, second time through dump out the movie, with each pixel normalized by its integrated intensity.  This means that images from otherwise quiet areas are emphasized.

For example:

```python instagram_map_visualize.py --region=World --minutes_step=60 --add_timezones --normalize_map --data_dir=data```

Will generate a map of the entire world, one frame per hour, will add timezone information to any points that are missing it, and will normalize the map to have a more uniform brightness.  There will be a total of 24 png images written to the ``data/`` subdirectory along with ``instagram_map.log``.

set -x PYTHONPATH /usr/local/lib/python2.7/site-packages/ $PYTHONPATH

## Utility functions

There are a couple utility functions

   * Describe the wordcloud one.
   * Describe the HTML page one.
