import pandas as pd
import geopandas as gpd

import osmium

from util import *
from qualfiers import * 

class WayHandler(osmium.SimpleHandler, DefaultOsmium):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        DefaultOsmium.__init__(self)

    def way(self, w):
        tags = dict(w.tags)
        id = int(w.id)
        
        # print(id)
        if('highway' in tags):
            try:
                self.id.append(id)
                self.tags.append(tags)
                self.osm_type.append('W')
                line = self.wkbfab.create_linestring(w)
                self.geometry.append(line)
                
            except Exception as e:
                print(e)
                print(w)