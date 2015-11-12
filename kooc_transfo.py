from kooc_class import *
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
        decls = module.funcs(node.member)
        for decl in decls:
            if decl._ctype.expr_type == node.func_type:
                call_expr = Id(decl._name)
                n = Func(call_expr, node.params)
                return n
    else:
        decls = module.variables(node.member)
        for decl in decls:
            if decl._ctype.expr_type == node.expr_type:
                n = Id(decl._name)
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
