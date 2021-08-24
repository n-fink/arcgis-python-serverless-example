#!/usr/bin/env python
""" A python script to be packaged in a zip archive to be run as an AWS Lambda
"""

__author__ = "Nick Fink"
__contact__ = "nicholas.fink@nltgis.com"
__copyright__ = "Copyright 2021 New Light Technologies, Inc."
__date__ = "2021/01/26"
__license__ = "MIT"

import os
import pandas
from arcgis import GIS
import requests


def agol_update(event, context):
    # this is for the lambda env
    data_url = os.environ['data_url']
    portal_url = os.environ['portal_url']
    portal_user = os.environ['portal_user']
    portal_password = os.environ['portal_password']
    portal_item = os.environ['portal_item']
    file_name = os.environ['file']

    os.chdir('/tmp/')

    api_data = requests.get(data_url).json()
    data_df = pandas.DataFrame(api_data)
    data_df.to_csv(file_name, index=False)

    ### updates agol service
    gis = GIS(url=portal_url, username=portal_user, password=portal_password)
    item = gis.content.get(portal_item)
    fs = item.layers[0].container
    fs.manager.overwrite(file_name)
