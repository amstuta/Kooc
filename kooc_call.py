from pyrser.parsing.node import Node


class KoocCall(Node):

    def __init__(self, call_expr):
        self.call_expr = call_expr

class KoocCast(Node):
    def __init__(self, ctype, expr):
        self.ctype = ctype
        self.expr = expr

