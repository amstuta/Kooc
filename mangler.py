
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
            res += '_'
            for par in proto._ctype.params:
                pointer = par._ctype._decltype
                while pointer != None:
                    if type(pointer) == cnorm.nodes.PointerType:
                        res +='P'
                    else:
                        break
                    pointer = pointer._decltype
                res += '$' + par._ctype._identifier + '_'
                

        return res
