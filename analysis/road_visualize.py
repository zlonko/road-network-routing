import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# local import
import setup_tools as st 
import map_measures as mm
from geo_dict import *

input_filename = input('Enter input filename: ')
print('...')
state = str(input('Enter state number: '))
print('...')
export_file = str(input('Enter export filename: '))

distances_output_dir = './distances_output/'
filepath = distances_output_dir + input_filename
df = pd.read_csv(filepath)

# take route column
route_list = df['ROUTE'].tolist()

# load route
print('loading graphml...')

G = ox.load_graphml('./roads/' + state +'.graphml', node_type=int)
Gs = ox.utils_graph.get_largest_component(G, strongly=True)
print('loaded graphml.')

print('plotting routes...')
fig, ax = ox.plot_graph_routes(Gs, route_list, route_colors='b')

print('displaying plot...')
plt.show()

plt.savefig('./images/' + export_file + '.svg')
print('saved route image to ./images/.')
