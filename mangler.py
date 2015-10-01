
import cnorm

class Mangler:
    
    def __init__(self):
        pass

    inst = None

    @staticmethod
    def instance():
        if (Mangler.inst == None):
            Mangler.inst = Mangler()

        return Mangler.inst

    def muckFangle(self, proto, module):
        res = ""
        if type(proto._ctype) == cnorm.nodes.FuncType :
            res += "Func"
        else:
            res += "Var"
        res += '$'
        res += module + '$'
        res += proto._name + '$'
        res += '$' + proto._ctype._identifier
        if type(proto._ctype) == cnorm.nodes.FuncType:
            for par in proto._ctype.params:
                res += '$' + par._ctype._identifier

        return res
