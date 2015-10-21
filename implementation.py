import cnorm
from mangler import *
from decl_keeper import *
from copy import deepcopy

class Implementation:

    def __init__(self, ident, imp):
        self.ident = ident
        self.alloc_fct = None

        self.imps = {}
        self.virtuals = []
        if self.ident in DeclKeeper.instance().classes:
            self.create_alloc_fct()
            
        for i in imp.body:
            if isinstance(i, cnorm.nodes.BlockStmt):
                for elem in i.body:
                    self.register_implementation(elem)
            else:
                self.register_implementation(i)



    def register_implementation(self, imp):
        ret = self.check_param(imp)
        if ret != None:
            self.imps[ret._name] = ret
            if '$init$' in ret._name:
                self.create_new_fct(ret)
        else:
            dec_imp = Mangler.instance().muckFangle(imp, self.ident)
            imp._name = dec_imp
            self.imps[dec_imp] = imp


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
                decl._name = Mangler.instance().muckFangle(decl, self.ident)
                self.alloc_fct = decl
                self.imps[decl._name] = decl

        """
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
        """


    # Créé une fct new pour chaque init rencontré
    def create_new_fct(self, ini):
        params = []
        if len(ini._ctype._params) >= 1:
            params = ini._ctype._params[1:]
        
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_%s %s;
        %s *new(%s)
        {
        %s* self;
        self = alloc();
        init(self, c);
        return (self);
        }
        """ % (self.ident, self.ident, self.ident,
               ', '.join([str(c.to_c()).rstrip() for c in params]).replace(';', ''),
               self.ident))

        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'new':
                decl._name = Mangler.instance().muckFangle(decl, self.ident)
                for dcl in decl.body.body:
                    if isinstance(dcl, cnorm.nodes.ExprStmt):
                        if isinstance(dcl.expr, cnorm.nodes.Binary):
                            dcl.expr.params[1].call_expr.value = self.alloc_fct._name
                        elif isinstance(dcl.expr, cnorm.nodes.Func):
                            dcl.expr.call_expr.value = ini._name
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
            sm_name = Mangler.instance().mimpleSangle(dc)
            dc._name = Mangler.instance().muckFangle(dc, self.ident)
            if dc._name in cl.members or sm_name in cl.virtuals:
                return dc
            return None
