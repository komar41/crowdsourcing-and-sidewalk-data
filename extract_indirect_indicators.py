import geopandas as gpd
from shapely.geometry import box
import pyrosm

import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict

from util import *
from extract_history_data import *
from extract_points import *
from extract_multipolygons import *
from extract_linestrings import *

def extract_ii_features(df, qualifier): # rename extract_ii_features
   values = []

   mp = defaultdict(int)
   for item in df.to_numpy():
      item_id = item[0]

      if(not mp[item_id]):
         mp[item_id] = 1

         all_versions = df[df['id']==item_id]
         n = len(all_versions)
         users = all_versions['uid'].unique() # unique users contributing to the item

         last = all_versions.iloc[n-1]
         ts = last['ts']
         tags = last['tags']
         osm_type = last['osm_type']

         if( not last['visible'] or not qualifier(tags, osm_type) ): continue # If changed to something other than poi in the last version or is deleted
         values.append([item_id,
                     users,
                     ts,
                     osm_type])


   colnames = ['id', 'nusers', 'ts', 'osm_type']
   df = pd.DataFrame(values, columns=colnames)

   return df

def get_poi_indir(h, h_n, h_wr):
    data_poi = h.get_data(poi_qualifier)
    colnames = ['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']
    history = pd.DataFrame(data_poi, columns=colnames)
    history = history.sort_values(by=['id', 'ts'])

    poi = extract_ii_features(history, poi_qualifier)

    poi_n = h_n.get_gdf(poi_qualifier)
    poi_wr = h_wr.get_gdf(poi_qualifier)

    poi_geom = pd.concat([poi_n, poi_wr])
    poi_indir = pd.merge(poi, poi_geom,  how='inner', left_on=['id','osm_type'], right_on = ['id','osm_type'])
    poi_indir = gpd.GeoDataFrame(poi_indir, crs="EPSG:4326")
    poi_indir['item_type'] = 'poi'

    return poi_indir

def get_road_indir(h, h_roads):
    data_road = h.get_data(highway_qualifier)

    colnames = ['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']
    history = pd.DataFrame(data_road, columns=colnames)
    history = history.sort_values(by=['id', 'ts'])

    road = extract_ii_features(history, highway_qualifier)
    road_geom = h_roads.get_gdf(highway_qualifier)

    roads_indir = pd.merge(road, road_geom, how='inner', left_on=['id','osm_type'], right_on = ['id','osm_type'])
    roads_indir = gpd.GeoDataFrame(roads_indir, crs="EPSG:4326")
    roads_indir['item_type'] = 'road'

    return roads_indir

def get_target_indir(qualifier, h, h_roads):
    data_road = h.get_data(qualifier)

    colnames = ['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']
    history = pd.DataFrame(data_road, columns=colnames)
    history = history.sort_values(by=['id', 'ts'])

    target = extract_ii_features(history, qualifier)
    target_geom = h_roads.get_gdf(qualifier)

    target_indir = pd.merge(target, target_geom, how='inner', left_on=['id','osm_type'], right_on = ['id','osm_type'])
    target_indir = gpd.GeoDataFrame(target_indir, crs="EPSG:4326")
    target_indir['item_type'] = 'target'

    return target_indir

def get_building_indir(h, h_wr):
    data = h.get_data(building_qualifier)

    colnames = ['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']
    history = pd.DataFrame(data, columns=colnames)
    history = history.sort_values(by=['id', 'ts'])

    building = extract_ii_features(history, building_qualifier)
    building_geom = h_wr.get_gdf(building_qualifier)

    building_indir = pd.merge(building, building_geom,  how='inner', on = ['id', 'osm_type'])
    building_indir = gpd.GeoDataFrame(building_indir, crs="EPSG:4326")
    building_indir['item_type'] = 'building'

    return building_indir

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
    #  for difference in days: return (d1- d2).days

def compute_indirect_indicators(df): # ii -> indirect indicators
    
    if(not len(df.index)): element_cnt, user_cnt, last_edit_time = 0, 0, 0
    else:
      mp = defaultdict(int)
      user_cnt = 0
      last_edit_time = df['ts'].iloc[0]

      for item in df.to_numpy():
         users = item[1]
         for user in users:
               if(not mp[user]): 
                  mp[user] = 1
                  user_cnt += 1

         edit_time = item[2]
         last_edit_time = max(edit_time, last_edit_time)

      last_edit_time = diff_month(datetime.now(), last_edit_time)
      element_cnt = len(df.index)

    return element_cnt, user_cnt, last_edit_time

def compute_cells(gdf):
    # Have to make one more consideration: if one building can be part of multiple cell. Do check that tomorrow!!

    size = 1000
    xmin, ymin, xmax, ymax= gdf.total_bounds
    cell_width = cell_height = size

    indir_indicators = []
    mp = defaultdict(int)
    for x0 in np.arange(xmin, xmax+cell_width, cell_width):
        for y0 in np.arange(ymin, ymax+cell_height, cell_height):
            x1 = x0+cell_width
            y1 = y0+cell_height

            cell = gdf.cx[x0:x1, y0:y1]
            
            # short form: uc -> user count, le_time -> last edit time
            roads = cell[cell['item_type'] == 'road']
            road_cnt, road_uc, road_le_time = compute_indirect_indicators(roads)

            buildings = cell[cell['item_type'] == 'building']
            building_cnt, building_uc, building_le_time = compute_indirect_indicators(buildings)

            pois = cell[cell['item_type'] == 'poi']
            poi_cnt, poi_uc, poi_le_time = compute_indirect_indicators(pois)

            targets = cell[cell['item_type'] == 'target']
            target_cnt, target_uc, target_le_time = compute_indirect_indicators(targets)
  
            for item in targets.to_numpy():
                if(not mp[item[0]]):
                    mp[item[0]] = 1
                    indir_indicators.append([
                                            item[0], 
                                            road_cnt, 
                                            road_uc, 
                                            road_le_time, 
                                            building_cnt, 
                                            building_uc, 
                                            building_le_time, 
                                            poi_cnt, 
                                            poi_uc, 
                                            poi_le_time,
                                            target_cnt,
                                            target_uc,
                                            target_le_time
                                            ])

    colnames = ['id', 
                'road_cnt', 
                'road_uc', 
                'road_le_time', 
                'building_cnt', 
                'building_uc', 
                'building_le_time', 
                'poi_cnt', 
                'poi_uc', 
                'poi_le_time', 
                'target_cnt', 
                'target_uc', 
                'target_le_time']

    indir = pd.DataFrame(indir_indicators, columns=colnames)

    return indir


def extract_indirect_indicators(qualifier, city = 'rec'):

    h = HistoryHandler()
    h.apply_file('data/osm/historical/'+ city + '_historical.osm.pbf')

    h_n = NodeHandler()
    h_n.apply_file('data/osm/latest/'+ city + '.osm.pbf')

    h_wr = AreaHandler()
    h_wr.apply_file('data/osm/latest/'+ city + '.osm.pbf')

    h_roads = WayHandler()
    h_roads.apply_file('data/osm/latest/'+ city + '.osm.pbf', locations = True)

    poi_indir = get_poi_indir(h, h_n, h_wr)
    roads_indir = get_road_indir(h, h_roads)
    building_indir = get_building_indir(h, h_wr)
    # sidewalk_indir = get_sidewalk_indir(h, h_roads)
    # with_sidewalk_tag_indir = highway_with_sidewalk_tag(h, h_roads)
    target_type_indir = get_target_indir(qualifier, h, h_roads)

    gdf = pd.concat([building_indir, roads_indir, poi_indir, target_type_indir])
    gdf = gdf.reset_index(drop=True)
    gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326")
    gdf = gdf.to_crs('epsg:3395')

    indir_ind = compute_cells(gdf)

    return indir_ind

def get_stats_indir(indir_ind):
    stats = indir_ind.describe()[['road_cnt', 'road_uc', 'road_le_time', 'building_cnt', 'building_uc', 'building_le_time', 'poi_cnt', 'poi_uc', 'poi_le_time', 'target_cnt', 'target_uc', 'target_le_time']]
    stats = stats.filter(items = ['mean', '25%', '50%'], axis=0)

    return stats
