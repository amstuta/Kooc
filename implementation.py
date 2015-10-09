import cnorm
from mangler import *
from decl_keeper import *
from copy import deepcopy

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident
        self.alloc_fct = None

        self.imps = {}
        if self.ident in DeclKeeper.instance().classes:
            self.create_alloc_fct()
            
        for i in imp.body:
            if isinstance(i, cnorm.nodes.BlockStmt):
                for elem in i.body:
                    ret = self.check_param(elem)
                    if ret != None:
                        self.imps[ret._name] = ret
                        if '$init$' in ret._name:
                            self.create_new_fct(ret)
                    else:
                        dec_elem = Mangler.instance().muckFangle(elem, ident)
                        elem._name = dec_elem
                        self.imps[dec_elem] = elem

            else:
                ret = self.check_param(i)
                if ret != None:
                    self.imps[ret._name] = ret
                    if '$init$' in ret._name:
                        self.create_new_fct(ret)
                else:
                    dec_i = Mangler.instance().muckFangle(i, ident)
                    i._name = dec_i
                    self.imps[dec_i] = i


    def create_alloc_fct(self):

        decl = cnorm.nodes.FuncType(self.ident, [])
        decl = cnorm.nodes.Decl('alloc', decl)
        decl._ctype._decltype = cnorm.nodes.PointerType()
        decl.body = cnorm.nodes.BlockStmt([])
        decl._name = Mangler.instance().muckFangle(decl, self.ident)
        
        # Declaration de la struct
        dec = cnorm.nodes.Binary(cnorm.nodes.Raw('*'), [cnorm.nodes.Id(self.ident), cnorm.nodes.Id('self')])
        dec = cnorm.nodes.ExprStmt(dec)
        decl.body.body.append(dec)

        # Malloc de la struct
        sizeof = cnorm.nodes.Sizeof(cnorm.nodes.Raw('sizeof'), [cnorm.nodes.PrimaryType(self.ident)])
        func = cnorm.nodes.Func(cnorm.nodes.Id('malloc'), [sizeof])
        binary = cnorm.nodes.Binary(cnorm.nodes.Raw('='), [cnorm.nodes.Id('self'), func])
        expr = cnorm.nodes.ExprStmt(binary)
        decl.body.body.append(expr)

        # Return
        ret = cnorm.nodes.Paren('()', [cnorm.nodes.Id('self')])
        ret = cnorm.nodes.Return(ret)
        decl.body.body.append(ret)

        self.alloc_fct = decl
        self.imps[decl._name] = decl


    # Créé une fct new pour chaque init rencontré
    def create_new_fct(self, ini):
        params = []
        if len(ini._ctype._params) >= 1:
            params = ini._ctype._params[1:]
        decl = cnorm.nodes.FuncType(self.ident, params)
        decl = cnorm.nodes.Decl('new', decl)
        decl._ctype._decltype = cnorm.nodes.PointerType()
        decl._name = Mangler.instance().muckFangle(decl, self.ident)
        decl.body = cnorm.nodes.BlockStmt([])

        # Declaration de la struct
        dec = cnorm.nodes.Binary(cnorm.nodes.Raw('*'), [cnorm.nodes.Id(self.ident), cnorm.nodes.Id('self')])
        dec = cnorm.nodes.ExprStmt(dec)
        decl.body.body.append(dec)

        # Call d'alloc
        assign = cnorm.nodes.Binary(cnorm.nodes.Raw('='), [cnorm.nodes.Id('self'), cnorm.nodes.Func(cnorm.nodes.Id(self.alloc_fct._name), [])])
        assign = cnorm.nodes.ExprStmt(assign)
        decl.body.body.append(assign)

        # Call a init
        params = []
        for p in ini._ctype._params:
            params.append(cnorm.nodes.Id(p._name))
        func = cnorm.nodes.Func(cnorm.nodes.Id(ini._name), params)
        call = cnorm.nodes.ExprStmt(func)
        decl.body.body.append(call)

        # Return
        ret = cnorm.nodes.Paren('()', [cnorm.nodes.Id('self')])
        ret = cnorm.nodes.Return(ret)
        decl.body.body.append(ret)
        
        self.imps[decl._name] = decl


    # Ajoute le parametre self aux parametres de la fct membre
    def check_param(self, decl):
        if isinstance(decl._ctype, cnorm.nodes.FuncType):
            if not self.ident in DeclKeeper.instance().classes:
                return None
            cl = DeclKeeper.instance().classes[self.ident]
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
