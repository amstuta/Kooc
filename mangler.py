
import cnorm

class Mangler:
    
    def __init__(self):
        pass

    inst = None
    speci = {4 : "L",
             5 : "LL",
             6 : "S"}

    @staticmethod
    def instance():
        if (Mangler.inst == None):
            Mangler.inst = Mangler()
        return Mangler.inst

    def changeClass(self, proto, newClassy, oldClassy):
        return proto.replace(oldClassy, newClassy)


    def muckFangle(self, proto, module):
        res = ""
        if type(proto._ctype) == cnorm.nodes.FuncType :
            res += "Func"
        else:
            res += "Var"
        res += '$'
        res += module + '$'
        res += proto._name + '$'
        pointerR = proto._ctype._decltype
        while pointerR != None:
            if type(pointerR) == cnorm.nodes.PointerType:
                res += 'P'
            elif type(pointerR) == cnorm.nodes.ArrayType:
                res += 'A'    
            pointerR = pointerR._decltype
            if proto._ctype._specifier in range(4,7):
                res += Mangler.speci[proto._ctype._specifier]
        res += '$' + proto._ctype._identifier
        if type(proto._ctype) == cnorm.nodes.FuncType:
            for par in proto._ctype.params:
                pointer = par._ctype._decltype
                res += '$'
                while pointer != None:
                    if type(pointer) == cnorm.nodes.PointerType:
                        res += 'P'
                    elif type(pointer) == cnorm.nodes.ArrayType:
                        res += 'A'
                    pointer = pointer._decltype
                if par._ctype._specifier in range(4,7):
                    res += Mangler.speci[par._ctype._specifier]
                res += '$' + par._ctype._identifier
        return res

    def mimpleSangle(self, proto):
        res = ""
        res += proto._name + '$'
        pointerR = proto._ctype._decltype
        while pointerR != None:
            if type(pointerR) == cnorm.nodes.PointerType:
                res += 'P'
            elif type(pointerR) == cnorm.nodes.ArrayType:
                res += 'A'    
            pointerR = pointerR._decltype
            if proto._ctype._specifier in range(4,7):
                res += Mangler.speci[proto._ctype._specifier]
        res += '$' + proto._ctype._identifier
        if type(proto._ctype) == cnorm.nodes.FuncType:
            for par in proto._ctype.params:
                pointer = par._ctype._decltype
                res += '$'
                while pointer != None:
                    if type(pointer) == cnorm.nodes.PointerType:
                        res += 'P'
                    elif type(pointer) == cnorm.nodes.ArrayType:
                        res += 'A'
                    pointer = pointer._decltype
                if par._ctype._specifier in range(4,7):
                    res += Mangler.speci[par._ctype._specifier]
                res += '$' + par._ctype._identifier
        return res
