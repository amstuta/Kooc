import cnorm
from mangler import *
from decl_keeper import *
from copy import deepcopy

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident

        self.imps = {}
        for i in imp.body:
            if isinstance(i, cnorm.nodes.BlockStmt):
                for elem in i.body:
                    ret = self.check_param(elem)
                    if ret != None:
                        self.imps[ret._name] = ret
                    else:
                        dec_elem = Mangler.instance().muckFangle(elem, ident)
                        elem._name = dec_elem
                        self.imps[dec_elem] = elem
            else:
                ret = self.check_param(i)
                if ret != None:
                    self.imps[ret._name] = ret
                else:
                    dec_i = Mangler.instance().muckFangle(i, ident)
                    i._name = dec_i
                    self.imps[dec_i] = i


    # Ajoute le parametre self aux parametres de la fct membre
    def check_param(self, decl):
        if isinstance(decl._ctype, cnorm.nodes.FuncType):
            if not DeclKeeper.instance().class_exists(self.ident):
                return None
            cl = DeclKeeper.instance().get_class(self.ident)
            param = cnorm.nodes.Decl('self', cnorm.nodes.PrimaryType(self.ident))
            param._ctype._decltype = cnorm.nodes.PointerType()
            if decl._ctype._params != [] and decl._ctype._params[0]._ctype._identifier == self.ident:
                return None
            dc = deepcopy(decl)
            dc._ctype._params.insert(0, param)
            dc._name = Mangler.instance().muckFangle(dc, self.ident)
            
            if dc._name in cl.members:
                return dc
            return None


    def __getitem__(self, ident):
        if ident in self.imps:
            return self.imps[ident]
        return None
