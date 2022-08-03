# This can also be a separate python module!! Tomorrow first thing!
import osmium
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
                                n.visible,
                                pd.Timestamp(n.timestamp, unit='s'),
                                n.uid,
                                tags,
                                'N'])

    def way(self, w):
        tags = dict(w.tags)
        self.history.append([
                                w.id,
                                w.visible,
                                pd.Timestamp(w.timestamp, unit='s'),
                                w.uid,
                                tags,
                                'W'])

    def relation(self, r):
        tags = dict(r.tags)
        self.history.append([
                                r.id,
                                r.visible,
                                pd.Timestamp(r.timestamp, unit='s'),
                                r.uid,
                                tags,
                                'R'])