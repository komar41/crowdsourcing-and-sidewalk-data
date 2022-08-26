import pandas as pd
import geopandas as gpd
import osmium
import pickle

class LatestHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.wkbfab = osmium.geom.WKBFactory()
        self.latest = []

    def read_parsed_data(self, city):
        pickle_in = open("data/parsed_osm/latest/%s.pickle"%(city),"rb")
        self.latest = pickle.load(pickle_in)

    def get_gdf(self, data):
        id = pd.Series([row[0] for row in data], dtype='UInt64')
        tags = pd.Series([row[1] for row in data])
        osm_type = pd.Series([row[2] for row in data], dtype='string')
        subtype = pd.Series([row[3] for row in data], dtype='string')
        geometry = gpd.GeoSeries.from_wkb([row[4] for row in data], crs='epsg:4326')

        return gpd.GeoDataFrame({
            'id': id,
            'tags': tags,
            'osm_type':  osm_type,
            'subtype': subtype,
            'geometry': geometry
        })

    def filter_data(self, qualifier):
        filtered = [i for i in self.latest if qualifier(i[1],i[2])]
        return filtered

    def node(self, n):
        id = n.id
        tags = dict(n.tags)

        try:
            point = self.wkbfab.create_point(n)
            self.latest.append([
                id,         # Id
                tags,       # Tag
                'N',        # OSM Type
                'Nodes',    # Subtype
                point       # Geometry
            ])
            
        except Exception as e:
            print(e)
            print(n)

    def way(self, w):
        id = w.id
        tags = dict(w.tags)
        
        # print(id)
        if('highway' in tags):
            try:
                line = self.wkbfab.create_linestring(w)
                self.latest.append([
                    id,         # Ids
                    tags,       # Tags
                    'W',        # OSM Type
                    'Highway',  # Subtype
                    line        # Geometry
                ])
                
            except Exception as e:
                print(e)
                print(w)
                
    def area(self, a):
        tags = dict(a.tags)
        id = int(a.orig_id())
        osm_type = 'W' if a.from_way() else 'R'
        
        if not (a.from_way() and 'highway' in tags):
            try:
                poly = self.wkbfab.create_multipolygon(a)
                self.latest.append([
                    id,               # Ids
                    tags,             # Tags
                    osm_type,         # OSM Type
                    'Multipolygons',  # Subtype
                    poly              # Geometry
                ])
            
            except Exception as e:
                print(e)
                print(a)

        