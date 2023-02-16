"""
Load a GeoJSON file and generate key descriptive information about the geometries contained:
- Find bounding box coordinates for the max/min latitude, max/min longitude of each individual geometry
- Determine coordinates of centroid for the bounding box of each geometry
- Determine the maximum distance across the state from north-to-south (LENGTH) and east-to-west (WIDTH)
Output descriptive information to local CSV
"""

# requirements
import pandas as pd
from pandas.io.json import json_normalize
import glob
import json
import numpy as np
from scipy import pi

# local import
import setup_tools as st
from map_measures import haversine, vincenty


def bbox_bounds(df_json):
    """
    Identify the maximum and minimum latitude and longitude values for each geometry in the dataframe.
    These represent the perimeter of the bounding box to the north, south, east, and west.
    """

    keep_col = ['id','properties.name','geometry.type','geometry.coordinates']
    df = df_json[keep_col]

    # placeholders
    df['LAT_MIN'] = 'x'
    df['LAT_MAX'] = 'x'
    df['LONG_MIN'] = 'x'
    df['LONG_MAX'] = 'x'

    # depending on if the shape is a polygon or multipolygon, the geojson list is unnested at different levels
    # then, each list within the list is analyzed: the first value being the lat, the second value being the long
    # the process assigns min lat, max lat, min long, and max long based on the values in those positions
    for i, coord in df.iterrows():
        if df.loc[i, 'geometry.type'] == 'Polygon':
            input_list = df.loc[i, 'geometry.coordinates']
            coord_list = [item for items in input_list for item in items]
            print('NAME: ' + df.loc[i, 'properties.name'])
            df['LAT_MIN'].iloc[i] = min([sublist[1] for sublist in coord_list])
            df['LAT_MAX'].iloc[i] = max([sublist[1] for sublist in coord_list])
            df['LONG_MIN'].iloc[i] = min([sublist[0] for sublist in coord_list])
            df['LONG_MAX'].iloc[i] = max([sublist[0] for sublist in coord_list])
            print('LAT_MIN: ' + str(df.loc[i, 'LAT_MIN']))
            print('LAT_MAX: ' + str(df.loc[i, 'LAT_MAX']))
            print('LONG_MIN: ' + str(df.loc[i, 'LONG_MIN']))
            print('LONG_MAX: ' + str(df.loc[i, 'LONG_MAX']))
            print('GEOMETRY TYPE: ' + df.loc[i, 'geometry.type'])
            print('COORDINATES:')
            print(coord_list)
            print('----------------------------------------------------------------')
        elif df.loc[i, 'geometry.type'] == 'MultiPolygon':
            input_list = df.loc[i, 'geometry.coordinates']
            coord_list = [item for items in input_list for item in items]
            coord_list = [item for items in coord_list for item in items]
            print('NAME: ' + df.loc[i, 'properties.name'])
            df['LAT_MIN'].iloc[i] = min([sublist[1] for sublist in coord_list])
            df['LAT_MAX'].iloc[i] = max([sublist[1] for sublist in coord_list])
            df['LONG_MIN'].iloc[i] = min([sublist[0] for sublist in coord_list])
            df['LONG_MAX'].iloc[i] = max([sublist[0] for sublist in coord_list])
            print('LAT_MIN: ' + str(df.loc[i, 'LAT_MIN']))
            print('LAT_MAX: ' + str(df.loc[i, 'LAT_MAX']))
            print('LONG_MIN: ' + str(df.loc[i, 'LONG_MIN']))
            print('LONG_MAX: ' + str(df.loc[i, 'LONG_MAX']))
            print('GEOMETRY TYPE: ' + df.loc[i, 'geometry.type'])
            print('COORDINATES:')
            print(coord_list)
            print('----------------------------------------------------------------')
        else: 
            print('Error...')
            print('----------------------------------------------------------------')

    return df


def bbox_centroid(df):
    """
    Calculate rough coordinates of the bounding box's center point.
    This can be used for different analyses, such as centering a custom polygon for the search area on each geometry.
    """
    # placeholders
    df['CENTROID_LAT'] = 'y'
    df['CENTROID_LONG'] = 'x'

    for i, coord in df.iterrows():
        # take the average of the latitudes and longitudes to determine centroid lat/long
        df['CENTROID_LAT'].iloc[i] = (df['LAT_MAX'].iloc[i] + df['LAT_MIN'].iloc[i]) / 2
        df['CENTROID_LONG'].iloc[i] = (df['LONG_MAX'].iloc[i] + df['LONG_MIN'].iloc[i]) / 2

    return df


def bbox_dimensions(df):
    """
    Calculate greatest width (west-to-east) and length (north-to-south) distance of an input geometry.
    These are the width and length in meters (m) of the bounding box of that geometry, then converted to miles.
    """
    # placeholders
    df['WIDTH_HAVERSINE'] = 'W'
    df['LENGTH_HAVERSINE'] = 'L'
    df['WIDTH_VINCENTY'] = 'W'
    df['LENGTH_VINCENTY'] = 'L'
    
    # set conversion rate from meters to miles
    conversion = 1 / 1609.34

    for i, coord in df.iterrows():
        # calculate spherical distance between coordinates in meters, then convert to miles
        df['WIDTH_HAVERSINE'].iloc[i] = haversine(df['LAT_MAX'].iloc[i],df['LONG_MIN'].iloc[i],df['LAT_MAX'].iloc[i],df['LONG_MAX'].iloc[i]) * conversion
        df['LENGTH_HAVERSINE'].iloc[i] = haversine(df['LAT_MAX'].iloc[i],df['LONG_MIN'].iloc[i],df['LAT_MIN'].iloc[i],df['LONG_MIN'].iloc[i]) * conversion
        # calculate ellipsoidal distance between coordinates in meters, then convert to miles
        df['WIDTH_VINCENTY'].iloc[i] = vincenty(df['LAT_MAX'].iloc[i],df['LONG_MIN'].iloc[i],df['LAT_MAX'].iloc[i],df['LONG_MAX'].iloc[i]) * conversion
        df['LENGTH_VINCENTY'].iloc[i] = vincenty(df['LAT_MAX'].iloc[i],df['LONG_MIN'].iloc[i],df['LAT_MIN'].iloc[i],df['LONG_MIN'].iloc[i]) * conversion

    return df


if __name__ == '__main__':
    # setup
    this_file = 'base'
    filename = './input/states.json'
    df = st.load_geojson(filename)
    # operations
    df = bbox_bounds(df)
    df = bbox_centroid(df)
    df = bbox_dimensions(df)
    # export
    df.to_csv('./output/output_' + this_file + '.csv')
    print('COMPLETE.')


