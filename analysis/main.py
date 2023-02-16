"""
Main controller for grabbing road networks based on GeoJSON geometries.
"""

# requirements

# local import
import setup_tools as st
import bounding_box as bb
import map_measures as mm
import modify_buffer as mb
import grab_roads as gr
from geo_dict import * 
import aerial_routing as ar 
import road_routing as rr


if __name__ == '__main__':
    # ------------------------------------
    # SETUP

    print('Starting to load GeoJSON data...')
    # input geojson file
    input_data_dir = './input/'
    filename_json = input_data_dir + 'states.json'
    df = st.load_geojson(filename_json)
    # data output directory
    output_data_dir = './output/'

    print('Loaded GeoJSON data.')
    print('----------------------------------------------')
    input("Press Enter to continue...")

    # ------------------------------------
    # BOUNDING_BOX

    this_file = 'base'
    export_dest = output_data_dir + 'output_' + this_file + '.csv'
    print('Starting to find bounding box for geometries...')
    # operations
    df = bb.bbox_bounds(df)
    df = bb.bbox_centroid(df)
    df = bb.bbox_dimensions(df)
    # export
    df.to_csv(export_dest)
   
    print('Found bounds, centroid, dimensions of GeoJSON.')
    print('Exported to ' + str(export_dest) + '.')
    print('----------------------------------------------')
    input("Press Enter to continue...")

    # ------------------------------------
    # MODIFY_BUFFER

    print('Starting the process to add buffer...')
    
    # choose buffer method and distance
    choice, buffer_dist = mb.buffer_choice()
    # run buffer method
    df_buffer, export_dest = mb.buffer_run(choice, df, buffer_dist)
    # export the buffered geometries from previous process
    mb.export_buffer_file(df_buffer, export_dest)
        
    print('Created geometry with buffer.')
    print('Exported to ' + str(export_dest) + '.')
    print('----------------------------------------------')

    # -----------------------------------
    # GRAB_ROADS

    send_to = './roads/'
    df = st.load_csv(output_data_dir + 'output_buffer_bbox.csv')
    
    # choose method
    if choice == 'bbox':
        gr.grab_roads_bbox(df, 'drive', True, True, send_to)
    elif choice == 'edge':
        gr.grab_roads_edge(df, 'drive', True, True, send_to)
    elif choice == 'point':
        gr.grab_roads_point(df, 'drive', True, True, send_to)
    
    # -----------------------------------
    # AERIAL_ROUTING

    # load data for hospitals and census tracts
    filename_hosp = input_data_dir + 'state_cert_coord.csv'
    filename_ct = input_data_dir + 'census_tract_coord.csv'
    filename_census = input_data_dir + 'acs_tract.csv'
    
    # find closest hospital by aerial distance
    hosp_dict, ct_dict = ar.geodata_to_dict(filename_hosp, filename_ct)
    df_ct = ar.assign_closest(hosp_dict, ct_dict)

    # merge population data to geography
    df = ar.merge_population_data(df_ct, filename_census)

    # export to csv
    df.to_csv(output_data_dir + 'census_tracts_closest_hospitals.csv')
    print('Exported data to csv.')

    # -----------------------------------
    # ROAD_ROUTING
    # load data for hospitals and census tracts
    filename_ct_hosp = output_data_dir + 'census_tracts_closest_hospitals.csv'
    df = st.load_csv(filename_ct_hosp)

    # find road distances by querying saved graphml files
    state_num = str(input('Enter State #: '))
    df = rr.find_roads(df, state_num)
