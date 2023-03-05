import json
from functools import wraps

DEBUG_STRING = False
DEBUG_NAME   = False
DEBUG_INTEGER = False

def _called(f):
    @wraps(f)
    def _impl(self, *method_args, **method_kwargs):
        self.do_more = True
        method_output = f(self, *method_args, **method_kwargs)
        method_args[0]['p1'] = True
        return method_output
    return _impl

class WenceCompilerPass1(object):
    @_called
    def P0_equation(self, node, parent, idx):
        return True
    
    @_called
    def P0_flowpoint(self, node, parent, idx):
        raise Exception("Code Left in for now, flowpoints must be calculated later (when loops can be constructed in the graph)")
        node['id'] = "FLOWPOINT"
        node['fid'] = self.fid
        self.ast['flowps'][self.fid] = node
        self.fid += 1
        return True
    
    @_called
    def P0_statement(self, node, parent, idx):
        #reorder statement 

        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        first = children[0]
        #when in doubt, perform fuckery
        this = first[1]
        for (x,c) in children[1:]:
            this[69] = c
            this = c
            del node[x]

        parent[idx] = first[1]
        
        return True
    
    def __init__(self, ast, walker):
        self.handlers = {
            #"flowpoint":self.P0_flowpoint,
            "statement":self.P0_statement,
        }
        self.ast = ast
        self.do_more = False
        self.walker  = walker
        self.fid     = 0

    def compile(self):
        while True:
            self.do_more = False
            self.walker.walk(self.ast, self.handlers)
            self.walker.walk(self.ast['blocks'], self.handlers)
            if not self.do_more:
                break
        