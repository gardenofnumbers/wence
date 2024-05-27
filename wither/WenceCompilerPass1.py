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
    #statements must be processed after all p0 manipulation is done, or things bork.
    @_called
    def P1_statement(self, node, parent, idx):
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
    
    
    def __init__(self, ast, blocks, walker):
        self.handlers = {
            "statement":self.P1_statement,
        }
        self.ast = ast
        self.blocks = blocks
        self.do_more = False
        self.walker  = walker
        
    def compile(self):
        while True:
            self.do_more = False
            self.walker.walk(self.ast, self.handlers)
            for block in self.blocks:
                self.walker.walk(block, self.handlers)
            if not self.do_more:
                break
        return self.blocks

