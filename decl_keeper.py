import cnorm
import mangler
from cnorm.parsing.declaration import Declaration


ids = []
modules = {}
implementations = []
classes = {}
inher = {}
typedef_vt_object = None
obj_vtable = None


def create_typedef_vt():

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

    res2 = d.parse(
        '''
        typedef struct _kc_Object Object;
        void clean(Object *);
        int isKindOf(Object *, const char *);
        int isKindOf(Object *, Object *);
        int isInstanceOf(Object *, const char *);
        int isInstanceOf(Object *, Object *);
        ''')
    res2.body.pop(0)
    for decl in res.body:
        if isinstance(decl._ctype, cnorm.nodes.ComposedType) and decl._ctype._identifier == '_kc_vt_Object':
            for (dcl, proto) in zip(decl._ctype.fields, res2.body):
                dcl._name = mangler.mimpleSangle(proto)
            global typedef_vt_object
            typedef_vt_object = decl



def instanciate_vtable():
    global implementations
    d = Declaration()
    res = d.parse("""
    typedef struct _kc_Object Object;
    typedef struct _kc_vt_Object vt_Object;
    vt_Object vtable_Object = {&clean, &isKindOf, &isKindOf, &isInstanceOf, &isInstanceOf};
    """)
    for decl in res.body:
        if hasattr(decl, '_name') and decl._name == 'vtable_Object':
            for (elem, imp) in zip(decl._assign_expr.body, implementations[0].imps):
                elem.params[0].value = imp._name
            global obj_vtable
            obj_vtable = decl
            return decl
    return None


def clean_implementations():
    global implementations
    implementations = []


def reset():
    global ids, modules, implementations, classes, inher
    ids = []
    modules = {}
    implementations = []
    classes = {}
    inher = {}
