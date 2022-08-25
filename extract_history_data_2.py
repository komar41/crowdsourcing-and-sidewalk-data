import osmium
import numpy as np
import pandas as pd

class HistoryHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.history = []

    def get_data(self, qualifier):
        return [i for i in self.history if qualifier(i[4],i[5])]
        
    def node(self, n):
        tags = dict(n.tags)
        self.history.append([
                                n.id,
                                '',
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
            members_list += ('[%s, %s],'%(str(i.ref), 'n'))
        
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
        members_list = ''
        
        for member in r.members:
            members_list += ('[%s, \'%s\', \'%s\'],'%(str(member.ref),str(member.type),str(member.role) ))
        members_list = members_list[:-1]

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