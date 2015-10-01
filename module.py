from mangler import *

class Module:
    
    def __init__(self, ident, statement, flag):

        # Declarations
        self.decls = {}
        for st in statement.body:
            dec_name = Mangler.instance().muckFangle(st, ident)
            st._name = dec_name
            self.decls[dec_name] = st

        # Nom du module
        self.ident = ident

        # Tout ce qui doit etre mis dans le fichier de sortie (extern, ...)
        self.out = []

        # Declaration trouvee dans le fichier courrant ou non
        self.recurs = flag


    def __getitem__(self, idx):
        if idx in self.decls:
            return self.decls[idx]
        return None
        
