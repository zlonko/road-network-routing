"""
Grab road networks for a series of given geometries and export as GraphML for future use.
To run OSMNx, first use in terminal:
    conda activate ox
    conda config --prepend channels conda-forge conda create -n ox --strict-channel-priority osmnx
"""

# requirements
import pandas as pd
import networkx as nx
import osmnx as ox
import shapely

# local import
import setup_tools as st
import modify_buffer as mb


def grab_roads_bbox(df, distance_type, simplify_tf, retain_tf, send_to):
    """
    Grab road networks with OSMNx using the bounding box method.
    This entails drawing a rectangle on the map and querying Open Street Map for roads within that rectangle.
        Params:
        distance_type: ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’
        simplify = BOOL True or False, simplify graph topology
        retain_all = BOOL True or False, return entire graph even if not connected
        https://osmnx.readthedocs.io/en/stable/osmnx.html
    Export to GraphML file in /roads directory.
    """
    # configure osmnx
    ox.config(use_cache=True, log_console=True)
    ox.__version__
    print('OSMNx configured.')

    for i, coord in df.iterrows():

        # pass in buffered distances from buffer.py
        north = df['BBOX_NORTH'].iloc[i]
        south = df['BBOX_SOUTH'].iloc[i]
        east = df['BBOX_EAST'].iloc[i]
        west = df['BBOX_WEST'].iloc[i]

        # create 
        print('Starting graph from bbox...')
        print('NAME: ' + str(df['properties.name'].iloc[i]))
        G = ox.graph_from_bbox(north, south, east, west, network_type=distance_type, simplify=simplify_tf, retain_all=retain_tf)
        
        # set filename to name of the geometry
        filename = str(df['properties.name'].iloc[i])
        # export GraphML file
        path_to_file = send_to + filename + '.graphml'
        ox.io.save_graphml(G,filepath=path_to_file, gephi=False, encoding='utf-8')
        print('Completed graph from bbox.')
        print('-----------------------------------------------------')
        print('-----------------------------------------------------')
        print('-----------------------------------------------------')
        # input('Press enter to continue process.\n-----------------------------------------------------')
    
    end_message = 'All road networks exported.'
    print(end_message)
    
    return end_message


def grab_roads_edge(df, distance_type, simplify_tf, retain_tf, send_to):
    """
    Grab road networks with OSMNx using the edge-conforming method.
    Here, we draw a polygon on the map and query Open Street Map for roads contained within that polygon.
        Params:
        distance_type: ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’
        simplify = BOOL True or False, simplify graph topology
        retain_all = BOOL True or False, return entire graph even if not connected
        https://osmnx.readthedocs.io/en/stable/osmnx.html
    Export to GraphML file in /roads directory.
    """

    for i, coord in df.iterrows():

        print('Starting graph from expanded edge polygon...')
        print('NAME: ' + str(df['properties.name'].iloc[i]))
        coords = df['EDGE_EXPANDED'].iloc[i]
        G = ox.graph_from_polygon(coords, network_type=distance_type, simplify=simplify_tf, retain_all=retain_tf)

        # set filename to name of the geometry
        filename = str(df['properties.name'].iloc[i])
        # export GraphML file
        path_to_file = send_to + filename + '.graphml'
        ox.io.save_graphml(G,filepath=path_to_file, gephi=False, encoding='utf-8')
        print('Completed graph from expanded edge polygon.')
        print('-----------------------------------------------------')
    
    end_message = 'All road networks exported.'
    print(end_message)
    
    return end_message


def grab_roads_point(df, distance_type, simplify_tf, retain_tf, send_to):
    """
    Grab road networks with OSMNx using a radius from the geometry centroid.
    A circle is drawn from the center of each geometry to query Open Street Map for roads containeed within that circle.
        Params:
        distance_type: ‘walk’, ‘bike’, ‘drive’, ‘drive_service’, ‘all’, ‘all_private’
        simplify = BOOL True or False, simplify graph topology
        retain_all = BOOL True or False, return entire graph even if not connected
        https://osmnx.readthedocs.io/en/stable/osmnx.html
    Export to GraphML file in /roads directory.
    """

    for i, coord in df.iterrows():

        print('Starting graph from point...')
        print('NAME: ' + str(df['properties.name'].iloc[i]))
        center_point = tuple(df['CENTROID_LAT'].iloc[i], df['CENTROID_LONG'].iloc[i])
        search_distance = df['SEARCH_RADIUS'].iloc[i]
        G = ox.graph_from_point(center_point, dist=search_distance, dist_type='bbox', network_type=distance_type, simplify=simplify_tf, retain_all=retain_tf)

        # set filename to name of the geometry
        filename = str(df['properties.name'].iloc[i])
        # export GraphML file
        path_to_file = send_to + filename + '.graphml'
        ox.io.save_graphml(G,filepath=path_to_file, gephi=False, encoding='utf-8')
        print('Completed graph from point.')
        print('-----------------------------------------------------')
    
    end_message = 'All road networks exported.'
    print(end_message)

    return end_message


if __name__ == '__main__':
    send_to = './roads/'
    load_filename = input('Enter name of buffer file in ./output, e.g., ./output/output_buffer_bbox.csv: ')
    df = st.load_csv(load_filename)
    # choose method
    grab_roads_bbox(df, 'drive', False, True, send_to)
    # grab_roads_edge(df, 'drive', True, True, send_to)
    # grab_roads_point(df, 'drive', True, True, send_to)
