"""Functionality to add timezone offset relative to UTC to any entries in
the instagram mongo table that requires them"""
import os
import pymongo
import geonames
import logging

def get_cursors():
    """Return cursor connections to the MongoDB database and to Geonames"""

    geonames_username = os.environ.get("GEONAMES_USERNAME", None)
    if geonames_username is None:
        raise ValueError("GEONAMES_USERNAME must be set to your username")
    ig_mongo = pymongo.MongoClient().instagram.ig
    geo = geonames.GeonamesClient(geonames_username)
    return ig_mongo, geo


def read_results_from_mongo():
    """Read all of the results from MongoDB"""
    ig_mongo, _ = get_cursors()
    full_results = []
    for res in ig_mongo.find():
        if (res["latitude"] > -90 and res["latitude"] < 90 and
            res["longitude"] > -180 and res["longitude"] < 180):
            full_results.append(res)
    logging.getLogger().info("Total number of points in sample : %d" %
                              len(full_results))
    return full_results


def add_timezone_info():

    ig_mongo, geo = get_cursors()

    num_added = 0
    for res in ig_mongo.find():
        if "offset" in res:
            continue
        try:
            timezone = geo.find_timezone({"lat": res["latitude"],
                                  "lng": res["longitude"]})
            res["offset"] = timezone["rawOffset"]
            ig_mongo.save(res)
            num_added += 1
        except geonames.GeonamesError, e:
            logging.getLogger().warn("GeonamesError for lat: %f, lng: %f " %
                   (res["latitude"], res["longitude"]))
            logging.getLogger().warn("GeonamesError message : "+str(e))

    logging.getLogger().info("Added %d missing offsets to data" % num_added)
