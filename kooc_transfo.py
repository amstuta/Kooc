from kooc_class import *
from kooc_typer import *
from cnorm.nodes import *
from pyrser import parsing, meta

def doKoocTransfoList(l):
    output = []
    for item in l:
        output.append(item.doKoocTransfo())
    return [ x for x in output if x is not None ]

@meta.add_method(KoocCall)
def doKoocTransfo(node):
    type_name = node.call_expr.expr_type.name
    if type_name in decl_keeper.modules:
        module = decl_keeper.modules[type_name]
        if node.call:
            params = []
            for p in node.params:
                pp = p.doKoocTransfo()
                if pp is not None:
                    params.append(pp)
            decls = module.funcs(node.member)
            for decl in decls:
                if decl._ctype.expr_type == node.func_type:
                    call_expr = Id(decl._name)
                    n = Func(call_expr, params)
                    return n
        else:
            decls = module.variables(node.member)
            for decl in decls:
                if decl._ctype.expr_type == node.expr_type:
                    n = Id(decl._name)
                    return n
    else:
        call_type = node.call_expr.expr_type
        if isinstance(node.call_expr.expr_type, Pointer):
            module = decl_keeper.classes[node.call_expr.expr_type.expr_type.name]
        else:
            module = decl_keeper.classes[call_type.name]
        if not call_type.is_instance:
            if node.call:
                params = []
                for p in node.params:
                    pp = p.doKoocTransfo()
                    if pp is not None:
                        params.append(pp)
                decls = module.funcs(node.member)
                for decl in decls:
                    if decl._ctype.expr_type == node.func_type:
                        call_expr = Id(decl._name)
                        n = Func(call_expr, params)
                        return n
            else:
                decls = module.variables(node.member)
                for decl in decls:
                    if decl._ctype.expr_type == node.expr_type:
                        n = Id(decl._name)
                        return n
        else:
            if node.call:
                params = [ node.call_expr.doKoocTransfo() ]
                for p in node.params:
                    pp = p.doKoocTransfo()
                    if pp is not None:
                        params.append(pp)
                decls = module.virtual_funcs(node.member)
                for decl in decls:
                    if decl._ctype.expr_type == node.func_type:
                        objptr_ctype = PrimaryType("Object")
                        objptr_ctype.push(PointerType())
                        me_ctype = PrimaryType(module.vt._ctype._identifier)
                        me_ctype.push(PointerType())
                        obj_expr = Cast(Raw("()"), [ objptr_ctype, Paren(Raw("()"), [ node.call_expr ]) ])
                        vt_expr = Paren(Raw("()"), [ Arrow(obj_expr, [ Id("vt") ]) ])
                        myvt_expr = Cast(Raw("()"), [ me_ctype, vt_expr ])
                        vt_field = Arrow(Paren(Raw("()"), [ myvt_expr ]), [ Id(decl._name) ])
                        n = Func(
                                Paren(Raw("()"),
                                    [ Unary(Raw("*"), [ Paren(Raw("()"), [
                                        vt_field ]) ]) ]), params)
                        return n
                decls = module.member_funcs(node.member)
                for decl in decls:
                    if decl._ctype.expr_type == node.func_type:
                        call_expr = Id(decl._name)
                        n = Func(call_expr, params)
                        return n
            else:
                decls = module.member_vars(node.member)
                for decl in decls:
                    if decl._ctype.expr_type == node.expr_type:
                        call_expr = Paren("()", [node.call_expr.doKoocTransfo()])
                        n = Arrow(call_expr, [Id(decl._name)])
                        return n
    raise Exception("KoocCall: type resolu mais pas de declaration")

@meta.add_method(parsing.Node)
def doKoocTransfo(node):
    if hasattr(node, "body"):
        node.body.doKoocTransfo()
    if hasattr(node, "thencond"):
        node.thencond.doKoocTransfo()
    if hasattr(node, "elsecond"):
        node.elsecond.doKoocTransfo()
    if hasattr(node, "condition"):
        node.condition = node.condition.doKoocTransfo()
    if hasattr(node, "expr"):
        node.expr = node.expr.doKoocTransfo()
    if hasattr(node, "params"):
        node.params = doKoocTransfoList(node.params)
    return node

@meta.add_method(BlockStmt)
def doKoocTransfo(self):
    self.body = doKoocTransfoList(self.body)
    return self.body

@meta.add_method(RootBlockStmt)
def doKoocTransfo(self):
    self.body = doKoocTransfoList(self.body)
    return self.body

@meta.add_method(Decl)
def doKoocTransfo(self):
    if hasattr(self, "_assign_expr"):
        self._assign_expr = self._assign_expr.doKoocTransfo()
    if hasattr(self, "body"):
        self.body.doKoocTransfo()
    return self
