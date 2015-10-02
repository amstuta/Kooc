import cnorm
from mangler import *
from copy import deepcopy
from decl_keeper import *

class Class:

    def __init__(self, class_name, statement, recurs):
        self.ident = class_name
        self.recurs = recurs
        self.protos = []

        # Ajoute aux membres les fcts qui recoivent une instance de l'objet en first param
        self.check_first_param(statement)

        # Mangling des save des membres
        self.members = {}
        if hasattr(statement, 'members'):
            for m in statement.members:
                if isinstance(m, cnorm.nodes.BlockStmt):
                    for i in m.body:
                        self.add_self_param(i)
                        dec_i = Mangler.instance().muckFangle(i, class_name)
                        i._name = dec_i
                        self.members[dec_i] = i
                else:
                    self.add_self_param(m)
                    dec_m = Mangler.instance().muckFangle(m, class_name)
                    m._name = dec_m
                    self.members[dec_m] = m

        # Mangling et save des non membres
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

        self.get_inheritance()
        self.add_inheritance()


    # Ecrit le typedef struct
    def register_typedef(self):
        decl = cnorm.nodes.Decl(self.ident, cnorm.nodes.ComposedType('_kc_' + self.ident))
        decl._ctype._specifier = 1
        decl._ctype._storage = cnorm.nodes.Storages.TYPEDEF
        if not hasattr(decl._ctype, 'fields'):
            setattr(decl._ctype, 'fields', [])

        parent = None
        if 'parent' in self.members:
            parent = deepcopy(self.members['parent'])
            del self.members['parent']
            decl._ctype.fields.append(parent)

        for mem in self.members:
            if type(self.members[mem]._ctype) != cnorm.nodes.FuncType:
                decl._ctype.fields.append(self.members[mem])
            else:
                self.protos.append(self.members[mem])
        for d in self.decls:
            item = self.decls[d]
            if type(item._ctype) == cnorm.nodes.FuncType:
                self.protos.append(item)
                continue
            item._ctype._storage = cnorm.nodes.Storages.STATIC
            decl._ctype.fields.append(item)
        if parent != None:
            self.members['parent'] = parent
        return decl


    # Ajoute le parametre self pour les fcts membres
    def add_self_param(self, decl):
        param = cnorm.nodes.Decl('self', cnorm.nodes.PrimaryType(self.ident))
        param._ctype._decltype = cnorm.nodes.PointerType()
        if isinstance(decl._ctype, cnorm.nodes.FuncType):
            if decl._ctype._params != [] and decl._ctype._params[0]._ctype._identifier == self.ident:
                return
            decl._ctype._params.insert(0, deepcopy(param))


    # Deplace des decls dans les membres si le premier param est un
    # pointeur sur un instance de la classe
    def check_first_param(self, statement):
        for decl in statement.body:
            if isinstance(decl, cnorm.nodes.BlockStmt):
                for i in decl.body:
                    
                    if isinstance(i, cnorm.nodes.FuncType) and i._ctype._params != []:
                        if i._ctype._params[0]._ctype._identifier == self.ident:
                            statement.members.append(deepcopy(i))
                            decl.body.remove(i)
            else:
                if isinstance(decl, cnorm.nodes.FuncType) and decl._ctype._params != []:
                    if decl._ctype._params[0]._ctype._identifier == self.ident:
                        statement.members.append(deepcopy(decl))
                        statement.body.remove(decl)


    def get_inheritance(self):
        if not self.ident in DeclKeeper.instance().inher:
            return
        mom = DeclKeeper.instance().inher[self.ident]
        decl = cnorm.nodes.Decl('parent', cnorm.nodes.PrimaryType(mom))
        self.members['parent'] = decl


    def add_inheritance(self):
        mom = DeclKeeper.instance().inher[self.ident]
        obj = DeclKeeper.instance().classes[mom]

        for mem_id in obj.members:
            mem = obj.members[mem_id]
            ident = Mangler.instance().changeClass(mem, self.ident, mom)
            tmp = deepcopy(mem)
            tmp._name = ident
            self.members[ident] = tmp

        for decl_id in obj.decls:
            decl = obj.decls[decl_id]
            ident = Mangler.instance().changeClass(decl, self.ident, mom)
            tmp = deepcopy(decl)
            tmp._name = ident
            self.decls[ident] = tmp


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
