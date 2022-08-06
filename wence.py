import json

DEBUG_WALKER = False
DEBUG_STRING = False
DEBUG_NAME   = False
DEBUG_INTEGER = False

class WenceCompilerPass0(object):
    def P0_String(self, node, parent, idx):
        if DEBUG_STRING:
            print(f"Visit string: {json.dumps(node)}")
        children = [node[x] for x in node if type(node[x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'printable':
                raise RuntimeError(f"TREE ERROR! expect printable, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = 'STRING'
        node[0] = s
        return False   
    def P0_Name(self, node, parent, idx):
        if DEBUG_NAME:
            print(f"Visit name: {json.dumps(node)}")
        children = [node[x] for x in node if type(node[x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'letter' and child['id'] != 'digit':
                raise RuntimeError(f"TREE ERROR! expect letter/digit, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = 'NAME'
        node[0] = s
        return False
    def P0_Integer(self, node, parent, idx):
        if DEBUG_INTEGER:
            print(f"Visit integer: {json.dumps(node)}")
        
        match node[0]['id']:
            case 'base10':
                mode = 10
            case 'base16':
                mode = 16
            case default:
                raise RuntimeError(f"TREE ERROR!! expect integer type, got {node[0]['id']}")
            
        children = [node[0][x] for x in node[0] if type(node[0][x]) == dict]
        s = "";
        for child in children:       
            if child['id'] != 'hex' and child['id'] != 'digit':
                raise RuntimeError(f"TREE ERROR! expect hex/digit, got {child['id']}")
            s += child[0]
        node.clear()
        node['id'] = f'INT'
        node[0] = int(s, base=mode)
        return False
    def P0_Block(self,node, parent, idx):
        node['eid'] = self.eid
        self.ast["blocks"][self.eid] = node
        parent[idx] = {
            "id": "BLOCK_REF",
            "BLOCK_ID": self.eid
        }
        self.eid += 1;
        return True

    def __init__(self, ast):
        self.handlers = {
            "string" : self.P0_String,
            "name": self.P0_Name,
            "integer" : self.P0_Integer,
            "block": self.P0_Block,   
        }
        self.ast = ast
        self.eid = 0
        ast["blocks"] = {'id': "BLOCK_STORE "}
        


class WenceWalker(object):
   

    def __init__(self, ast):
        self.trace = ""
        self.ast = ast
        
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
            self.walk(child, handlers, depth+1)




class WenceCompiler(object):
    def __init__(self, ast):
        self.ast = ast
        self.walker = WenceWalker(ast);

    def compile(self):
        p0 = WenceCompilerPass0(self.ast);
        self.walker.walk(self.ast, p0.handlers)
        