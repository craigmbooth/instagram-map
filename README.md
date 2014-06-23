# instagram-map

Python code to mine data from Instagram and animate heatmaps of this data.

## Initial setup

The code expects that there is a MongoDB daemon running on localhost port 27017.  Additionally, the following three environment variables need to be set:

   * ``INSTAGRAM_CLIENT_ID``
   * ``INSTAGRAM_CLIENT_SECRET``
   * ``GEONAMES_USERNAME``

## Collection

Collect tagged photos by running ``instagram_map_collect.py``.

## Visualization

Generate map visualizations by running ``instagram_map_visualize.py``.

set -x PYTHONPATH /usr/local/lib/python2.7/site-packages/ $PYTHONPATH
