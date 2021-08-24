#!/usr/bin/env python
""" A python script that updates a feature service in an ArcGIS portal
"""

__author__ = "Nick Fink"
__contact__ = "nicholas.fink@nltgis.com"
__copyright__ = "Copyright 2021 New Light Technologies, Inc."
__date__ = "2021/01/26"
__license__ = "MIT"

import pandas
from arcgis import GIS
import os
import requests

data_url = "https://www3.septa.org/api/TrainView/"
portal_url = "https://YourOrg.maps.arcgis.com"
portal_user = "YourUser"
portal_password = "SuperSecurePassword"
portal_item = ""   # the 32 character item id of the feature service created earlier
file_name = "my_awesome_api_test.csv"   # the file name for the update has to be the same as the one used to publish

# once again, we're reading data in from the api and creating a csv
api_data = requests.get(data_url).json()
data_df = pandas.DataFrame(api_data)
data_df.to_csv(file_name, index=False)

# connect to the portal again
gis = GIS(url=portal_url, username=portal_user, password=portal_password)
# find the feature service we're updating
item = gis.content.get(portal_item)
# find the layer in the feature service we're updating
fs = item.layers[0].container
# overwrite the layer with the new data
fs.manager.overwrite(file_name)

# delete the file once the service has been updated
os.remove(file_name)
