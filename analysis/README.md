# Instructions to run road distances with OSMNX library:

## Install requirements

### 1. Open a terminal window, navigate to the road_distance folder on your desktop.

cd Desktop/road_distance

### 2. Copy-paste and run the following to install the requirements

pip install networkx

conda config --prepend channels conda-forge
conda create -n ox --strict-channel-priority osmnx

### 3. Initiate "conda" instance with the following terminal command. This creates a virtual environment with all of the requirements for the OSMNX library.

conda activate ox

## Run Python file

python road_routing.py

### This should start the road routing process.


