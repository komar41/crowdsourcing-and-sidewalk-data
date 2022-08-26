import geopandas as gpd
import pandas as pd
from datetime import datetime
from collections import defaultdict

from util import *
from extract_history_data import *
from extract_latest_data import *

def process_history_features(df, qualifier): # rename extract_ii_features
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

def merge_history_geom(h, l, qualifier, item_type):
    filtered = h.filter_data(qualifier)
    df = h.get_df(filtered)[['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']]
    df = df.sort_values(by=['id', 'ts'])
    
    history = process_history_features(df, qualifier)
    
    filtered = l.filter_data(qualifier)
    geom = l.get_gdf(filtered)

    merged = pd.merge(history, geom,  how='inner', left_on=['id','osm_type'], right_on = ['id','osm_type'])
    merged = gpd.GeoDataFrame(merged, crs="EPSG:4326")
    merged['item_type'] = item_type

    return merged

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


def extract_indirect_indicators(qualifier, city = 'rec'): # Pass h and l as parameters

    h = HistoryHandler()
    h.read_parsed_data(city) # Load it in compute trustworthiness once and then use for dir and indir ind

    l = LatestHandler()
    l.read_parsed_data(city)

    poi = merge_history_geom(h, l, poi_qualifier, 'poi')
    road = merge_history_geom(h, l, highway_qualifier, 'road')
    building = merge_history_geom(h, l, building_qualifier, 'building')
    target_type_indir = merge_history_geom(h, l, qualifier, 'target')

    gdf = pd.concat([building, road, poi, target_type_indir])
    gdf = gdf.reset_index(drop=True)
    gdf = gpd.GeoDataFrame(gdf, crs="EPSG:4326")
    gdf = gdf.to_crs('epsg:3395')

    indir_ind = compute_cells(gdf)

    return indir_ind

def get_stats_indir(indir_ind):
    stats = indir_ind.describe()[['road_cnt', 'road_uc', 'road_le_time', 'building_cnt', 'building_uc', 'building_le_time', 'poi_cnt', 'poi_uc', 'poi_le_time', 'target_cnt', 'target_uc', 'target_le_time']]
    stats = stats.filter(items = ['mean', '25%', '50%'], axis=0)

    return stats
