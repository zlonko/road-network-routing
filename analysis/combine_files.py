import pandas as pd
import glob

print('--------------------------------')
print('Combines state-level road routing files based on version #.')
path_to = input('Enter path to, e.g., ./distances/: ')
version = str(input('Enter version ID, e.g., 3: '))

all_files = glob.glob(path_to + 'road_dist_' + version + '_*.csv')
li = []
for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    print('loaded ' + filename)
    li.append(df)
df_tracts = pd.concat(li, axis=0, ignore_index=True)
# df_tracts = df_tracts.drop(columns=['Unnamed: 0.1.1','Unnamed: 0'])
df_tracts['DISTANCE_ROAD_MILES'] = df_tracts['DISTANCE_ROAD']/1609.34

output_filename = './distances_output/road_dist_' + version + '_ALL.csv'
df_tracts.to_csv(output_filename)

print('--------------------------------')
print('Finished exporting file to ./distances_output/: ' + output_filename)