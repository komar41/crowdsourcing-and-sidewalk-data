import pandas as pd
import geopandas as gpd
import numpy as np

import osmium

import re

# Qualifiers
def poi_qualifier(tags):
    return ('amenity' in tags or 'shop' in tags or 'tourism' in tags)

def building_qualifier(tags):
   return ( ('building' in tags) or ('building:part' in tags) or (tags.get('type') == 'building') ) and ( (tags.get('location') != 'underground') or ('bridge' not in tags) )


class AreaHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.id = []
        self.osm_type = []
        self.tags = []
        self.geometry = []
        self.wkbfab = osmium.geom.WKBFactory()
        
    def get_gdf(self, qualifier):
        n = len(self.tags)
        id_, osm_type_, geometry_ = [], [], []

        for i in range(n):
            qualifies = qualifier(self.tags[i]) # Callback function!!
            if qualifies:
                id_.append(self.id[i])
                osm_type_.append(self.osm_type[i])
                geometry_.append(self.geometry[i])

        id = pd.Series(id_, dtype='UInt64')
        osm_type = pd.Series(osm_type_, dtype='string')
        geometry = gpd.GeoSeries.from_wkb(geometry_, crs='epsg:4326')

        return  gpd.GeoDataFrame({
            'id': id,
            'osm_type':  osm_type,
            'geometry': geometry
        }, index=geometry.index)
    
    def area(self, a):
        tags = dict(a.tags)
        id = int(a.orig_id())
        
        try:
            self.id.append(id)
            if (not a.from_way()): self.osm_type.append('R')
            else: self.osm_type.append('W')
            self.tags.append(tags)
            poly = self.wkbfab.create_multipolygon(a) 
            self.geometry.append(poly)
            
        except Exception as e:
            print(e)
            print(a)