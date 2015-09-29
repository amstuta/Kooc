class Types:
    def __init__(self):
        self.types = {}

    def __getitem__(self, idx):
        return self.types[idx]

    def __setitem__(self, idx, val):
        self.types[idx] = val

    def __delitem__(self, idx):
        del self.types[idx]
