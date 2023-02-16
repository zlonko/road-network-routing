import pandas as pd
from geopy import distance
from math import cos, asin, sqrt
import heapq
import networkx as nx
import osmnx as ox

"""Finds average distance to closest hospital for census tract, county, and state. Merge with demographic data for each census tract."""

def load_data(filename_input):
    df_created = pd.read_csv(filename_input)
    return df_created

def load_data_keep(filename_input, keep_col_input):
    df_created = pd.read_csv(filename_input)
    df_created = df_create[keep_col_input].copy()
    return df_created

def create_dict(df_input):
    dict_output = df_input.to_dict('records')
    return dict_output

def haversine(lat1, lon1, lat2, lon2):
    """
    Define Haversine calculation for calculating distance.
    """
    p = 0.017453292519943295
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(a))

def createmap_usa():
    """
    Create one map of all roads in the United States to run queries.
    """
    # configure osmnx
    ox.config(use_cache=True, log_console=True)
    ox.__version__
    # create graph
    G = ox.graph_from_place(center_point = 'United States', network_type = 'drive')
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G

def createmap_states(df, added_border_distance):
    """
    Create road network slightly larger than a given state in the United States to run queries.
    This is accomplished by requesting the road network by polygon, using a bounding box.
    """
    # configure osmnx
    ox.config(use_cache=True, log_console=True)
    ox.__version__
    # pass in dataframe for state geometries
    x = added_border_distance
    north = df['BBOX_LAT_MAX'] + x
    south = df['BBOX_LAT_MIN'] - x
    east = df['BBOX_LONG_MAX'] - x
    west = df['BBOX_LONG_MIN'] + x
    # create graph
    G = ox.graph_from_bbox(north, south, east, west, network_type = 'drive')
    G = ox.graph_from_place(center_point = (df['INTPTLAT'], df['INTPTLONG']), network_type = 'drive')
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G


def closest_road(allhosp, ct, G):
    """
    Find closest hospital by distance and time.
    """
    # find three closest hosp by haversine 
    closest_list = heapq.nsmallest(3, allhosp, key = lambda p: haversine(p['y'],p['x'],ct['INTPTLAT'],ct['INTPTLONG']))
    # set farthest of 3 as radius from CT center point to create network
    farthest = max(closest_list, key = lambda x: haversine(x['y'],x['x'],ct['INTPTLAT'],ct['INTPTLONG']))
    radius = haversine(farthest['y'],farthest['x'],ct['INTPTLAT'],ct['INTPTLONG']) * 1610 # convert from miles to meters
    # find closest hosp of 3 closest by linear distance
    orig = ox.get_nearest_node(G,(ct['INTPTLAT'],ct['INTPTLONG']))
    hospdist = {}
    hosptime = {}
    for hosp in closest_list:
        dest = ox.get_nearest_node(G,(hosp['INTPTLAT'],hosp['INTPTLONG']))
        dist = nx.shortest_path_length(G, orig, dest, weight = 'length')
        time = nx.shortest_path_length(G, orig, dest, weight = 'travel_time')
        hospdist[hosp] = dist
        hosptime[hosp] = time
    closest_bydist = min(hospdist, key = hospdist.get) , hospdist[min(hospdist, key = hospdist.get)] # returns closest_hosp, hosp_dist
    closest_bytime = min(hosptime, key = hosptime.get), hosptime[min(hosptime, key = hosptime.get)] # returnts closest_hosp, hosp_time
    return closest_bydist, closest_bytime

# find closest hosp to each CT
def find_roads(ct_dict, hosp_dict, G):
    """
    Iterate through census tract dictionary using closest_road function to generate dataframe of closest hospitals by time and distance.
    """
    for ct in ct_dict:
        closest_bydist, closest_bytime = closest_road(hosp_dict, ct, G)
        ct.update(closest_bydist[0])
        ct['CT_dist'] = closest_bydist[1]
    df_ct = pd.DataFrame.from_dict(ct_dict)
    return df_ct

def merge_demography(df_ct, filename_tracts):
    """
    Join generated distance data df_ct to existing tract data df_tract.
    """
    # format distance data for tracts to merge with demographic data
    df_ct['GEOID'] = df_ct['GEOID'].apply(lambda x: '{0:0>11}'.format(x))
    df_ct['GEOID'] = df_ct['GEOID'].astype(str)
    # format tract-level demographic data
    df_tracts = pd.read_csv(filename_tracts)
    df_tracts['Geographical ID'] = df_tracts['Geographical ID'].str[-11:]
    df_tracts = df_tracts.replace(-666666666,'NaN')
    # merge with demographic data and save as csv
    df_ct = df_ct.merge(right=df_tracts, right_on='Geographical ID', left_on='GEOID', how='left')
    return df_ct

def export_demography(df_export, filename_export):
    """
    Export dataframe to CSV.
    """
    df_export.to_csv(filename_export)


if __name__ == '__main__':
    
    # -------------------------------------
    # info about hospital file
    filename_hosp = 'state_cert_coord.csv'
    keep_col_hosp = ['Hospital','x','y']
    # info about census tract coord file
    filename_ct = 'census_tract_coord.csv'
    keep_col_ct = ['GEOID','INTPTLAT','INTPTLONG']
    # info about state dimensions in geometry directory
    filename_states = './input/united_states_dimensions.csv'
    # info about tract file
    filename_tracts = './input/acs_tract.csv'
    # info about export file
    filename_export = './output/ct_roaddistances.csv'

    # -------------------------------------
    # load hospitals and census tracts
    df_hosp = load_data_keep(filename_hosp, keep_col_hosp)
    df_ct = load_data_keep(filename_ct, keep_col_ct)
    # load state geography
    df_states = load_data(filename_states)

    # -------------------------------------
    # create dictionaries
    dict_hosp = create_dict(df_hosp)
    dict_ct = create_dict(df_ct)

    # -------------------------------------
    # find road distances using closestroad function
    G = createmap_usa()
    df_ct = find_roads(dict_ct, dict_hosp, G)

    # -------------------------------------
    # export stuff
    df_ct = merge_demography(df_ct, df_hosp)
    export_demography(df_ct, filename_export)