import osmium
import pandas as pd
import geopandas as gpd

class DefaultOsmium():

    def __init__(self):
        self.id = []
        self.tags = []
        self.osm_type = []
        self.geometry = []
        self.wkbfab = osmium.geom.WKBFactory()


    def get_gdf(self, qualifier):
        n = len(self.tags)
        id_, tags_, osm_type_, geometry_ = [], [], [], []
        for i in range(n):
            qualifies = qualifier(self.tags[i], self.osm_type[i]) # Callback function!!
            if qualifies:
                id_.append(self.id[i])
                tags_.append(self.tags[i])
                osm_type_.append(self.osm_type[i])
                geometry_.append(self.geometry[i])

        id = pd.Series(id_, dtype='UInt64')
        tags = pd.Series(tags_)
        osm_type = pd.Series(osm_type_, dtype='string')
        geometry = gpd.GeoSeries.from_wkb(geometry_, crs='epsg:4326')

        return  gpd.GeoDataFrame({
            'id': id,
            'tags': tags,
            'osm_type':  osm_type,
            'geometry': geometry
        })