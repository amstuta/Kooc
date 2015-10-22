import cnorm
import mangler
from copy import deepcopy
import decl_keeper

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
                        dec_i = mangler.muckFangle(i, class_name)
                        i._name = dec_i
                        self.members[dec_i] = i
                else:
                    self.add_self_param(m)
                    dec_m = mangler.muckFangle(m, class_name)
                    m._name = dec_m
                    self.members[dec_m] = m

        # Save des virtuals
        self.virtuals = {}
        if hasattr(statement, 'virtuals'):
            for v in statement.virtuals:
                if isinstance(v, cnorm.nodes.BlockStmt):
                    for item in v.body:
                        self.add_self_param(item)
                        self.virtuals[item._name] = item
                else:
                    self.add_self_param(v)
                    self.virtuals[v._name] = v

        # Mangling et save des non membres
        self.decls = {}
        for d in statement.body:
            if isinstance(d, cnorm.nodes.BlockStmt):
                for i in d.body:
                    dec_i = mangler.muckFangle(i, class_name)
                    i._name = dec_i
                    self.decls[dec_i] = i
            else:
                dec_d = mangler.muckFangle(d, class_name)
                d._name = dec_d
                self.decls[dec_d] = d

        self.add_alloc_proto()
        self.get_inheritance()


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
            mom = decl_keeper.inher[self.ident]
            if decl_keeper.classes[mom].vt != None:
                decl_mom = decl_keeper.classes[mom].vt
                decl._ctype.fields.extend(decl_mom._ctype.fields)
            self.add_self_virtuals(decl)
            self.vt = decl
            return decl

        else:
            # Add champs virtuels de Object
            tpd_object = decl_keeper.typedef_vt_object
            struct = cnorm.nodes.ComposedType('_kc_vt_%s' % self.ident)
            struct._specifier = 1
            setattr(struct, 'fields', tpd_object._ctype.fields)
            decl = cnorm.nodes.Decl('', struct)
            self.add_self_virtuals(decl)
            self.vt = decl
            return decl


    def register_non_members(self):
        non_mbrs = []
        for d in self.decls:
            item = deepcopy(self.decls[d])
            if type(item._ctype) == cnorm.nodes.FuncType:
                self.protos.append(item)
                continue
            non_mbrs.append(item)
        return non_mbrs


    def add_alloc_proto(self):
        ctype = cnorm.nodes.FuncType(self.ident, [], cnorm.nodes.PointerType())
        decl = cnorm.nodes.Decl('alloc', ctype)
        dec_n = mangler.muckFangle(decl, self.ident)
        decl._name = dec_n
        self.protos.append(decl)


    def add_self_virtuals(self, decl):
        for vr in self.virtuals:
            vr_name = mangler.mimpleSangle(self.virtuals[vr])
            if self.virtual_exists(decl._ctype.fields, vr_name):
                continue
            item = self.virtuals[vr]
            ct_fct = cnorm.nodes.PrimaryType(item._ctype._identifier)
            ct_fct._storage = 0
            ct_fct._specifier = 0
            ct_fct._decltype = cnorm.nodes.PointerType()
            setattr(ct_fct._decltype, '_decltype', cnorm.nodes.ParenType(item._ctype._params))
            setattr(ct_fct._decltype, '_identifier', item._ctype._identifier)
            fct_ptr = cnorm.nodes.Decl(vr_name, ct_fct)
            decl._ctype.fields.append(fct_ptr)


    def virtual_exists(self, vlist, vname):
        for v in vlist:
            if v._name == vname:
                return True
        return False


    # Instancie la vtable
    def instanciate_vt(self):
        m_inst_vt = None
        if self.ident in decl_keeper.inher:
            mom_name = decl_keeper.inher[self.ident]
            m_inst_vt = decl_keeper.classes[mom_name].inst_vt
        else:
            m_inst_vt = decl_keeper.obj_vtable
        blockInit = deepcopy(decl_keeper.obj_vtable._assign_expr)

        ## + voir si on peut redeclarer une fct virtual sans le mot cle
        # Réassignation des pointeurs
        size_b = len(blockInit.body)
        size_v = len(self.vt._ctype.fields)
        if size_v > size_b:
            diff = size_v - size_b
            for i in range(0, diff):
                blockInit.body.append(None)
        for vir_name in self.virtuals:
            idx = None
            tmp_name = mangler.mimpleSangle(self.virtuals[vir_name])
            for index, tp in enumerate(self.vt._ctype.fields):
                if tp._name == tmp_name:
                    idx = index
            if idx == None: continue
            fct = self.virtuals[vir_name]
            m_name = mangler.muckFangle(fct, self.ident)
            blockInit.body[idx] = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id(m_name)])

        decl = cnorm.nodes.Decl('vtable_%s' % self.ident, cnorm.nodes.PrimaryType('vt_%s' % self.ident))
        setattr(decl, '_assign_expr', blockInit)
        self.inst_vt = decl
        self.mangle_virtuals()
        return decl


    # Mangle les nom des prototypes de virtuals
    # et les ajoute à la liste de protos
    def mangle_virtuals(self):
        new_dict = {}
        for vir in self.virtuals:
            m_name = mangler.muckFangle(self.virtuals[vir], self.ident)
            v_name = mangler.mimpleSangle(self.virtuals[vir])
            v_obj = deepcopy(self.virtuals[vir])
            v_obj._name = v_name
            new_dict[v_name] = v_obj
            proto = deepcopy(v_obj)
            proto._name = m_name
            self.protos.append(proto)
        self.virtuals = new_dict


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
        if not self.ident in decl_keeper.inher:
            return
        mom = decl_keeper.inher[self.ident]
        decl = cnorm.nodes.Decl('parent', cnorm.nodes.PrimaryType(mom))
        self.members['parent'] = decl
