"""
Add buffer around GeoJSON geometry using data from bounding_box operations.
"""

# requirements
import pandas as pd
from shapely.geometry import shape

# local import
import setup_tools as st


def buffer_bbox(df, buffer_radians):
    """
    Add a buffer distance in RADIANS to return new max/min latitude and max/min longitude values 
    for the bounding box of each geometry. Adding a buffer accounts for people that may travel to 
    locations across the border of their geometry, e.g., living in Illinois but going to a hospital
    in St. Louis City, MO.
    """
    this_file = 'buffer'
    buffer_type = 'bbox'
    b = buffer_radians

    print('Starting new geometry...')
    
    # placeholders
    df['BBOX_NORTH'] = 'n'
    df['BBOX_SOUTH'] = 's'
    df['BBOX_EAST'] = 'e'
    df['BBOX_WEST'] = 'w'
    df['BUFFER_DIST_RAD'] = 'buffer'
    
    for i, coord in df.iterrows():
        print('NAME: ' + str(df['properties.name'].iloc[i]))
        df['BUFFER_DIST_RAD'].iloc[i] = b
        df['BBOX_NORTH'].iloc[i] = df['LAT_MAX'].iloc[i] + b
        df['BBOX_SOUTH'].iloc[i] = df['LAT_MIN'].iloc[i] - b
        df['BBOX_EAST'].iloc[i] = df['LONG_MAX'].iloc[i] + b
        df['BBOX_WEST'].iloc[i] = df['LONG_MIN'].iloc[i] - b
        print('BUFFER DISTANCE IN RADIANS: ' + str(df['BUFFER_DIST_RAD'].iloc[i]))
        print('BUFFERED NORTH LATITUDE: ' + str(df['BBOX_NORTH'].iloc[i]))
        print('BUFFERED SOUTH LATITUDE: ' + str(df['BBOX_SOUTH'].iloc[i]))
        print('BUFFERED EAST LONGITUDE: ' + str(df['BBOX_EAST'].iloc[i]))
        print('BUFFERED WEST LONGITUDE: ' + str(df['BBOX_WEST'].iloc[i]))
        print('-----------------------------------------------------')

    # export new geometry
    export_dest = './output/output_' + this_file + '_' + buffer_type + '.csv'

    return df, export_dest


def buffer_edge(df, buffer_radians):
    """
    Add a buffer distance in RADIANS to return new max/min latitude and max/min longitude values 
    for the bounding box of each geometry. Adding a buffer accounts for people that may travel to 
    locations across the border of their geometry, e.g., living in Illinois but going to a hospital
    in St. Louis City, MO.
    """

    this_file = 'buffer'
    buffer_type = 'edge'
    b = buffer_radians

    print('Starting new geometry...')
    
    # placeholders
    df['BUFFER_DIST_RAD'] = 'b'
    df['EDGE_EXPANDED'] = 'e'
    
    for i, coord in df.iterrows():

        print('NAME: ' + str(df['properties.name'].iloc[i]))
        df['BUFFER_DIST_RAD'].iloc[i] = b
        coords_to_expand = df['geometry.coordinates'].iloc[i]
        df['EDGE_EXPANDED'].iloc[i] = shape(coords_to_expand.buffer(b))
        print('BUFFER DISTANCE IN RADIANS: ' + str(df['BUFFER_DIST_RAD'].iloc[i]))
        print('NEW EXPANDED EDGE GEOMETRY: ' + str(df['EDGE_EXPANDED'].iloc[i]))
        print('-----------------------------------------------------')

    # export new geometry
    export_dest = './output/output_' + this_file + '_' + buffer_type + '.csv'

    return df, export_dest


def buffer_point(df, buffer_radians):
    """
    Add a buffer distance in RADIANS around the centroid of a given geometry. The buffer_radians
    value will act as an additional distance extending past the length or width of the geometry, 
    depending on which is greater.
    """

    this_file = 'buffer'
    buffer_type = 'point'
    b = buffer_radians 

    print('Starting new geometry...')

    # placeholders
    df['BUFFER_DIST_RAD'] = 'b'
    df['SEARCH_RADIUS'] = 'r'

    # iterate through df to add the additional buffer to the max(length, width) value
    # this returns a radius value to be projected from the centroid when searching the
    # road network on OSMNx
    for i, coord in df.iterrows():
        print('NAME: ' + str(df['properties.name'].iloc[i]))
        df['BUFFER_DIST_RAD'].iloc[i] = b
        greater_internal_dist = max(df['WIDTH_VINCENTY'].iloc[i],df['LENGTH_VINCENTY'].iloc[i])
        df['SEARCH_RADIUS'].iloc[i] = (b + greater_internal_dist) / 2
    
    # export new geometry
    export_dest = './geography/output/output_' + this_file + '_' + buffer_type + '.csv'

    return df, export_dest


def buffer_choice():
    """
    Choose the preferred buffer type in a script requiring user input.
    """

    # possible buffer methods
    choices = ['bbox', 'edge', 'point']

    # choose buffer method
    while True:
        choice = input('\nChoose buffer method: bbox, edge, or point?   ').lower()
        if choice not in choices:
            print('\nCommand not recognized. Please try again.')
            continue
        else:
            break

    # choose buffer distance
    while True:
        buffer_dist = float(input('\nEnter desired buffer distance in radians:   '))
        if buffer_dist < 0:
            print('\nBuffer distance must be >= 0. Please enter another value.')
        elif isinstance(buffer_dist, str) == True: 
            print('\nBuffer distance cannot be a string value. Please enter a numerical value.')
        else:
            break
    
    return choice, buffer_dist


def buffer_run(choice, df, buffer_dist):
    """
    Run the preferred buffer type "choice" ay distance "buffer_dist" in a script requiring user input.
    """

    if choice == 'bbox':
        # add buffer using bbox method with distance in radians
        df_buffer, export_dest = buffer_bbox(df, buffer_dist)
    elif choice == 'edge':
        # add buffer conforming to shape edge with distance in radians
        df_buffer, export_dest = buffer_edge(df, buffer_dist)
    elif choice == 'point':
        # add buffer params to search within a circular radius, with distance in radians
        df_buffer, export_dest = buffer_point(df, buffer_dist)
    else:
        pass

    return df_buffer, export_dest


def export_buffer_file(df_buffer, export_dest):
    """
    Export new geometries with added buffer.
    """

    df_buffer.to_csv(export_dest)

    return df_buffer


if __name__ == '__main__':
    
    df = st.load_csv('./output/output_base.csv')

    # choose buffer method and distance
    choice, buffer_dist = buffer_choice()

    # run buffer method
    df_buffer, export_dest = buffer_run(choice, df, buffer_dist)

    # export the buffered geometries from previous process
    export_buffer_file(df_buffer, export_dest)

