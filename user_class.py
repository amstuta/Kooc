import cnorm
from mangler import *
from copy import deepcopy
from decl_keeper import *

class Class:

    def __init__(self, class_name, statement, recurs):
        self.ident = class_name
        self.recurs = recurs
        self.protos = []
        self.vt = None

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

        # Mangling et save des virtuals
        self.virtuals = {}
        if hasattr(statement, 'virtuals'):
            for v in statement.virtuals:
                if isinstance(v, cnorm.nodes.BlockStmt):
                    for item in v.body:
                        self.add_self_param(item)
                        dec_i = Mangler.instance().muckFangle(item, class_name)
                        item._name = dec_i
                        self.virtuals[dec_i] = item
                else:
                    self.add_self_param(v)
                    dec_v = Mangler.instance().muckFangle(v, class_name)
                    v._name = dec_v
                    self.virtuals[dec_v] = v

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
        #self.add_inheritance() A supprimer


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


    def register_typedef_vt(self):
        #for vr in self.virtuals:
        #    item = self.virtuals[vr]
        #    self.protos.append(item)
        
        if 'parent' in self.members:
            decl = cnorm.nodes.Decl('vt_%s' % self.ident, cnorm.nodes.ComposedType('_kc_vt_%s' % self.ident))
            decl._ctype._specifier = 1
            decl._ctype._storage = cnorm.nodes.Storages.TYPEDEF
            if not hasattr(decl._ctype, 'fields'):
                setattr(decl._ctype, 'fields', [])

            mom = DeclKeeper.instance().inher[self.ident]
            if DeclKeeper.instance().classes[mom].vt != None: #Check inutile a l'avenir
                #decl_mom = cnorm.nodes.Decl('parent', cnorm.nodes.PrimaryType('vt_%s' % mom))
                decl_mom = DeclKeeper.instance().classes[mom].vt
                decl._ctype.fields.extend(decl_mom)
            
            # Ajouter check si pas deja ds vt_mom
            for vr in self.virtuals:
                item = self.virtuals[vr]
                # nom : changer ac appel a mingleSangle

                ct_fct = cnorm.nodes.PrimaryType(item._ctype._identifier)
                ct_fct._storage = 0
                ct_fct._specifier = 0
                ct_fct._decltype = cnorm.nodes.PointerType()
                setattr(ct_fct._decltype, '_decltype', cnorm.nodes.ParenType(item._ctype._params))
                setattr(ct_fct._decltype, '_identifier', item._ctype._identifier)

                # vr: trouver convention de nommage pour vtable
                fct_ptr = cnorm.nodes.Decl(vr, ct_fct)
                decl._ctype.fields.append(fct_ptr)

            self.vt = decl
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
        if not self.ident in DeclKeeper.instance().inher:
            return
        mom = DeclKeeper.instance().inher[self.ident]
        obj = DeclKeeper.instance().classes[mom]

        for mem_id in obj.members:
            mem = obj.members[mem_id]
            if not isinstance(mem._ctype, cnorm.nodes.FuncType):
                continue
            ident = Mangler.instance().changeClass(mem_id, self.ident, mom)
            tmp = deepcopy(mem)
            tmp._name = ident
            tmp._ctype._params[0]._ctype._identifier = self.ident
            self.members[ident] = tmp

        for decl_id in obj.decls:
            decl = obj.decls[decl_id]
            if not isinstance(decl._ctype, cnorm.nodes.FuncType):
                continue
            ident = Mangler.instance().changeClass(decl_id, self.ident, mom)
            tmp = deepcopy(decl)
            tmp._name = ident
            tmp._ctype._params[0]._ctype._identifier = self.ident
            self.decls[ident] = tmp

        for vir_id in obj.virtuals:
            vir = obj.virtuals[vir_id]
            if not isinstance(vir._ctype, cnorm.nodes.FuncType):
                continue
            ident = Mangler.instance().changeClass(vir_id, self.ident, mom)
            tmp = deepcopy(vir)
            tmp._name = ident
            tmp._ctype._params[0]._ctype._identifier = self.ident
            self.virtuals[ident] = tmp


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
