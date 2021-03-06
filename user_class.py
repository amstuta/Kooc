import cnorm
import mangler
from copy import deepcopy
import decl_keeper
from cnorm.parsing.declaration import Declaration
from cnorm.nodes import *

class Class:

    def __init__(self, class_name, statement, recurs):
        self.ident = class_name
        self.recurs = recurs
        self.protos = []
        self.vt = None
        self.inst_vt = None
        self.non_mangled = []

        # Ajoute aux membres les fcts qui recoivent une instance de l'objet en first param
        self.check_first_param(statement)

        # Mangling et save des membres
        self.members = []
        self.add_legacy_fcts()
        if hasattr(statement, 'members'):
            for m in statement.members:
                if isinstance(m, cnorm.nodes.BlockStmt):
                    for i in m.body:
                        if (i._name == 'init'):
                            self.add_new_proto(i)
                        self.add_self_param(i)
                        self.non_mangled.append(deepcopy(i))
                        i.saved_name = i._name
                        i._name = mangler.muckFangle(i, class_name)
                        self.members.append(i)
                else:
                    if (m._name == 'init'):
                        self.add_new_proto(m)
                    self.add_self_param(m)
                    self.non_mangled.append(deepcopy(m))
                    m.saved_name = m._name
                    m._name = mangler.muckFangle(m, class_name)
                    self.members.append(m)

        # Save des virtuals
        self.virtuals = {}
        if hasattr(statement, 'virtuals'):
            for v in statement.virtuals:
                if isinstance(v, cnorm.nodes.BlockStmt):
                    for item in v.body:
                        self.add_self_param(item)
                        item.saved_name = item._name
                        self.virtuals[item._name] = item
                else:
                    self.add_self_param(v)
                    v.saved_name = v._name
                    self.virtuals[v._name] = v

        # Mangling et save des non membres
        self.decls = []
        self.decls_vars = []
        for d in statement.body:
            if isinstance(d, cnorm.nodes.BlockStmt):
                for i in d.body:
                    i.saved_name = i._name
                    i._name = mangler.muckFangle(i, class_name)
                    if not isinstance(i._ctype, cnorm.nodes.FuncType):
                        self.decls_vars.append(i)
                        tmp = deepcopy(i)
                        tmp._ctype._storage = 4
                        self.decls.append(tmp)
                    else:
                        self.decls.append(i)
            else:
                d.saved_name = d._name
                d._name = mangler.muckFangle(d, class_name)
                if not isinstance(d._ctype, cnorm.nodes.FuncType):
                    self.decls_vars.append(d)
                    tmp = deepcopy(d)
                    tmp._ctype._storage = 4
                    self.decls.append(tmp)
                else:
                    self.decls.append(d)

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
        if self.has_parent():
            parent = deepcopy(self.members[0])
            del self.members[0]
            decl._ctype.fields.append(parent)
        else:
            decl_type = cnorm.nodes.PrimaryType('Object')
            decl_obj = cnorm.nodes.Decl('parent', decl_type)
            decl._ctype.fields.append(decl_obj)

        for mem in self.members:
            if not isinstance(mem._ctype, cnorm.nodes.FuncType):
                cpy = deepcopy(mem)
                decl._ctype.fields.append(cpy)
            else:
                self.protos.append(mem)
        
        if parent != None:
            self.members.insert(0, parent)
        return decl


    # Ecrit le struct de la vtable
    def register_struct_vt(self):
        if self.has_parent():
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
            setattr(struct, 'fields', deepcopy(tpd_object._ctype.fields))
            decl = cnorm.nodes.Decl('', struct)
            self.add_self_virtuals(decl)
            self.vt = decl
            return decl
        

    def register_non_members(self):
        non_mbrs = []
        for item in self.decls:
            item = deepcopy(item)
            if isinstance(item._ctype, cnorm.nodes.FuncType):
                self.protos.append(item)
                continue
            non_mbrs.append(item)
        return non_mbrs


    def add_alloc_proto(self):
        ctype = cnorm.nodes.FuncType(self.ident, [], cnorm.nodes.PointerType())
        decl = cnorm.nodes.Decl('alloc', ctype)
        dec_n = mangler.muckFangle(decl, self.ident)
        decl._name = dec_n
        setattr(decl, 'saved_name', 'alloc')
        self.protos.append(decl)


    def add_new_proto(self, decl):
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_%s %s;
        %s *new(%s);
        """ % (self.ident, self.ident, self.ident,
               ', '.join([str(c.to_c()).rstrip() for c in decl._ctype.params]).replace(';', '')))
        dcl = res.body[1]
        dcl._name = mangler.muckFangle(dcl, self.ident)
        setattr(decl, 'saved_name', 'new')
        self.protos.append(dcl)


    def add_legacy_fcts(self):
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_%s %s;
        void delete(%s*);
        """ % (self.ident, self.ident, self.ident))
        decl = res.body[1]
        decl._name = mangler.muckFangle(decl, self.ident)
        setattr(decl, 'saved_name', 'delete')
        self.members.append(decl)

        
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
        blockInit = deepcopy(m_inst_vt._assign_expr)

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
        self.add_virtual_members()
        self.mangle_virtuals()
        
        ext = deepcopy(self.inst_vt)
        delattr(ext, '_assign_expr')
        ext._ctype._storage = cnorm.nodes.Storages.EXTERN
        
        return ext


    # Change le lien vers la fct virtuelle
    # qd le mot-clé n'a pas été mis
    def add_virtual_members(self):
        for decl in self.non_mangled:
            vir_name = mangler.mimpleSangle(decl)
            for idx, dcl in enumerate(self.vt._ctype.fields):
                if dcl._name == vir_name:
                    m_name = mangler.muckFangle(decl, self.ident)
                    self.inst_vt._assign_expr.body[idx].params[0].value = m_name
                    


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
        decl.saved_name = decl._name
        self.members.insert(0, decl)


    def has_parent(self):
        if self.members != [] and self.members[0]._name == 'parent':
            return True
        return False

    def funcs(self, name):
        out = []
        for decl in self.decls:
            if decl.saved_name == name and isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out

    def variables(self, name):
        out = []
        for decl in self.decls:
            if decl.saved_name == name and not isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out

    def member_vars(self, name):
        out = []
        for decl in self.members:
            if decl.saved_name == name and not isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out

    def member_funcs(self, name):
        out = []
        for decl in self.members:
            if decl.saved_name == name and isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out

    def virtual_funcs(self, name):
        out = []
        for decl_name in self.virtuals:
            decl = self.virtuals[decl_name]
            if decl.saved_name == name and isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out
