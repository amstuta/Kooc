from pyrser import meta, parsing
from cnorm.nodes import *

class Type():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        items = []
        for k, v in vars(self).items():
            items.append("{} = {}".format(k, repr(v)))
        return "{}({})".format(self.__class__.__name__, ", ".join(items))

class Pointer(Type):
    def __init__(self, name, expr_type):
        Type.__init__(self, name)
        self.expr_type = expr_type

class Function(Type):
    def __init__(self, name, return_type):
        Type.__init__(self, name)
        self.params = []
        self.return_type = return_type

    def push_param(self, param_type):
        self.params.append(param_type)


### Useful types

int_type = Type("int")
char_type = Type("char")
str_type = Pointer("%P", char_type)

###


### CType resolver

@meta.add_method(PrimaryType)
def resolve_type(self, scope):
    t = Type(self._identifier)
    declt = self._decltype
    while not declt is None:
        if isinstance(declt, PointerType) or isinstance(declt, ArrayType):
            t = Pointer("%P", t)
        declt = declt._decltype
    return t

@meta.add_method(FuncType)
def resolve_type(self, scope):
    return_type = PrimaryType.resolve_type(self, scope)
    t = Function("%F", return_type)
    for param in self._params:
        param_t = param.resolve_type(scope)
        t.push_param(param_t)
    return t

### End CType resolver

### Stmt resolver

class DefScope():
    def __init__(self, parent = None):
        self.parent = parent
        self.defs = {}

@meta.add_method(parsing.Node)
def resolve_type(self, scope = None):
    if scope is None:
        scope = DefScope()
    if hasattr(self, "body"):
        new_scope = DefScope(scope)
        for node in self.body:
            node.resolve_type(new_scope)
    if hasattr(self, "expr"):
        self.expr.resolve_type(scope)
    if hasattr(self, "condition"):
        new_scope = DefScope(scope)
        self.condition.resolve_type(new_scope)
    if hasattr(self, "thencond"):
        new_scope = DefScope(scope)
        self.thencond.resolve_type(new_cope)
    if hasattr(self, "elsecond"):
        new_scope = DefScope(scope)
        self.elsecond.resolve_type(new_scope)

# End Stmt resolver

# Expr resolver

@meta.add_method(Decl)
def resolve_type(self, scope):
    self.expr_type = self._ctype.resolve_type(scope)
    if self._name in scope.defs:
        raise Exception("redéfinition d'un symbole dans le même scope") #TODO(lakh): throw
    scope.defs[self._name] = self.expr_type
    if hasattr(self, "_assign_expr"):
        self._assign_expr.resolve_type(scope)
    new_scope = DefScope(scope)
    if hasattr(self, "body"):
        self.body.resolve_type(scope)
    return self.expr_type



@meta.add_method(Func)
def resolve_type(self, scope):
    t = self.call_expr.resolve_type(scope)
    if not isinstance(t, Function):
        raise Exception("call_expr de Func n'est pas une fonction") #TODO(lakh): throw
    self.expr_type = t.return_type
    return self.expr_type


@meta.add_method(Unary)
def resolve_type(self, scope):
    self.expr_type = self.params[0].resolve_type(scope)
    if isinstance(self.call_expr, Raw):
        if self.call_expr.value == "*":
            if not isinstance(self.expr_type, Pointer):
                from cnorm.passes import to_c
                raise Exception("On déréférence une expression de type non-pointeur : `{}`".format(self.params[0].to_c())) #TODO(lakh): throw
            self.expr_type = self.expr_type.expr_type
        elif self.call_expr.value == "&":
            self.expr_type = Pointer("%P", self.expr_type)
    return self.expr_type

@meta.add_method(Array)
def resolve_type(self, scope):
    self.expr_type = self.call_expr.resolve_type(scope)
    if not isinstance(self.expr_type, Pointer): # Array est gere comme un pointeur pour la simplicite
        from cnorm.passes import to_c
        raise Exception("On déréférence une expression de type non-pointeur : `{}`".format(self.params[0].to_c())) #TODO(lakh): throw
    self.expr_type = self.expr_type.expr_type 

@meta.add_method(Id)
def resolve_type(self, scope):
    while not scope is None:
        if self.value in scope.defs:
            self.expr_type = scope.defs[self.value]
            return self.expr_type
        scope = scope.parent
    raise Exception("symbole `{}` non défini".format(self.value)) #TODO(lakh): throw

@meta.add_method(Literal)
def resolve_type(self, scope):
    if self.value[0] == '"':
        self.expr_type = str_type
    else:
        self.expr_type = int_type
    return self.expr_type

# End Expr resolver
