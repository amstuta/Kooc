class DeclKeeper:

    _instance = None

    def __init__(self):
        self.ids = []
        self.modules = {}
        self.types = {}
        self.implementations = {}
        self.classes = {}
        self.inher = {}

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

    def add_implementation(self, ident, statement):
        self.implementations[ident] = statement

    def implementation_exists(self, ident):
        if ident in self.implementations:
            return True
        return False

    def get_implementation(self, ident):
        if self.implementation_exists(ident):
            return self.implementations[ident]
        return None
            
    def add_class(self, ident, cl):
        self.classes[ident] = cl

    def class_exists(self, ident):
        if ident in self.classes:
            return True
        return False

    def get_class(self, ident):
        if self.class_exists(ident):
            return self.classes[ident]
        return None
