import pandas as pd
import numpy as np

from collections import defaultdict
from datetime import datetime

from qualfiers import *

def extract_features(df, qualifier):
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
                     tags,
                     osm_type])


   colnames = ['id', 'nusers', 'ts', 'tags', 'osm_type']
   df = pd.DataFrame(values, columns=colnames)

   return df

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
    #  for difference in days: return (d1- d2).days


def compute_ii_parameters(df): # ii -> indirect indicators
    
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