from mangler import *

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident

        self.imps = {}
        for i in imp.body:
            self.imps[Mangler.instance().muckFangle(ident, i)] = i


    def __getitem__(self, ident):
        if ident in self.imps:
            return self.imps[ident]
        return None
