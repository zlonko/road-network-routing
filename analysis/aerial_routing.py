"""
Find distances in miles between closest hospital and centroid of the specified geometry.
"""

import numpy as np
import pandas as pd
from geopy import distance

# local import
import setup_tools as st 
import map_measures as mm
from geo_dict import *


def geodata_to_dict(filename_hosp, filename_ct):

    # load list of hospitals and coordinates      
    df_hosp = pd.read_csv(filename_hosp)
    keep_col = ['HOSPITAL','ZIPCODE','CERT_DESIGNATION','CERT_ORG','HOSPITAL_LAT', 'HOSPITAL_LONG']
    df_hosp = df_hosp[keep_col].copy()

    # load all ct coordinates
    df_ct = pd.read_csv(filename_ct)
    keep_col = ['GEOID','USPS','AREA_LAND_SQMI','TRACT_LAT','TRACT_LONG']
    df_ct = df_ct[keep_col].copy()

    # create list of dictionaries containing lon/lat of each hosp and zcta
    hosp_dict = df_hosp.to_dict('records')
    ct_dict = df_ct.to_dict('records')

    return hosp_dict, ct_dict


def closest_aerial(hosp_dict, ct):

    # base function to find closest by aerial distance
    closest_hosp = min(hosp_dict, key = lambda p: mm.haversine(p['HOSPITAL_LAT'],p['HOSPITAL_LONG'],ct['TRACT_LAT'],ct['TRACT_LONG']))
    hosp_dist = distance.geodesic((closest_hosp['HOSPITAL_LAT'], closest_hosp['HOSPITAL_LONG']),(ct['TRACT_LAT'], ct['TRACT_LONG'])).miles
    return closest_hosp, hosp_dist


def assign_closest(hosp_dict, ct_dict):

    # iterate through dictionary to assign closest hospital
    # use closest_aerial() function
    for ct in ct_dict:
        print(ct.get('GEOID'))
        closest_hosp, hosp_dist = closest_aerial(hosp_dict, ct)
        ct.update(closest_hosp)
        ct['AERIAL_DIST'] = hosp_dist
        print(closest_hosp.get('HOSPITAL'))
        print(hosp_dist)
        print('-------------------')
    df = pd.DataFrame.from_dict(ct_dict)
    
    return df


def merge_population_data(df_ct, filename_census):

    # format to merge with demographic data
    df_ct['GEOID'] = df_ct['GEOID'].apply(lambda x: '{0:0>11}'.format(x))
    df_ct['GEOID'] = df_ct['GEOID'].astype(str)

    # load population data
    df_pop = pd.read_csv(filename_census)
    df_pop['Geographical ID'] = df_pop['Geographical ID'].str[-11:]
    df_pop = df_pop.replace(-666666666,'NaN')

    # merge with demographic data and save as csv
    df_ct_pop = df_ct.merge(right=df_pop, right_on='Geographical ID', left_on='GEOID', how='left')

    df_ct_pop['POPDENSITY'] = df_ct_pop['Total Population'] / df_ct_pop['AREA_LAND_SQMI']

    return df_ct_pop 


if __name__ == '__main__':

    # load data for hospitals and census tracts
    filename_hosp = './input/state_cert_coord.csv'
    filename_ct = './input/census_tract_coord.csv'
    filename_census = './input/acs_tract.csv'
    
    # find closest hospital by aerial distance
    hosp_dict, ct_dict = geodata_to_dict(filename_hosp, filename_ct)
    df_ct = assign_closest(hosp_dict, ct_dict)

    # merge population data to geography
    df = merge_population_data(df_ct, filename_census)

    # export to csv
    df.to_csv('./output/census_tracts_closest_hospitals.csv')
    print('Exported data to csv.')