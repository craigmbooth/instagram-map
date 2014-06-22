"""Functionality to add timezone offset relative to UTC to any entries in
the instagram mongo table that requires them"""
import pymongo
import geonames
import logging

def get_cursors():
    ig_mongo = pymongo.MongoClient().instagram.ig
    geo = geonames.GeonamesClient("craigmbooth")
    return ig_mongo, geo


def read_results_from_mongo():
    ig_mongo, _ = get_cursors()
    full_results = []
    for res in ig_mongo.find():
        if (res["latitude"] > -90 and res["latitude"] < 90 and
            res["longitude"] > -180 and res["longitude"] < 180):
            full_results.append(res)
    logging.getLogger().info("Total number of points in sample : %d" %
                              len(full_results))
    return full_results


def dump_images_to_html():
    ig_mongo, _ = get_cursors()
    with open("ig.html", "w") as f:
        for res in ig_mongo.find():
            f.write('<img src="'+res["image_url"]+'">"<br>')


def add_timezone_info():

    ig_mongo, geo = get_cursors()
    for res in ig_mongo.find():
        if "offset" in res:
            continue
        try:
            timezone = geo.find_timezone({"lat": res["latitude"],
                                  "lng": res["longitude"]})
            res["offset"] = timezone["rawOffset"]
            ig_mongo.save(res)
        except geonames.GeonamesError, e:
            logging.getLogger().warn("GeonamesError for lat: %f, lng: %f " %
                   (res["latitude"], res["longitude"]))
            logging.getLogger().warn("GeonamesError message : "+str(e))
