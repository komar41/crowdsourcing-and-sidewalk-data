import pandas as pd
import geopandas as gpd
import numpy as np

import osmium

from util import *
from qualfiers import *


class NodeHandler(osmium.SimpleHandler, DefaultOsmium):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        DefaultOsmium.__init__(self)
        
    def node(self, n):
        tags = dict(n.tags)
        id = n.id

        try:
            self.id.append(id)
            self.tags.append(tags)
            self.osm_type.append('N')
            point = self.wkbfab.create_point(n)
            self.geometry.append(point)

        except Exception as e:
            print(n)
            print(e)
        