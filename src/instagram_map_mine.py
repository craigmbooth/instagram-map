"""Read instagram photos with a specific tag and save to Mongo"""
from instagram.client import InstagramAPI
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import pprint
from retry import retries, example_exc_handler
from time import sleep
import geonames
import logging
import os

LOGGER = logging.getLogger()
CLIENT_ID = os.environ.get("INSTAGRAM_CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("INSTAGRAM_CLIENT_SECRET", None)

@retries(5, hook=example_exc_handler, delay=10, backoff=2)
def save_instagram_to_mongo(desired_tag):

    client = MongoClient()
    geo = geonames.GeonamesClient("craigmbooth")
    db = client.instagram
    api = InstagramAPI(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    ig_mongo = db.ig

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

    LOGGER.warning("Saved "+str(len(res))+" to mongo")

def initialize_run():
    """Initialize"""

    fh = logging.FileHandler("instagram.log")
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    LOGGER.addHandler(fh)

    LOGGER.info("Entering main loop")

    if CLIENT_ID is None:
        raise TypeError
    if CLIENT_SECRET is None:
        raise TypeError

if __name__ == "__main__":

    initialize_run()

    while True:
        save_instagram_to_mongo("sunset")
        sleep(30)
