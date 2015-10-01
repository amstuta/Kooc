from mangler import *

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident

        self.imps = {}
        for i in imp.body:
            if isinstance(i, cnorm.nodes.BlockStmt):
                for elem in i.body:
                    dec_elem = Mangler.instance().muckFangle(elem, ident)
                    elem._name = dec_elem
                    self.imps[dec_elem] = elem
            else:
                dec_i = Mangler.instance().muckFangle(i, ident)
                i._name = dec_i
                self.imps[dec_i] = i


    def __getitem__(self, ident):
        if ident in self.imps:
            return self.imps[ident]
        return None
