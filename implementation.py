import cnorm
import mangler
import decl_keeper
from copy import deepcopy
from cnorm.parsing.declaration import Declaration

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident
        self.alloc_fct = None
        self.imps = []
        self.virtuals = []

        self.add_vars_decls()
        if self.ident in decl_keeper.classes:
            self.create_alloc_fct()
            self.create_delete_fct()
            
        for i in imp.body:
            if isinstance(i, cnorm.nodes.BlockStmt):
                for elem in i.body:
                    self.register_implementation(elem)
            else:
                self.register_implementation(i)


    def register_implementation(self, imp):
        ret = self.check_param(imp)
        if ret != None:
            self.imps.append(ret)
            if '$init$' in ret._name:
                self.create_new_fct(ret)
        else:
            imp._name = mangler.muckFangle(imp, self.ident)
            self.imps.append(imp)


    def add_vars_decls(self):
        if self.ident in decl_keeper.modules:
            self.imps.extend(decl_keeper.modules[self.ident].decls_vars)
        elif self.ident in decl_keeper.classes:
            obj = decl_keeper.classes[self.ident]
            self.imps.extend(obj.decls_vars)
            self.imps.append(obj.inst_vt)
        else:
            raise BaseException('Unknown module or class : %s' % self.ident)


    def create_alloc_fct(self):
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_%s %s;
        %s *alloc()
        {
        %s *self;
        self = malloc(sizeof(%s));
        return (self);
        }
        """ % (self.ident, self.ident, self.ident, self.ident, self.ident))
        
        for decl in res.body:
            if isinstance(decl._ctype, cnorm.nodes.FuncType):
                decl._name = mangler.muckFangle(decl, self.ident)
                self.alloc_fct = decl
                self.imps.append(decl)


    # Créé une fct pour free les champs de l'object
    def create_delete_fct(self):
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_Object Object;
        typedef struct _kc_%s %s;
        void delete(%s *self)
        {
        free((Object*)(self)->name);
        clean(this);
        }
        """ % (self.ident, self.ident, self.ident))

        for decl in res.body:
            if isinstance(decl._ctype, cnorm.nodes.FuncType):
                decl._name = mangler.muckFangle(decl, self.ident)
                for dcl in decl.body.body:
                    if hasattr(dcl.expr, 'call_expr') and dcl.expr.call_expr.value == 'clean':
                        name = decl_keeper.classes[self.ident].members[0]._name
                        dcl.expr.call_expr.value = name
                self.imps.append(decl)


    # Créé une fct new pour chaque init rencontré
    def create_new_fct(self, ini):
        params = []
        if len(ini._ctype._params) >= 1:
            params = ini._ctype._params[1:]
        
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_Object Object;
        typedef struct _kc_%s %s;
        %s *new(%s)
        {
        %s* self;
        self = alloc();
        init(self, %s);
        (Object*)(self)->name = "%s";
        return (self);
        }
        """ % (self.ident, self.ident, self.ident,
               ', '.join([str(c.to_c()).rstrip() for c in params]).replace(';', ''),
               self.ident,
               ', '.join([c._name for c in params]),
               self.ident))

        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'new':
                decl._name = mangler.muckFangle(decl, self.ident)
                for dcl in decl.body.body:
                    if isinstance(dcl, cnorm.nodes.ExprStmt):
                        if isinstance(dcl.expr, cnorm.nodes.Binary) and \
                           isinstance(dcl.expr.params[0], cnorm.nodes.Cast):
                            pass
                        elif isinstance(dcl.expr, cnorm.nodes.Binary):
                            dcl.expr.params[1].call_expr.value = self.alloc_fct._name
                        elif isinstance(dcl.expr, cnorm.nodes.Func):
                            dcl.expr.call_expr.value = ini._name
                self.imps.append(decl)
                

    # Ajoute le parametre self aux parametres de la fct membre
    def check_param(self, decl):
        if isinstance(decl._ctype, cnorm.nodes.FuncType):
            if not self.ident in decl_keeper.classes:
                return None
            cl = decl_keeper.classes[self.ident]
            param = cnorm.nodes.Decl('self', cnorm.nodes.PrimaryType(self.ident))
            param._ctype._decltype = cnorm.nodes.PointerType()

            if decl._ctype._params != [] and decl._ctype._params[0]._ctype._identifier == self.ident:
                return None
            
            dc = deepcopy(decl)
            dc._ctype._params.insert(0, param)
            sm_name = mangler.mimpleSangle(dc)
            dc._name = mangler.muckFangle(dc, self.ident)
            for dcl in cl.members:
                if dcl._name == dc._name:
                    return dc
            if sm_name in cl.virtuals:
                return dc
            return None
