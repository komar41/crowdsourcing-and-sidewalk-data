from extract_points import NodeHandler


def extract_time_indicators(qualifier, city = 'rec'):
    h_n  = NodeHandler()
    h_r.apply_file("data/osm/latest/" + city + ".osm.pbf")
    
    h_r = RelationHandler()
    h_r.apply_file("data/osm/latest/" + city + ".osm.pbf")

    h_w = WayHandler()
    h_w.apply_file("data/osm/latest/" + city + ".osm.pbf")

    colnames = ['id', 'nodes/ways', 'version', 'visible', 'ts', 'uid', 'chgset', 'ntags', 'tags', 'type']
    history = pd.DataFrame(h_r.history_relation + h_w.history_way, columns=colnames)
    history = history.sort_values(by=['id', 'ts'])

    time = gdf[gdf['item_type'] == 'building'][['id','ts']]
    time['last_edit(months)'] = [diff_month(datetime.now(), row) for row in time['ts']]


def get_stats(dir_ind):
    stats = dir_ind.describe()[['nversions', 'nusers', 'nedits', 'ntags', 'dir_confirmations', 'nrollbacks']]
    stats = stats.filter(items = ['mean', '25%', '50%'], axis=0)

    return stats