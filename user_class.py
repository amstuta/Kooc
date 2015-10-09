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
        self.inst_vt = None

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
                        dec_i = Mangler.instance().mimpleSangle(item)
                        item._name = dec_i
                        self.virtuals[dec_i] = item
                else:
                    self.add_self_param(v)
                    dec_v = Mangler.instance().mimpleSangle(v)
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


    # Ecrit les typedefs de struct et struct vt
    def register_typedefs(self):
        tpd_struct = cnorm.nodes.Decl(self.ident, cnorm.nodes.ComposedType('_kc_%s' % self.ident))
        tpd_struct._ctype._storage = cnorm.nodes.Storages.TYPEDEF
        tpd_struct._ctype._specifier = 1
        
        tpd_vt = cnorm.nodes.Decl('vt_%s' % self.ident, cnorm.nodes.ComposedType('_kc_vt_%s' % self.ident))
        tpd_vt._ctype._storage = cnorm.nodes.Storages.TYPEDEF
        tpd_vt._ctype._specifier = 1

        return [tpd_struct, tpd_vt]
        

    # Ecrit la struct de la classe
    def register_struct(self):
        decl = cnorm.nodes.Decl('', cnorm.nodes.ComposedType('_kc_' + self.ident))
        decl._ctype._specifier = 1
        if not hasattr(decl._ctype, 'fields'):
            setattr(decl._ctype, 'fields', [])

        # Obj parent
        parent = None
        if 'parent' in self.members:
            parent = deepcopy(self.members['parent'])
            del self.members['parent']
            decl._ctype.fields.append(parent)
        else:
            decl_type = cnorm.nodes.PrimaryType('Object')
            decl_obj = cnorm.nodes.Decl('parent', decl_type)
            decl._ctype.fields.append(decl_obj)

        for mem in self.members:
            if type(self.members[mem]._ctype) != cnorm.nodes.FuncType:
                cpy = deepcopy(self.members[mem])
                delattr(cpy, '_assign_expr')
                decl._ctype.fields.append(cpy)
            else:
                self.protos.append(self.members[mem])
        for d in self.decls:
            item = deepcopy(self.decls[d])
            if type(item._ctype) == cnorm.nodes.FuncType:
                self.protos.append(item)
                continue
            delattr(item, '_assign_expr')
            item._ctype._storage = cnorm.nodes.Storages.STATIC
            decl._ctype.fields.append(item)
        if parent != None:
            self.members['parent'] = parent
        return decl


    # Ecrit le struct de la vtable
    def register_struct_vt(self):
        if 'parent' in self.members:
            decl = cnorm.nodes.Decl('', cnorm.nodes.ComposedType('_kc_vt_%s' % self.ident))
            decl._ctype._specifier = 1
            if not hasattr(decl._ctype, 'fields'):
                setattr(decl._ctype, 'fields', [])

            # Add champs virtuals de la classe mere
            mom = DeclKeeper.instance().inher[self.ident]
            if DeclKeeper.instance().classes[mom].vt != None:
                decl_mom = DeclKeeper.instance().classes[mom].vt
                decl._ctype.fields.extend(decl_mom._ctype.fields)
            self.add_self_virtuals(decl)
            self.vt = decl
            return decl

        else:
            # Add champs virtuels de Object
            tpd_object = DeclKeeper.instance().typedef_vt_object
            struct = cnorm.nodes.ComposedType('_kc_vt_%s' % self.ident)
            struct._specifier = 1
            setattr(struct, 'fields', tpd_object._ctype.fields)
            decl = cnorm.nodes.Decl('', struct)
            self.add_self_virtuals(decl)
            self.vt = decl
            return decl


    def add_self_virtuals(self, decl):
        for vr in self.virtuals:
            # Check si virtual deja ds vtable
            if self.virtual_exists(decl._ctype.fields, vr):
                continue
            item = self.virtuals[vr]
            ct_fct = cnorm.nodes.PrimaryType(item._ctype._identifier)
            ct_fct._storage = 0
            ct_fct._specifier = 0
            ct_fct._decltype = cnorm.nodes.PointerType()
            setattr(ct_fct._decltype, '_decltype', cnorm.nodes.ParenType(item._ctype._params))
            setattr(ct_fct._decltype, '_identifier', item._ctype._identifier)
            fct_ptr = cnorm.nodes.Decl(vr, ct_fct)
            decl._ctype.fields.append(fct_ptr)


    def virtual_exists(self, vlist, vname):
        for v in vlist:
            if v._name == vname:
                return True
        return False


    # Instancie la vtable
    def instanciate_vt(self):
        m_inst_vt = None
        if self.ident in DeclKeeper.instance().inher:
            mom_name = DeclKeeper.instance().inher[self.ident]
            m_inst_vt = DeclKeeper.instance().classes[mom_name].inst_vt
        else:
            m_inst_vt = DeclKeeper.instance().obj_vtable
        blockInit = deepcopy(DeclKeeper.instance().obj_vtable._assign_expr)
        decl = cnorm.nodes.Decl('vtable_%s' % self.ident, cnorm.nodes.PrimaryType('vt_%s' % self.ident))
        setattr(decl, '_assign_expr', blockInit)
        self.inst_vt = decl
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
