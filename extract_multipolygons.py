import pandas as pd
import geopandas as gpd
import shapely.wkb as wkblib
import numpy as np

import osmium
import re

from util import *

class AreaHandler(osmium.SimpleHandler, DefaultOsmium):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        DefaultOsmium.__init__(self)

    def area(self, a):
        tags = dict(a.tags)
        id = int(a.orig_id())
        
        if not (a.from_way() and 'highway' in tags): # Highways are linestrings and not multipolygon
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