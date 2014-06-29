import os
import argparse
import pymongo
import numpy as np
from scipy.ndimage.filters import gaussian_filter
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches
import datetime
import logging

from configs import (cameras, ValidRegions)
from extract_data import (add_timezone_info, read_results_from_mongo)
from utils import TimedLogger

def fix_opacity_and_color_map(x, opacity_thresh=0.1, max_opacity=0.8):
    """"Given a 2d image, x, get rgbt values for each pixel and modify
    opacity values"""
    tmp = cm.hot(x)
    im_max = np.max(x)
    for i in xrange(tmp.shape[0]):
        for j in xrange(tmp.shape[1]):
            if x[i,j]/im_max > opacity_thresh:
                tmp[i,j][3] = max_opacity
            else:
                tmp[i,j][3] = max_opacity * (1./opacity_thresh)*x[i,j]/im_max
    return tmp

def add_time_labels(fig, background_color="#FFFFFF"):
    """Adds time labels to the plot"""

    #Axes with range [0,1] to allow for easy absolute positioning of text
    ax = fig.add_axes([0,0,1,1])

    # axes coordinates are 0,0 is bottom left and 1,1 is upper right
    p = patches.Rectangle(
        (0, 0), 1, 1,
        fill=True, transform=ax.transAxes, clip_on=False, color=background_color
    )
    ax.add_patch(p)

    font_kwargs = {"color": "white", "fontsize": 40, "transform": ax.transAxes}

    gmt_time = target_time - datetime.timedelta(hours=0)
    ax.text(0.5, 0.02, gmt_time.strftime("%I%p GMT"),
        horizontalalignment='center',
        verticalalignment='bottom',
        **font_kwargs)

    eastern_time = target_time - datetime.timedelta(hours=4)
    ax.text(0.02, 0.02, eastern_time.strftime("%I%p EST"),
        horizontalalignment='left',
        verticalalignment='bottom',
        **font_kwargs)

    aest_time = target_time + datetime.timedelta(hours=10)
    ax.text(0.98, 0.02, aest_time.strftime("%I%p AEST"),
        horizontalalignment='right',
        verticalalignment='bottom',
        **font_kwargs)

    ax.set_axis_off()


def make_map(target_time, camera, lons, lats, weights, gauss_sigma=1,
             sea_color="#111111", land_color="#888888", nheatmapbins=500,
             file_prefix="USA", show_plot=False, opacity_thresh=0.1,
             max_opacity=0.8):
    """Makes a single image"""

    fig = plt.gcf()

    fig = plt.figure()
    fig.set_size_inches(16,9)
    plt.clf()

    add_time_labels(fig, background_color=sea_color)

    m = Basemap(
            projection=camera["projection"],
            resolution=camera["resolution"],
            **camera["projection_kwargs"])
    m.drawcoastlines(color=sea_color)
    m.drawcountries(color=sea_color)
    m.drawstates(color=sea_color)
    m.drawmapboundary(fill_color=sea_color)
    m.fillcontinents(color=land_color,lake_color=sea_color)

    xpoints,ypoints = m(lons,lats)
    im, xedges, yedges = np.histogram2d(xpoints, ypoints,
                                    range=((m.llcrnrx, m.urcrnrx),
                                           (m.llcrnry, m.urcrnry)),
                                    bins=(nheatmapbins, (9./16.)*nheatmapbins),
                                    weights=weights)

    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    im = np.log(np.rot90(im)+1)
    im = gaussian_filter(im, gauss_sigma)

    plt.imshow(fix_opacity_and_color_map(im, max_opacity=max_opacity,
                                         opacity_thresh=opacity_thresh),
                extent=extent, zorder=10)

    logging.getLogger().info("Saving file : "+file_prefix+".png")

    if show_plot:
        plt.show()

    plt.savefig(file_prefix+".png")


def calculate_point_weights(points, time, decay_hours=1):
    """For each of the lat and lng points calculate a weight.
    Point weights should drop off as the associated time falls further into
    the past"""

    lat = []
    lon = []
    weights = []
    for res in points:
        image_time = res["created_time"]

        #Time to the nearest minute from the photo being taken to now:
        #+ve times mean that the photo was taken earlier than now.
        dt_in_minutes = (60*(time.hour - image_time.hour) +
                            (time.minute-image_time.minute))
        if dt_in_minutes < 0:
            dt_in_minutes = dt_in_minutes + 24*60

        weight = np.exp(-float(dt_in_minutes)/60/decay_hours)

        if weight > 1e-30:
            lat.append(res["latitude"])
            lon.append(res["longitude"])
            weights.append(weight)
    return lat, lon, weights


if __name__ == "__main__":
    """If run directly from the command line, parse arguments and write
    movie frames"""

    parser = argparse.ArgumentParser(description="Code that reads points from "
        "a MongoDB database, and makes movie frames showing how the points "
        "are distributed on a map")
    parser.add_argument('--minutes_step', type=int, default=60,
                   help='number of minutes to advance for each frame')
    parser.add_argument('--region', type=ValidRegions, default="World",
                   help='Select which of the configs in config.py to use, by '
                   'dictionary key.  Allowed values : \n%s' % cameras.keys())
    parser.add_argument('--add_timezones', action="count",
                   help='If present then add timezone offsets to any DB '
                   'elements that are missing them')
    parser.add_argument('--data_dir', type=str, default="data",
                   help='Path to store output images')
    parser.add_argument('--logfile', type=str, default="instagram_map.log",
                   help='Name of logfile')

    args = parser.parse_args()

    max_opacity = cameras[args.region].get("max_opacity", 0.8)
    opacity_thresh = cameras[args.region].get("max_opacity", 0.1)

    logging.getLogger().info("Setting region=%s" % args.region)
    logging.getLogger().info("Setting max_opacity=%f" % max_opacity)
    logging.getLogger().info("Setting opacity_thresh=%f" % opacity_thresh)

    logging.basicConfig(filename=os.path.join(args.data_dir, args.logfile),
                        level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s')

    if args.add_timezones:
        with TimedLogger("Adding missing timezone info", logging.getLogger()):
            add_timezone_info()

    with TimedLogger("Reading full dataset from MongoDB", logging.getLogger()):
        full_results = read_results_from_mongo()

    timedelta = datetime.timedelta(minutes=args.minutes_step)
    target_time = datetime.datetime(2014, 1, 1, 0,0,0)
    while target_time.day == 1:
        target_time += timedelta
        logging.getLogger().info("Calculating for time %s" %
                                 target_time.strftime("%H:%M"))
        lat, lon, weights = calculate_point_weights(full_results,
                                                    target_time, decay_hours=1)

        file_prefix = os.path.join(args.data_dir,
                                   args.region+target_time.strftime("%H%M"))

        with TimedLogger("Writing frame with prefix %s" % file_prefix,
                         logging.getLogger()):
            make_map(target_time, cameras[args.region], lon, lat, weights,
                     gauss_sigma=1, show_plot=False, file_prefix=file_prefix,
                     opacity_thresh=opacity_thresh, max_opacity=max_opacity)

    logging.getLogger().info("instagram_map_visualize is COMPLETE")
