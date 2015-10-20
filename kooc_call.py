class KoocCall:

    def __init__(self, module, function, expr_type=None, params=None):
        self.module = module
        self.function = function
        self.expr_type = expr_type
        self.params = params
