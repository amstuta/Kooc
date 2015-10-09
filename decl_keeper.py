import cnorm
from mangler import *

class DeclKeeper:

    _instance = None

    def __init__(self):
        self.ids = []
        self.modules = {}
        self.types = {}
        self.implementations = {}
        self.classes = {}
        self.inher = {}
        self.typedef_vt_object = None
        self.obj_vtable = None
        self.create_typedef_vt()
        self.instanciate_vtable()

    @staticmethod
    def instance():
        if DeclKeeper._instance:
            return DeclKeeper._instance
        DeclKeeper._instance = DeclKeeper()
        return DeclKeeper._instance


    def create_typedef_vt(self):
        decl_clean = cnorm.nodes.Decl('clean', cnorm.nodes.PrimaryType('void'))
        setattr(decl_clean._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_clean._ctype._decltype, '_decltype', cnorm.nodes.ParenType())
        name = Mangler.instance().mimpleSangle(decl_clean)
        decl_clean._name = name

        decl_isKOf = cnorm.nodes.Decl('isKindOf', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isKOf._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('char'))]))
        setattr(decl_isKOf._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf._ctype._decltype._decltype._params[0]._ctype._decltype, '_decltype', cnorm.nodes.QualType(1))
        name = Mangler.instance().mimpleSangle(decl_isKOf)
        decl_isKOf._name = name
        
        decl_isKOf2 = cnorm.nodes.Decl('isKindOf2', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isKOf2._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf2._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
        setattr(decl_isKOf2._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        name = Mangler.instance().mimpleSangle(decl_isKOf2)
        decl_isKOf2._name = name

        decl_isIOf = cnorm.nodes.Decl('isInstanceOf', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isIOf._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('char'))]))
        setattr(decl_isIOf._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf._ctype._decltype._decltype._params[0]._ctype._decltype, '_decltype', cnorm.nodes.QualType(1))
        name = Mangler.instance().mimpleSangle(decl_isIOf)
        decl_isIOf._name = name

        decl_isIOf2 = cnorm.nodes.Decl('isInstanceOf2', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isIOf2._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf2._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
        setattr(decl_isIOf2._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        name = Mangler.instance().mimpleSangle(decl_isIOf2)
        decl_isIOf2._name = name
        
        ctype = cnorm.nodes.ComposedType('_kc_vt_Object')
        ctype._specifier = 1
        setattr(ctype, 'fields', [decl_clean, decl_isKOf, decl_isKOf2, decl_isIOf, decl_isIOf2])

        decl = cnorm.nodes.Decl('', ctype)
        self.typedef_vt_object = decl


    def instanciate_vtable(self):
        clean = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$clean$$void')])
        isKOf = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isKindOf$$int$P$char')])
        isKOf2 = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isKindOf$$int$P$Object')])
        isIOf = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isInstanceOf$$int$P$char')])
        isIOf2 = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isInstanceOf$$int$P$Object')])
        blockInit = cnorm.nodes.BlockInit([clean, isKOf, isKOf2, isIOf, isIOf2])
        decl = cnorm.nodes.Decl('vtable_Object', cnorm.nodes.PrimaryType('vt_Object'))
        setattr(decl, '_assign_expr', blockInit)
        self.obj_vtable = decl


    def clean_implementations(self):
        self.implementations = {}

        
    def add_id(self, ident):
        self.ids.append(ident)

    def __getitem__(self, ident):
        if ident in self.ids:
            return True
        return False

    def add_module(self, ident, mod):
        self.modules[ident] = mod

    def module_exists(self, ident):
        if ident in self.modules:
            return True
        return True
        
    def get_module(self, ident):
        if self.module_exists(ident):
            return self.modules[ident]
        return None

    def add_type(self, ident, statement):
        self.types[ident] = statement

    def type_exists(self, ident):
        if ident in self.types:
            return True
        return False

    def get_type(self, ident):
        if self.type_exists(ident):
            return self.types[ident]
        return None

    def add_implementation(self, ident, statement):
        self.implementations[ident] = statement

    def implementation_exists(self, ident):
        if ident in self.implementations:
            return True
        return False

    def get_implementation(self, ident):
        if self.implementation_exists(ident):
            return self.implementations[ident]
        return None
            
    def add_class(self, ident, cl):
        self.classes[ident] = cl

    def class_exists(self, ident):
        if ident in self.classes:
            return True
        return False

    def get_class(self, ident):
        if self.class_exists(ident):
            return self.classes[ident]
        return None
