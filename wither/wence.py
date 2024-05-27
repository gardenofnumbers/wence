import json
from .WenceCompilerPass0 import WenceCompilerPass0
from .WenceCompilerPass1 import WenceCompilerPass1
from .WenceDotGen import WenceDotGen
DEBUG_WALKER = False
DEBUG_UNIMPL = False
class WenceWalker(object):
    def __init__(self, ast):
        self.trace = ""
        self.ast = ast
        self.unimpl = set()

    def walk(self, node, handlers, depth = 0):
        children = [(x, node[x]) for x in node if type(node[x]) == dict and type(x) == int]
        if DEBUG_WALKER:
            print("\t"*depth + f"c: {node['id']} ({len(children)})")
            print("\t"*depth + json.dumps([c[1]['id'] for c in children]))
            self.trace += f" {node['id']}"
        for (idx, child) in children:
            if child['id'] in handlers:
                if not handlers[child['id']](child, node, idx):
                    continue
            else:
                if DEBUG_UNIMPL:
                    print(f"UNIMPLEMENTED: {child['id']}")
                self.unimpl.add(child['id']) 
            self.walk(child, handlers, depth+1)

class WenceCompiler(object):
    def __init__(self, ast):
        self.ast = ast
        self.walker = WenceWalker(ast);

    """
        TODO: Fully refactor to combine ast/blocks into a single array (since `blocks` is a list of AST objects)
              as is, DotGen takes a blocks array, just need to refactor the other two compile() calls. Just being lazy for now
    """
    def compile(self):
        p0 = WenceCompilerPass0(self.ast, self.walker);
        blocks = p0.compile()
        p1 = WenceCompilerPass1(self.ast, blocks, self.walker);
        blocks = p1.compile()
        
        dot = WenceDotGen([self.ast] + blocks)

        return dot.generate(), dot.blocks
    

        
        