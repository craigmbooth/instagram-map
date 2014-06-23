"""Read instagram photos with a specific tag and save to Mongo"""
import argparse
from instagram.client import InstagramAPI
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from retry import retries, example_exc_handler
from extract_data import get_cursors
from time import sleep
import geonames
import logging
import os

CLIENT_ID = os.environ.get("INSTAGRAM_CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("INSTAGRAM_CLIENT_SECRET", None)

@retries(5, hook=example_exc_handler, delay=10, backoff=2)
def save_instagram_to_mongo(desired_tag):

    ig_mongo, geo = get_cursors()

    api = InstagramAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    tag_recent_media, _ = api.tag_recent_media(tag_name=desired_tag)

    batch_to_send = []
    for media in tag_recent_media:
        media_dict = {}
        media_dict["_id"] = media.id
        try:
            media_dict["latitude"] = media.location.point.latitude
            media_dict["longitude"] = media.location.point.longitude
            media_dict["created_time"] = media.created_time
            media_dict["caption"] = str(media.caption)
            media_dict["image_url"] = media.images['standard_resolution'].url
            media_dict["schema"] = 1
        except AttributeError:
            # If an instagram is missing a tag that we want, skip it
            continue

        try:
            # Times returned by Instagram are all UTC.  Use geonames
            # to add the offset so we can convert to local time
            timezone = geo.find_timezone({"lat": media_dict["latitude"],
                                          "lng": media_dict["longitude"]})
            media_dict["offset"] = timezone["rawOffset"]
        except:
            # Any failure here should be ignored because we can always
            # add this data back in later
            pass

        try:
            media_dict["tags"] = [str(x)[5:] for x in media.tags]
        except AttributeError:
            media_dict["tags"] = None

        batch_to_send.append(media_dict)

    try:
        res = ig_mongo.insert(batch_to_send, continue_on_error=True)
    except DuplicateKeyError:
        res = []

    logging.getLogger().warning("Saved "+str(len(res))+" to mongo")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Code that repeatedly hits "
        "the instagram API to get images tagged with a specific word.  Stores "
        "links to the images and GPS coordinates to MongoDB")
    parser.add_argument('--logfile', type=str, default="instagram_map.log",
                   help='Name of logfile')
    parser.add_argument('--tag', type=str, required=True,
                   help='Tag to search for')
    parser.add_argument('--delay', type=int, default=30,
                   help='Delay time between hits to the Instagram API')

    args = parser.parse_args()

    logging.basicConfig(filename=args.logfile,
                        level=logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(message)s')

    if CLIENT_ID is None:
        raise ValueError("Environment variable INSTAGRAM_CLIENT_ID must "
            "contain your client ID")
    if CLIENT_SECRET is None:
        raise ValueError("Environment variable INSTAGRAM_CLIENT_SECRET must "
            "contain your client ID")

    while True:
        save_instagram_to_mongo(args.tag)
        sleep(args.delay)
