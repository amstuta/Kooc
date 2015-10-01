class DeclKeeper:

    _instance = None

    def __init__(self):
        self.ids = []
        self.modules = {}
        self.types = {}

    @staticmethod
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
