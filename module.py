class Module:
    
    def __init__(self, ident, statement):
        self.decls = {}
        self.ident = ident
        for st in statement.body:
            self.decls[Mangler.instance().muckFangle(st)] = st

    def __getitem__(self, idx):
        if idx in self.decls:
            return self.decls[idx]
        return None
        
