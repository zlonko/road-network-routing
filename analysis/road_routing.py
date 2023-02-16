"""
Find distances in miles between closest hospital and centroid of the specified geometry.
Merge with demographic data from the Census.
"""

import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx

# local import
import setup_tools as st 
import map_measures as mm
from geo_dict import *


def find_roads(input_path, graph_location, output_path, version, state_list):
    
    print('--------------------------------')
    print('states to print:')
    print(state_list)
    print('--------------------------------')

    for state_num in state_list:

        df_ct_hosp = st.load_csv(input_path)
        df_ct_hosp['DISTANCE_ROAD'] = 'd'
        df_ct_hosp['DISTANCE_TIME'] = 't'
        df_ct_hosp['ROUTE'] = 'r'

        # filter dataframe to particular state
        print('State: ' + str(state_num))
        state_num_i = int(state_num)
        df = df_ct_hosp[df_ct_hosp['State'] == state_num_i]

        # load graphml file for corresponding state
        state_num = str(state_num)
        G = ox.load_graphml(graph_location + state_num + '.graphml', node_type=int)
        print('loaded graphml for ' + state_num + '.')
        print('--------------------------------')
        Gs = ox.utils_graph.get_largest_component(G, strongly=True)
        print('making strongly connected graph...')
        print('--------------------------------')

        df = df.reset_index()
        
        print('starting road routing for State ' + state_num + '...')

        for i, coord in df.iterrows():

            geoid_no = str(df['GEOID'].iloc[i])
            
            print(i)
            print('GEOID: ' + geoid_no)

            orig_lat = df['ORIG_LAT'].iloc[i]
            print('origin latitude:')
            print(orig_lat)

            orig_long = df['ORIG_LONG'].iloc[i]
            print('origin longitude:')
            print(orig_long)

            dest_lat = df['DEST_LAT'].iloc[i]
            print('destination latitude:')
            print(dest_lat)

            dest_long = df['DEST_LONG'].iloc[i]
            print('destination longitude:')
            print(dest_long)

            orig = ox.get_nearest_node(Gs,(orig_lat,orig_long))
            print('origin node:')
            print(orig)

            dest = ox.get_nearest_node(Gs,(dest_lat,dest_long))
            print('destination node:')
            print(dest)

            dist = nx.shortest_path_length(Gs, orig, dest, weight = 'length')
            print('total distance:')
            print(dist)

            time = nx.shortest_path_length(Gs, orig, dest, weight = 'travel_time')
            print('total travel time:')
            print(time)

            route = nx.shortest_path(Gs, orig, dest, weight='length')
            print('route:')
            print(route)

            df['DISTANCE_ROAD'].iloc[i] = dist
            df['DISTANCE_TIME'].iloc[i] = time
            df['ROUTE'].iloc[i] = route

            print('-------------------------------')

        df.to_csv(output_path + 'road_dist_' + version + '_state_' + state_num + '.csv')
        print('exported csv for ' + state_num)
        
        print('-------------------------------')

    return df


if __name__ == '__main__':

    # find road distances by querying saved graphml files
    print('-------------------------------')
    print('ROAD ROUTING ... Start')
    print('-------------------------------')

    # user inputs
    input_path = input('Enter filepath to INPUT CSV, e.g., ./distances_input/census_tracts_closest_hospitals.csv: ')
    print('...')
    graph_location = input('Enter directory for GRAPHML files, e.g., ./roads/: ')
    print('...')
    output_path = input('Enter directory for OUTPUT CSV files, e.g., ./distances_output/: ')
    print('...')
    version = str(input('Enter VERSION #: '))
    print('...')
    fork = str(input('Run process on select states, the contiguous U.S., or all states? Enter SELECT, CONTIGUOUS, or ALL: ').upper())
    if fork == 'SELECT':
        state_list = list(map(int,input('Enter TARGET STATES(s), separated by commas: ').strip().split(',')))
    elif fork == 'CONTIGUOUS':
        state_list = state_dict_abbr_contiguous.values()
    else:
        state_list = state_dict_abbr.values()
    print('...')

    # run process
    df = find_roads(input_path, graph_location, output_path, version, state_list)
