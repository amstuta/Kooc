import cnorm
import mangler
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
                    dcl._name = mangler.mimpleSangle(dcl)
                self.typedef_vt_object = decl


    def instanciate_vtable(self):
        d = Declaration()
        res = d.parse("""
        typedef struct _kc_Object Object;
        typedef struct _kc_vt_Object vt_Object;
        vt_Object vtable_Object = {&clean, &isKindOf, &isKindOf, &isInstanceOf, &isInstanceOf};
        """)

        for decl in res.body:
            if hasattr(decl, '_name') and decl._name == 'vtable_Object':
                for (elem, imp) in zip(decl._assign_expr.body, self.implementations['Object'].imps):
                    elem.params[0].value = imp._name
                self.obj_vtable = decl
                return decl
        return None
        

    def clean_implementations(self):
        self.implementations = {}



from kooc_class import Kooc
