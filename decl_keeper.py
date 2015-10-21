import cnorm
from mangler import *
from cnorm.parsing.declaration import Declaration

class DeclKeeper:

    _instance = None

    def __init__(self):
        self.ids = []
        self.modules = {}
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

        # Problème mangling
        d = Declaration()
        res = d.parse(
            '''
            typedef struct _kc_Object Object;
            struct _kc_vt_Object {
            void (*clean)(Object *);
            int (*isKindOf)(Object *, const char *);
            int (*isKindOf)(Object *, Object *);
            int (*isInstanceOf)(Object *, const char *);
            int (*isInstanceOf)(Object *, Object *);
            }; ''')
        
        for decl in res.body:
            if isinstance(decl._ctype, cnorm.nodes.ComposedType) and decl._ctype._identifier == '_kc_vt_Object':
                for dcl in decl._ctype.fields:        
                    dcl._name = Mangler.instance().mimpleSangle(dcl)
                self.typedef_vt_object = decl

        """
        decl_clean = cnorm.nodes.Decl('clean', cnorm.nodes.PrimaryType('void'))
        setattr(decl_clean._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_clean._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
        setattr(decl_clean._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        name = Mangler.instance().mimpleSangle(decl_clean)
        decl_clean._name = name

        decl_isKOf = cnorm.nodes.Decl('isKindOf', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isKOf._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object')),
                                                                                 cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('char'))]))
        setattr(decl_isKOf._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf._ctype._decltype._decltype._params[1]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf._ctype._decltype._decltype._params[1]._ctype._decltype, '_decltype', cnorm.nodes.QualType(1))
        name = Mangler.instance().mimpleSangle(decl_isKOf)
        decl_isKOf._name = name
        
        decl_isKOf2 = cnorm.nodes.Decl('isKindOf2', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isKOf2._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf2._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object')),
                                                                                  cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
        setattr(decl_isKOf2._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isKOf2._ctype._decltype._decltype._params[1]._ctype, '_decltype', cnorm.nodes.PointerType())
        name = Mangler.instance().mimpleSangle(decl_isKOf2)
        decl_isKOf2._name = name

        decl_isIOf = cnorm.nodes.Decl('isInstanceOf', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isIOf._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object')),
                                                                                 cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('char'))]))
        setattr(decl_isIOf._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf._ctype._decltype._decltype._params[1]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf._ctype._decltype._decltype._params[1]._ctype._decltype, '_decltype', cnorm.nodes.QualType(1))
        name = Mangler.instance().mimpleSangle(decl_isIOf)
        decl_isIOf._name = name

        decl_isIOf2 = cnorm.nodes.Decl('isInstanceOf2', cnorm.nodes.PrimaryType('int'))
        setattr(decl_isIOf2._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf2._ctype._decltype, '_decltype', cnorm.nodes.ParenType([cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object')),
                                                                                  cnorm.nodes.Decl('', cnorm.nodes.PrimaryType('Object'))]))
        setattr(decl_isIOf2._ctype._decltype._decltype._params[0]._ctype, '_decltype', cnorm.nodes.PointerType())
        setattr(decl_isIOf2._ctype._decltype._decltype._params[1]._ctype, '_decltype', cnorm.nodes.PointerType())
        name = Mangler.instance().mimpleSangle(decl_isIOf2)
        decl_isIOf2._name = name
        
        ctype = cnorm.nodes.ComposedType('_kc_vt_Object')
        ctype._specifier = 1
        setattr(ctype, 'fields', [decl_clean, decl_isKOf, decl_isKOf2, decl_isIOf, decl_isIOf2])

        decl = cnorm.nodes.Decl('', ctype)
        
        #self.typedef_vt_object = decl
        """


    def instanciate_vtable(self):
        clean = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$clean$$void$P$Object')])
        isKOf = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isKindOf$$int$P$Object$P$char')])
        isKOf2 = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isKindOf$$int$P$Object$P$Object')])
        isIOf = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isInstanceOf$$int$P$Object$P$char')])
        isIOf2 = cnorm.nodes.Unary(cnorm.nodes.Raw('&'), [cnorm.nodes.Id('Func$Object$isInstanceOf$$int$P$Object$P$Object')])
        blockInit = cnorm.nodes.BlockInit([clean, isKOf, isKOf2, isIOf, isIOf2])
        decl = cnorm.nodes.Decl('vtable_Object', cnorm.nodes.PrimaryType('vt_Object'))
        setattr(decl, '_assign_expr', blockInit)
        self.obj_vtable = decl


    def clean_implementations(self):
        self.implementations = {}



from kooc_class import Kooc
