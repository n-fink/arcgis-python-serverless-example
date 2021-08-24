#!/usr/bin/env python
""" A python script to automate the creation of feature services in an ArcGIS portal
"""

__author__ = "Nick Fink"
__contact__ = "nicholas.fink@nltgis.com"
__copyright__ = "Copyright 2021 New Light Technologies, Inc."
__date__ = "2021/01/26"
__license__ = "MIT"

from arcgis import GIS
import pandas
import os
import requests

# here's our login credentials for the ArcGIS Portal
portal_url = "https://YourOrg.maps.arcgis.com"
portal_user = "YourUser"
portal_password = "SuperSecurePassword"

# connect to your gis portal to do the work
gis = GIS(url=portal_url, username=portal_user, password=portal_password)

# here's our variables to work with
folder_name = "My Test Folder"  # the name of the folder in your user's content to place the content in
data_url = "https://www3.septa.org/api/TrainView/"  # this is the url of the data we'll be testing with
tbl_name = "my_awesome_api_test"    # this is what we'll name the file/feature service
frmt = "CSV"    # this is the format we'll be using
summary = "A quick test layer from an API"  # a quick summary of for the content page
desc = "An ArcGIS feature service proving we can publish a brand new layer with the Python API for Arcgis from a " \
       "live API!"  # a short description for the content page
tags = "test, awesome, python, arcgis"  # tags to more easily find our new content
title = "My Awesome API Test"   # a nicely formatted title for our content

try:
    # if the folder doesn't exist, create it
    gis.content.create_folder(folder=folder_name)
except:
    # if the folder exists, skip creating it
    pass

file_name = tbl_name+'.'+frmt.lower()

# read the data from the api
api_data = requests.get(data_url).json()

# we're using pandas because it already comes with the arcgis library
data_df = pandas.DataFrame(api_data)

# write the json data to csv
data_df.to_csv(file_name, index=False)

# define the service's properties
service_properties = {'title': title, 'snippet': summary, 'description': desc, 'tags': tags, 'type': frmt,
                      'overwrite': True}

# upload the csv file to the arcgis portal
file_item = gis.content.add(item_properties=service_properties, data=file_name, folder=folder_name)

# publish a feature service from the uploaded file
feature_layer_item = file_item.publish()

# delete the file from your workspace as a clean up step, comment this out if you want to see what the file looks like
os.remove(file_name)
