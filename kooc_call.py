from pyrser.parsing.node import Node


class KoocCall(Node):

    def __init__(self, module, function, expr_type=None, params=None):
        self.module = module
        self.function = function
        self.expr_type = expr_type
        self.params = params

class KoocCast(Node):
    def __init__(self, ctype, expr):
        self.ctype = ctype
        self.expr = expr

