import pandas as pd
import geopandas as gpd
import numpy as np

import osmium
import re

# Qualifiers
def building_qualifier(tags):
   return ( ('building' in tags) or ('building:part' in tags) or (tags.get('type') == 'building') ) and ( (tags.get('location') != 'underground') or ('bridge' not in tags) )

def road_qualifier(tags):
    return 'highway' in tags

def poi_qualifier(tags):
    return 'amenity' in tags

class AreaHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.id = []
        self.type = []
        self.tags = []
        self.geometry = []
        self.wkbfab = osmium.geom.WKBFactory()
        
    def get_buildings(self):
        n = len(self.tags)
        geom, iid, typ = [], [], []

        for i in range(n):
            qualifies = building_qualifier(self.tags[i]) # Callback Function!!
            if qualifies:
                iid.append(self.geometry[i])
                typ.append(self.type[i])
                geom.append(self.id[i])

        id = pd.Series(iid, dtype='UInt64')
        type = pd.Series(typ, dtype='string')
        geometry = gpd.GeoSeries.from_wkb(geom, crs='epsg:4326')

        return  gpd.GeoDataFrame({
            'id': id,
            'geometry': geometry,
            'type':  type
        }, index=geometry.index)
    
    def area(self, a):
        tags = dict(a.tags)
        id = int(a.orig_id())
        
        try:
            self.id.append(id)
            if (not a.from_way()): self.type.append('R')
            else: self.type.append('W')
            self.tags.append(tags)
            poly = self.wkbfab.create_multipolygon(a)     
            self.geometry.append(poly)
            
        except Exception as e:
            print(e)
            print(a)