import osmium
import pickle
import numpy as np
import pandas as pd
from util import *

class HistoryHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.history = []

    def read_parsed_data(self, city):
        pickle_in = open("data/parsed_osm/historical/%s_historical.pickle"%(city),"rb")
        self.history = pickle.load(pickle_in)

    def get_df(self, data):
        id = pd.Series([row[0] for row in data], dtype='Int64')
        members = pd.Series([row[1] for row in data])
        version = pd.Series([row[2] for row in data], dtype='Int64')
        visible = pd.Series([row[3] for row in data], dtype='bool')
        ts = pd.Series([row[4] for row in data]).dt.tz_localize(None)
        uid = pd.Series([row[5] for row in data], dtype='Int64')
        changeset = pd.Series([row[6] for row in data], dtype='Int64')
        ntags = pd.Series([row[7] for row in data], dtype ='Int32')
        tags = pd.Series([row[8] for row in data])
        osm_type = pd.Series([row[9] for row in data], dtype='string')

        return pd.DataFrame({
            'id': id,
            'members': members,
            'version':  version,
            'visible': visible,
            'ts': ts,
            'uid': uid,
            'changeset': changeset,
            'ntags': ntags,
            'tags': tags,
            'osm_type': osm_type
        })

    def filter_data(self, qualifier):
        filtered = [i for i in self.history if qualifier(i[8],i[9])]
        return filtered
        
    def node(self, n):
        tags = dict(n.tags)
        self.history.append([
                                n.id,
                                np.nan,
                                n.version,
                                n.visible,
                                pd.Timestamp(n.timestamp, unit='s'),
                                n.uid,
                                n.changeset,
                                len(n.tags),
                                tags,
                                'N'])

    def way(self, w):
        tags = dict(w.tags)
        members_list = []

        for i in list(w.nodes):
            members_list.append( (i.ref, 'n') )
        
        self.history.append([
                                w.id,
                                members_list,
                                w.version,
                                w.visible,
                                pd.Timestamp(w.timestamp),
                                w.uid,
                                w.changeset,
                                len(w.tags),
                                tags,
                                'W'])

    def relation(self, r):
        tags = dict(r.tags)
        members_list = []
        
        for member in r.members:
            members_list.append( (member.ref, member.type, member.role) )

        self.history.append([
                                r.id,
                                members_list,
                                r.version,
                                r.visible,
                                pd.Timestamp(r.timestamp),
                                r.uid,
                                r.changeset,
                                len(r.tags),
                                tags,
                                'R'])