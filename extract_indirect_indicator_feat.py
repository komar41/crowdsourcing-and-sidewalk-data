from collections import defaultdict
import pandas as pd

def poi_qualifier(tags):
   return ('amenity' in tags or 'shop' in tags or 'tourism' in tags)

def road_qualifier(tags):
    return 'highway' in tags

def building_qualifier(tags):
    pass

def extract_features(df, qualifier):
   values = []

   mp = defaultdict(int)
   for item in df.to_numpy():
      item_id = item[0]
      tags = item[4]
      osm_type = item[5]


      if(not mp[item_id]):
         mp[item_id] = 1

         all_versions = df[df['id']==item_id]
         n = len(all_versions)
         num_users = all_versions['uid'].nunique() # Number of unique users contributing to per building
         last = all_versions.iloc[n-1]
         ts = last['ts']
         if( not last['visible'] or not qualifier(last['tags']) ): continue # If changed to something other than poi in the last version or is deleted


         values.append([item_id,
                     num_users,
                     ts,
                     tags,
                     osm_type])


   colnames = ['id', 'nusers', 'ts', 'tags', 'osm_type']
   df = pd.DataFrame(values, columns=colnames)

   return df