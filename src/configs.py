"""Configs for the different viewports

:projection:  A valid matplotlib.Basemap projection
:resolution:  Resolution of coastlines.  One of "c" (crude),
    "l" (low), "m" (medium), "h" (high)
:resolution_kwargs: A dictionary containing whatever parameters
   are required by this particular projection.  Notably, ``lat_0``
   and ``lon_0`` specify the center of the image in latitude and longitude
"""
cameras = {
    "Original": {
        "projection": "lcc",
        "resolution": "l",
        "projection_kwargs": {
            "width": 12000000,
            "height": (9./16.)*12000000,
            "lat_0": 50,
            "lon_0": -107,
            "lat_1": 45,
            "lat_2": 55
        }
    },
    "USA": {
        "width": 6500000,
        "resolution": "l",
        "projection": "lcc",
        "projection_kwargs": {
            "lat_0": 40,
            "lon_0": -100,
            "lat_1": 45,
            "lat_2": 55
        }
    },
    "Europe": {
        "width": 6500000,
        "resolution": "l",
        "projection": "lcc",
        "projection_kwargs": {
            "lat_0": 50,
            "lon_0": 20,
            "lat_1": 45,
            "lat_2": 55
        }
    },
    "UK": {
        "resolution": "i",
        "projection": "lcc",
        "projection_kwargs": {
            "lat_0": 55,
            "lon_0": 10,
            "lat_1": 45,
            "lat_2": 55,
            "width": 3000000,
            "height": (9./16.)*3000000
        }
    },
    "World": {
         "resolution": "l",
         "projection": 'mill',
         "projection_kwargs": {
             "llcrnrlon": -180,
             "llcrnrlat": -80,
             "urcrnrlon": 180,
             "urcrnrlat": 80
         }
    }

}
