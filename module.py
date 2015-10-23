import mangler

class Module:
    
    def __init__(self, ident, statement, flag):

        # Declarations
        self.decls = []
        for st in statement.body:
            st._name = mangler.muckFangle(st, ident)
            self.decls.append(st)

        # Nom du module
        self.ident = ident

        # Tout ce qui doit etre mis dans le fichier de sortie (extern, ...)
        self.out = []

        # Declaration trouvee dans le fichier courrant ou non
        self.recurs = flag
