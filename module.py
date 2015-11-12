import mangler
import cnorm
from cnorm.nodes import *
from copy import deepcopy

class Module:
    
    def __init__(self, ident, statement, flag):

        # Declarations
        self.decls = []
        self.decls_vars = []
        for st in statement.body:
            st.saved_name = st._name
            st._name = mangler.muckFangle(st, ident)
            if not isinstance(st._ctype, cnorm.nodes.FuncType):
                self.decls_vars.append(st)
                tmp = deepcopy(st)
                if hasattr(tmp, '_assign_expr'):
                    delattr(tmp, '_assign_expr')
                tmp._ctype._storage = 4
                self.decls.append(tmp)
            else:
                self.decls.append(st)

        # Nom du module
        self.ident = ident

        # Tout ce qui doit etre mis dans le fichier de sortie (extern, ...)
        self.out = []

        # Declaration trouvee dans le fichier courrant ou non
        self.recurs = flag

    def funcs(self, name):
        out = []
        for decl in self.decls:
            if decl.saved_name == name and isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out

    def variables(self, name):
        out = []
        for decl in self.decls:
            if decl.saved_name == name and not isinstance(decl._ctype, FuncType):
                out.append(decl)
        return out
