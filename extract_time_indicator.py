from extract_history_data_2 import *
from util import *
from datetime import datetime
import pandas as pd

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def extract_time_indicator(qualifier, city = 'rec'): # h as parameter
    h = HistoryHandler()
    h.apply_file("data/osm/latest/" + city + ".osm.pbf")

    filtered = h.filter_data(qualifier)
    time = h.get_df(filtered)[['id', 'visible', 'ts', 'uid', 'tags', 'osm_type']]
    time = time.sort_values(by=['id', 'ts'])

    time = time[['id','ts']]
    time['last_edit(months)'] = [diff_month(datetime.now(), row) for row in time['ts']]

    return time

def get_stats(time):
    stats = time.describe()[['last_edit(months)']]
    stats = stats.filter(items = ['mean', '50%'], axis=0)

    return stats