from extract_latest_data import *
from util import *
from datetime import datetime
import pandas as pd

def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def extract_time_indicator(qualifier, l): # h as parameter
    filtered = l.filter_data(qualifier)
    time = l.get_gdf(filtered)[['id', 'ts']]
    time = time.sort_values(by=['id', 'ts'])
    time['last_edit(months)'] = [diff_month(datetime.now(), row) for row in time['ts']]

    return time

def get_stats(time):
    stats = time.describe()[['last_edit(months)']]
    stats = stats.filter(items = ['mean', '50%'], axis=0)

    return stats