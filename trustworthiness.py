from util import *
from direct_indicators import *
from indirect_indicators import *
from time_indicator import *

def time_indicator(qualifier, l):
    time_ind = extract_time_indicator(qualifier, l)
    stats = get_stats(time_ind)
    avg = stats.loc['mean'].apply(np.ceil)[0] # Average last edit
    time_ind['Ttime'] = time_ind.apply(lambda row: 1 if row['last_edit(months)'] >= avg else 0, axis=1)

    return time_ind[['id', 'Ttime']]

def compute_Ti(stats, **kwargs):
    cnt = 0
    for key in kwargs:
        cnt  += 1 if kwargs[key] >= stats[key] else 0

    Ti = 1 if cnt >= 6 else 0

    return Ti

def indirect_indicator(qualifier, h, l):
    indir_ind = extract_indirect_indicators(qualifier, h, l)
    stats = get_stats_indir(indir_ind)

    # Using ceil(mean) as central tendency measure
    stats = stats.loc['mean'].apply(np.ceil).to_dict()

    indir_ind['Ti'] = indir_ind.apply(lambda row: compute_Ti(
                                                    stats,
                                                    road_cnt = row.road_cnt, 
                                                    road_uc = row.road_uc, 
                                                    road_le_time = row.road_le_time, 
                                                    building_cnt = row.building_cnt, 
                                                    building_uc = row.building_uc, 
                                                    building_le_time = row.building_le_time,
                                                    poi_cnt = row.poi_cnt,
                                                    poi_uc = row.poi_uc,
                                                    poi_le_time = row.poi_le_time,
                                                    target_cnt = row.target_cnt,
                                                    target_uc = row.target_uc,
                                                    target_le_time = row.target_le_time
                                                    ), 
                                                    axis=1)

    return indir_ind[['id', 'Ti']]

def compute_Td(stats, **kwargs):
    '''
    Formula:
    Td(F) = (Wnum.V_num) + (Wdir_c.Dir_C) + (Wuc.UC) + (Wedit.Tag_edits) + (WrollB.RollBk) + (WTag.Tag)
    Wnum = 0.2
    Wdir_c = 0.2
    Wuc = 0.2
    Wedit = 0.1
    WrollB = 0.1
    WTag = 0.2
    '''

    res = dict()
    for key in kwargs:
        res[key]  = 1 if kwargs[key] >= stats[key] else 0

    Wnum, Wdir_c, Wuc, Wedit, WrollB, WTag = 0.2, 0.2, 0.2, 0.1, 0.1, 0.2
    Td = (Wnum * res['nversions']) + (Wdir_c * res['dir_confirmations']) + \
         (Wuc * res['nusers']) + (Wedit * res['nedits']) + \
         (WrollB * res['nrollbacks']) + (WTag * res['ntags'])

    return Td

def direct_indicator(qualifier, h):
    dir_ind = extract_direct_indicators(qualifier, h)
    dir_ind = dir_ind[dir_ind['visibility'] == 'V'] # Exclude deleted or changed entries
    stats = get_stats_dir(dir_ind)

    # Using ceil(mean) as central tendency measure
    stats = stats.loc['mean'].apply(np.ceil).to_dict()

    dir_ind['Td'] = dir_ind.apply(lambda row: compute_Td(
                                                    stats,
                                                    nversions = row.nversions, 
                                                    dir_confirmations = row.dir_confirmations, 
                                                    nusers = row.nusers, 
                                                    nedits = row.nedits, 
                                                    nrollbacks = row.nrollbacks, 
                                                    ntags = row.ntags
                                                    ), 
                                                    axis=1)

    return dir_ind[['id', 'Td']]

def compute_trust(Td, Ti, Ttime):
    '''
    Formula:
    T(F) = Td(F).Wd + Ti(F).Wi + Ttime(F).Wtime
    Wd = 0.5
    Wi = 0.25
    Wtime = 0.25
    '''
    trust = Td * 0.5 + Ti * 0.25 + Ttime * 0.25
    return trust

def trustworthiness(qualifier, city = 'laf'):
    h = HistoryHandler()
    h.read_parsed_data(city)

    l = LatestHandler()
    l.read_parsed_data(city)

    dir_ind = direct_indicator(qualifier, h)
    indir_ind = indirect_indicator(qualifier, h, l)
    time_ind = time_indicator(qualifier, l)

    res = pd.merge(dir_ind, indir_ind, on="id")[['id', 'Td', 'Ti']]
    res = pd.merge(res, time_ind, on="id")[['id', 'Td', 'Ti', 'Ttime']]
    res['Trust'] = res.apply(lambda row: compute_trust(
                                                        row.Td,
                                                        row.Ti,
                                                        row.Ttime
                                                        ),
                                                        axis = 1)

    return res