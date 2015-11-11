from pyrser import meta, parsing
from cnorm.nodes import *
from kooc_class import *
from module import Module
from user_class import Class

class Type():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        items = []
        for k, v in vars(self).items():
            items.append("{} = {}".format(k, repr(v)))
        return "{}({})".format(self.__class__.__name__, ", ".join(items))

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self == other.v_type
        if not isinstance(other, Type):
            return False
        return self.name == other.name

### Useful types

int_type = Type("int")
char_type = Type("char")
void_type = Type("void")

###

class Pointer(Type):

    def __init__(self, expr_type):
        Type.__init__(self, "%P")
        self.expr_type = expr_type

    def __eq__(self, other):
        if not isinstance(other, Pointer):
            return False
        if self.expr_type == void_type or other.expr_type == void_type:
            return True
        return self.expr_type == other.expr_type

### Useful types

voidptr_type = Pointer(void_type)
str_type = Pointer(char_type)

###

class Function(Type):
    def __init__(self, return_type, params = None):
        Type.__init__(self, "%F")
        if params is None:
            params = []
        self.params = params
        self.return_type = return_type

    def push_param(self, param_type):
        self.params.append(param_type)

    def param(self, i):
        if i >= len(self.params):
           return None
        return self.params[i]

    def cmp_params(self, other_func):
        if len(other_func.params) != len(self.params):
            return False
        for (i, p) in enumerate(self.params):
            if p != other_func.param(i):
                return False
        return True

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self == other.v_type
        #TODO(lakh): Gérer la comparaison fct* et fct ??
        if not isinstance(other, Function):
            return False
        if not self.return_type == other.return_type:
            return False
        if len(self.params) != len(other.params):
            return False
        for (idx, param) in enumerate(self.params):
            if not param == other.params[idx]:
                return False
        return True


class Variable(Type):
    def __init__(self, name, v_type):
        Type.__init__(self, "%V")
        self.name = name
        self.v_type = v_type

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.v_type == other.v_type
        return self.v_type == other

class Struct(Type):
    def __init__(self, name, fields = None):
        self.name = name
        if fields is None:
            fields = []
        self.fields = fields

    def add_field(self, field):
        self.fields.append(field)

    def funcs(self, name):
        o = []
        for f in self.fields:
            if isinstance(f, Variable) and f.name == name and isinstance(f.v_type, Function):
                o.append(f.v_type)
        return o

    def __eq__(self, other):
        if isinstance(other, Variable):
            return self == other.v_type
        if not isinstance(other, Struct):
            return False
        if len(self.fields) != len(other.fields):
            return False
        for (idx, field) in enumerate(self.fields):
            if not field == other.fields[idx]:
                return False
        return True

class TypesSet():
    def __init__(self, types = None):
        if types is None:
            types = []
        self.types = types

    def __eq__(self, other):
        if not isinstance(other, TypesSet):
            return False
        if len(self.types) != len(other.types):
            return False
        for t in self.types:
            if not t in other.types:
                return False
        return True

    def push(self, obj):
        if isinstance(obj, TypesSet):
            for t in obj.types:
                self.push(t)
        else:
            for t in self.types:
                if t == obj:
                    return None
            self.types.append(obj)

    def intersect(self, obj):
        if isinstance(obj, Type):
            return self.intersect_type(obj)
        return self.intersect_set(obj)

    def intersect_type(self, obj):
        for t in self.types:
            if t == obj:
                return obj
        return None

    def intersect_set(self, obj):
        r = TypesSet()
        for t in obj.types:
            if self.intersect_type(t) is not None:
                r.push(t)
        return r

### CType resolver

@meta.add_method(PrimaryType)
def resolve_type(self, scope):
    t = Type(self._identifier)
    declt = self._decltype
    while not declt is None:
        if isinstance(declt, PointerType) or isinstance(declt, ArrayType):
            t = Pointer(t)
        declt = declt._decltype
    return t

@meta.add_method(FuncType)
def resolve_type(self, scope):
    return_type = PrimaryType.resolve_type(self, scope)
    t = Function(return_type)
    for param in self._params:
        param_t = param.resolve_type(DefScope(), None)
        t.push_param(param_t)
    return t

@meta.add_method(ComposedType)
def resolve_type(self, scope):
    t = Struct(self._identifier)
    if hasattr(self, "fields"):
        if self._identifier in scope.decls:
            raise Exception("Redefinition du symbole `{}`".format(self._identifier))
        new_scope = DefScope(scope)
        for f in self.fields:
            f_type = Variable(f._name, f.resolve_type(new_scope, None))
            t.add_field(f_type)
        scope.decls[self._identifier] = t
    else:
        if not self._identifier in scope.decls:
            raise Exception("Utilisation d'un symbole non defini : `{}`".format(self._identifier))
        t = scope.find_decl(self._identifier)
    return t

### End CType resolver

### Stmt resolver

class DefScope():
    def __init__(self, parent = None):
        self.parent = parent
        self.defs = {}
        self.decls = {}

    def find_def(self, name):
        scope = self
        while not scope is None:
            if name in scope.defs:
                return scope.defs[name]
            scope = scope.parent
        return None

    def find_decl(self, name):
        scope = self
        while not scope is None:
            if name in scope.decls:
                return scope.decls[name]
            scope = scope.parent
        return None

@meta.add_method(parsing.Node)
def resolve_type(self, scope = None, type_set = None):
    if scope is None:
        scope = DefScope()
    if hasattr(self, "body"):
        new_scope = DefScope(scope)
        for node in self.body:
            node.resolve_type(new_scope, type_set)
    if hasattr(self, "expr"):
        self.expr.resolve_type(scope, type_set)
    if hasattr(self, "condition"):
        new_scope = DefScope(scope)
        self.condition.resolve_type(new_scope, type_set)
    if hasattr(self, "thencond"):
        new_scope = DefScope(scope)
        self.thencond.resolve_type(new_cope, type_set)
    if hasattr(self, "elsecond"):
        new_scope = DefScope(scope)
        self.elsecond.resolve_type(new_scope, type_set)

# End Stmt resolver

# Expr resolver

@meta.add_method(Decl)
def resolve_type(self, scope, type_set):
    self.expr_type = self._ctype.resolve_type(scope)
    if self._name in scope.defs:
        raise Exception("redéfinition d'un symbole dans le même scope : `{}`".format(self._name))
    scope.defs[self._name] = self.expr_type

    if hasattr(self, "_assign_expr"):
        new_scope = DefScope(scope)
        if isinstance(self._ctype, FuncType):
            for param in self._ctype.params:
                if param._name in scope.defs:
                    raise Exception("redéfinition d'un symbole dans le même scope : `{}`".format(self._name))
                new_scope.decls[param._name] = param.resolve_type()
        s = TypesSet([ self.expr_type ])
        self._assign_expr.resolve_type(new_scope, s)

    new_scope = DefScope(scope)
    if hasattr(self, "body"):
        self.body.resolve_type(scope)
    return self.expr_type

@meta.add_method(BlockInit)
def resolve_type(self, scope, type_set):
    self.expr_type = Struct("%S")
    for decl in self.body:
        self.expr_type.add_field(decl.resolve_type(scope, None)) #TODO(lakh): remplacer None. Overload pas gere ici
    return self.expr_type

@meta.add_method(Func)
def resolve_type(self, scope, type_set):
    t = self.call_expr.resolve_type(scope, None) 
    if not isinstance(t, Function):
        raise Exception("call_expr de Func n'est pas une fonction : t : {}".format(repr(t))) #TODO(lakh): throw
    self.expr_type = t.return_type
    return self.expr_type


@meta.add_method(Unary)
def resolve_type(self, scope, type_set):
    self.expr_type = self.params[0].resolve_type(scope, type_set)
    if isinstance(self.call_expr, Raw):
        if self.call_expr.value == "*":
            if not isinstance(self.expr_type, Pointer):
                from cnorm.passes import to_c
                raise Exception("On déréférence une expression de type non-pointeur : `{}`".format(self.params[0].to_c())) #TODO(lakh): throw
            self.expr_type = self.expr_type.expr_type
        elif self.call_expr.value == "&":
            self.expr_type = Pointer(self.expr_type)
    return self.expr_type

@meta.add_method(Array)
def resolve_type(self, scope, type_set):
    ts = TypesSet()
    for t in type_set.types:
        ts.push(Pointer(t))

    self.expr_type = self.call_expr.resolve_type(scope, ts)
    if not isinstance(self.expr_type, Pointer): # Array est gere comme un pointeur pour la simplicite
        from cnorm.passes import to_c
        raise Exception("On déréférence une expression de type non-pointeur : `{}`".format(self.params[0].to_c())) #TODO(lakh): throw

    self.expr_type = self.expr_type.expr_type

@meta.add_method(Id)
def resolve_type(self, scope, type_set):
    t = scope.find_def(self.value)
    if not t is None:
        self.expr_type = t
        return t
    elif self.value in decl_keeper.modules:
        module = decl_keeper.modules[self.value]
        module.resolve_type(DefScope(scope), None)
        return module.expr_type
    elif self.value in decl_keeper.classes:
        c = decl_keeper.classes[self.value]
        c.resolve_type(DefScope(scope), None)
        return c.expr_type
    raise Exception("symbole `{}` non défini".format(self.value)) #TODO(lakh): throw

@meta.add_method(Literal)
def resolve_type(self, scope, type_set):
    if self.value[0] == '"':
        self.expr_type = str_type
    else:
        self.expr_type = int_type
    return self.expr_type

@meta.add_method(KoocCast)
def resolve_type(self, scope, type_set):
    self.expr_type = self.ctype.resolve_type(scope)
    self.expr.resolve_type(scope, TypesSet([ self.expr_type ]))
    return self.expr_type

@meta.add_method(KoocCall)
def resolve_type(self, scope, type_set):
    struct_type = self.call_expr.resolve_type(scope, type_set) #TODO(lakh): verifier Struct
    if self.call:
        gtype = Function(None)
        f_types = struct_type.funcs(self.member)
        for (i, p) in enumerate(self.params):
            tset = TypesSet()
            for f_type in f_types:
                param_t = f_type.param(i)
                if not param_t is None:
                    tset.push(f_type)
            f_type = p.resolve_type(scope, tset)
            if not isinstance(f_type, Type):
                raise Exception("Type ambigu")
            gtype.push_param(f_type)
        result = []
        for f_type in f_types:
            if f_type.cmp_params(gtype):
                result.append(f_type)
        if len(result) == 0:
            raise Exception("pas d'overload disponible pour {}".format(self.member))
        if len(result) > 1:
            raise Exception("appel fonction ambigu pour {}".format(self.member))
        self.expr_type = result[0].return_type
        return self.expr_type
    else:
        pass

@meta.add_method(Module)
def resolve_type(self, scope, type_set):
    self.expr_type = Struct(self.ident)
    for decl in self.decls:
        t = decl.resolve_type(DefScope(), None)
        n = decl.saved_name
        self.expr_type.add_field(Variable(n, t))

# End Expr resolver
