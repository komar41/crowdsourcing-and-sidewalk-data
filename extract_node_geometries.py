import pandas as pd
import geopandas as gpd
import numpy as np

import osmium

import re

# Qualifiers
def poi_qualifier(tags):
    return ('amenity' in tags or 'shop' in tags or 'tourism' in tags)

class NodeHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.id = []
        self.lat = []
        self.lon = []
        self.osm_type = []
        self.tags = []

    def get_gdf(self, qualifier):

        n = len(self.tags)
        values = []

        for i in range(n):
            qualifies = qualifier(self.tags[i]) # Callback function!!
            if qualifies:
                values.append([
                           self.id[i],
                           self.osm_type[i],
                           self.lat[i],
                           self.lon[i]
                           ])

        colnames = ['id', 'osm_type', 'lat', 'lon']
        nodes = pd.DataFrame(values, columns=colnames)
        gdf = gpd.GeoDataFrame(nodes, geometry=gpd.points_from_xy(nodes.lon, nodes.lat), crs="EPSG:4326")
        gdf = gdf.drop(['lon','lat'], axis = 1)
        gdf = gdf.to_crs('epsg:3395')

        return gdf
        
    def node(self, n):
        tags = dict(n.tags)
        
        try:
            lon, lat = (str(n.location)).split('/')
            lon, lat = float(lon), float(lat)
        except:
            lon = lat = np.nan

        self.id.append(n.id)
        self.lat.append(lat)
        self.lon.append(lon)
        self.osm_type.append('N')
        self.tags.append(tags)
        