from mangler import *

class Module:
    
    def __init__(self, ident, statement, flag):

        # Declarations
        self.decls = {}
        for st in statement.body:
            self.decls[Mangler.instance().muckFangle(ident, st)] = st

        # Nom du module
        self.ident = ident

        # Tout ce qui doit etre mis dans le fichier de sortie (extern, ...)
        self.out = []

        # Declaration trouvee dans le fichier courrant ou non
        self.current_file = flag


    def __getitem__(self, idx):
        if idx in self.decls:
            return self.decls[idx]
        return None
        
