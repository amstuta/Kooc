import cnorm
from mangler import *

class Class:

    def __init__(self, class_name, statement, recurs):
        self.ident = class_name
        self.recurs = recurs

        self.members = {}
        if hasattr(statement, 'members'):
            for m in statement.members:
                if isinstance(m, cnorm.nodes.BlockStmt):
                    for i in m.body:
                        dec_i = Mangler.instance().muckFangle(i, class_name)
                        i._name = dec_i
                        self.members[dec_i] = i
                else:
                    dec_m = Mangler.instance().muckFangle(m, class_name)
                    m._name = dec_m
                    self.members[dec_m] = m

        self.decls = {}
        for d in statement.body:
            if isinstance(d, cnorm.nodes.BlockStmt):
                for i in d.body:
                    dec_i = Mangler.instance().muckFangle(i, class_name)
                    i._name = dec_i
                    self.decls[dec_i] = i
            else:
                dec_d = Mangler.instance().muckFangle(d, class_name)
                d._name = dec_d
                self.decls[dec_d] = d


    def register_typedef(self):
        decl = cnorm.nodes.Decl(self.ident, cnorm.nodes.ComposedType('_kc_' + self.ident))
        decl._ctype._specifier = 1
        decl._ctype._storage = cnorm.nodes.Storages.TYPEDEF
        if not hasattr(decl._ctype, 'fields'):
            setattr(decl._ctype, 'fields', [])
        for mem in self.members:
            if type(self.members[mem]._ctype) != cnorm.nodes.FuncType:
                decl._ctype.fields.append(self.members[mem])
        for d in self.decls:
            item = self.decls[d]
            if type(item._ctype) == cnorm.nodes.FuncType:
                continue
            item._ctype._storage = cnorm.nodes.Storages.STATIC
            decl._ctype.fields.append(item)
        return decl
        


    def decl_exists(self, ident):
        if ident in self.decls:
            return True
        return False

    def get_decl(self, ident):
        if self.decl_exists(ident):
            return self.decls[ident]
        return None

    def member_exists(self, ident):
        if ident in self.members:
            return True
        return False

    def __getitem__(self, ident):
        if self.member_exists(ident):
            return self.members[ident]
        return None
