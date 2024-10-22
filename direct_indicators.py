from collections import defaultdict

from util import *
from extract_history_data import *

def compute_direct_indicators(df, qualifier):
   direct_indicators = []

   mp = defaultdict(int)
   for item in df.to_numpy():
      item_id = item[0]

      tags = item[8]
      item_type = item[9]
      qualifies = qualifier(tags, item_type)

      if(not mp[item_id] and qualifies):
         mp[item_id] = 1

         all_versions = df[df['id']==item_id]
         n = len(all_versions)
         
         num_rollbacks = 0
         num_edits = 0
         num_users = all_versions['uid'].nunique() # Number of unique users contributing to per building
         num_versions = all_versions.iloc[n-1]['version'] # Number of versions of the building
         num_tags = all_versions.iloc[n-1]['ntags'] # Number of tags in the latest version of the building
         visibility = 'V' # visibility: V: visible / C: Changed / D: Deleted

         deletion = 0
         addition = 0
         change = 0
         direct_confirmations = 0
         latest_tags = dict()

         for i in range(1, n):
            
            prev = all_versions.iloc[i-1] 
            cur = all_versions.iloc[i]

            prev_tags = prev['tags']
            cur_tags = cur['tags']

            prev_n_w = prev['members']
            cur_n_w = cur['members']

            prev_uid = prev['uid']
            cur_uid = cur['uid']

            # Rollback: 
            # If the geometry or the tags of cur does not match with the prev, check if it matches with any other previous versions. If so, count it as a rollback.
            if(cur_n_w != prev_n_w or cur_tags != prev_tags):
               for k in range(i-1):
                  if(cur_n_w == all_versions.iloc[k]['members'] and cur_tags == all_versions.iloc[k]['tags']):
                     num_rollbacks += 1

            # Direct Confirmations:         
            if(cur_uid != prev_uid and cur_n_w == prev_n_w): # If different users mapped the same geometry for a building, we would count it as direct confirmation
               direct_confirmations += 1

            for key in prev_tags: # Number of deleted tags in the newer version
               if key not in cur_tags:
                  deletion += 1

            for key in cur_tags: # Number of newly added tags in the newer version
               if key not in prev_tags:
                  addition += 1

            for key in cur_tags: # Number of tags that were changed in the newer version
               if key in prev_tags:
                  if(cur_tags[key] != prev_tags[key]):
                     change += 1

            if(i == n-1):
               if(not cur['visible']): visibility = "D" # Deleted: if on the latest version -> no tags and no nodes
               elif(not qualifier(cur_tags, item_type)): visibility = "C" # Not Building: else if on the latest version -> no tags that qualify for a building
               latest_tags = cur_tags

         if(n == 1): latest_tags = tags

         # Edits
         num_edits = deletion + addition + change

         direct_indicators.append([item_id,
                                 num_versions,
                                 num_users,
                                 num_edits,
                                 num_tags,
                                 direct_confirmations,
                                 num_rollbacks,
                                 visibility,
                                 latest_tags,
                                 item_type])


   colnames = ['id', 'nversions', 'nusers', 'nedits', 'ntags', 'dir_confirmations', 'nrollbacks', 'visibility', 'tags', 'type']
   dir_ind = pd.DataFrame(direct_indicators, columns=colnames)
   
   return dir_ind

def extract_direct_indicators(qualifier, h): # pass h by parameter
    history = h.get_df(h.history)
    history = history.sort_values(by=['id', 'ts'])

    dir_ind = compute_direct_indicators(history, qualifier)
    return dir_ind

def get_stats_dir(dir_ind):
    stats = dir_ind.describe()[['nversions', 'nusers', 'nedits', 'ntags', 'dir_confirmations', 'nrollbacks']]
    stats = stats.filter(items = ['mean', '25%', '50%'], axis=0)

    return stats