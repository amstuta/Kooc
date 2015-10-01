class DeclKeeper:

    _instance = None

    def __init__(self):
        self.ids = []
        self.modules = {}

    def instance():
        if DeclKeeper._instance:
            return DeclKeeper._instance
        DeclKeeper._instance = DeclKeeper()
        return DeclKeeper._instance

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
