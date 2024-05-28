import json
from functools import wraps
from pprint import PrettyPrinter; pp = lambda x: print(json.dumps(x)) #pp = PrettyPrinter().pprint
DEBUG_STRING = False
DEBUG_NAME   = False
DEBUG_INTEGER = False
DEBUG_FLOWP = False

def _called(f):
    @wraps(f)
    def _impl(self, *method_args, **method_kwargs):
        self.do_more = True
        method_output = f(self, *method_args, **method_kwargs)
        method_args[0]['p1'] = True
        return method_output
    return _impl

class WenceCompilerPass1(object):
    """
            TODO: Load bearing jank. 
            we're passing around dict-trees, with 0..N being used for children, and other keys used for node values
            We want to restructure the graph and mark an edge for flow, but due to legacy reasons the edges had to be numeric. 
            Use special value 9090 to mark the flow edge.

            This badly needs refactoring.
        """
    @_called
    def P1_statement(self, node, parent, idx):
        #construct flow-chain from statement
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        first = children[0]
        this = first[1]
        for (x,c) in children[1:]:
            this[9090] = c
            this = c
            del node[x]
        parent[idx] = first[1]
        return True
    

    """
        This feels kinda weird, since we don't usually inspect the parent this deeply.
        However, the compiler is designed this way for a reason
        If it can be done, it might as well be
    """
    @_called
    def P1_flowpoint(self, node, parent, idx):
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int and x != 9090]
        node['value'] = []
        node['flow_id'] = self.flow_id;
        self.flow_id += 1;
        for i,child in children:
            if child['id'] != "NAME":
                raise RuntimeError(f"Expected NAME and got {node[0]['id']} in P1 Flowpoint")
            node['value'].append(child['value'])
            del node[i]
        node['id']="FLOWPOINT"
        if 9090 in parent and parent[9090] is node:
            if DEBUG_FLOWP:
                print(f"Detected flow into flowpoint at {node['value']}")
            node['flow_to'] = True
        if 9090 in node:
            if DEBUG_FLOWP:
                print(f"Detected flow from flowpoint at {node['value']}")
            node['flow_from'] = True
        return True
    """
        TODO: Maybe allow equations with only 1 child (e.g. (1) )
        TODO: Maybe rework equations generally tbh it's fairly legacy wither
    """
    @_called
    def P1_equation(self, node, parent, idx):
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int and x != 9090]
        operator    = children[1][1];
        operator[0] = children[0][1];
        operator[1] = children[2][1];
        parent[idx] = operator;
        #CURSED CURSED CURSED CURSED
        del node

        return True
    
    def __init__(self, ast, blocks, walker):
        self.handlers = [
            {"statement":self.P1_statement},
            {"flowpoint":self.P1_flowpoint},
            {"equation": self.P1_equation},
            ]
        self.ast = ast
        self.blocks = blocks
        self.do_more = False
        self.walker  = walker
        self.flow_id = 0;
    def compile(self):
        hidx = 0
        while True:
            self.do_more = False
            self.walker.walk(self.ast, self.handlers[hidx])
            for block in self.blocks:
                self.walker.walk(block, self.handlers[hidx])
            if not self.do_more:
                hidx += 1
                if hidx == len(self.handlers):
                    break;
        return self.blocks

