class Module:
    
    def __init__(self):
        self.modules = {}

    def __getitem__(self, idx):
        return self.modules[idx]

    def __setitem__(self, idx, val):
        self.modules[idx] = val

    def __delitem__(self, idx):
        del self.modules[idx]
