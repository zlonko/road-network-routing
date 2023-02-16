import pandas as pd
# from pandas.io.json import json_normalize
import glob
import json


def load_csv(filename_csv):
    df = pd.read_csv(filename_csv)
    return df


def load_geojson(filename_geojson):
    """
    Import GeoJSON file and convert to dataframe. Any level can be used: state, county, tract, etc.
    """
    df = pd.read_json(filename_geojson, orient='records')
    df = pd.json_normalize(df["features"])
    return df