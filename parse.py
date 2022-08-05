import string
import traceback

_depth = 0;

class ASTNode0(object):
    nodeid_ = 0;
    def __init__(self, t, v):
        self.n = ASTNode0.nodeid_;
        ASTNode0.nodeid_ += 1; 
        self.bt = t;
        self.s = v;
        self.parent = None
        self.children = []
        self.touched = False
    def link(self, child):
        if child is None:
            child = ASTNode0("EMPTY", "");
        child.parent = self;
        self.children.append(child)
    def __str__(self):
        global _depth;
        tab = "= "*_depth
        _depth += 1
        s = self._str(tab)
        _depth -= 1 
        return s
    def _str(self, tab):
        return tab + f"{self.bt}({self.n}): {self.s}" +"\n" + (((("").join([str(c) for c in self.children]))) if len(self.children) else "")

    def graph(self):
        gr = f'{self.n} [label="{self.bt}:{self.s}"];\n'
        for i, c in enumerate(self.children):
            gr += f'{self.n} -> {str(c.n)} [ label = "{i}" ]\n'
        
        for c in self.children:
            gr += c.graph();
        return gr;

    
class Parser(object):
    def __init__(self, text):
        self.text = text.replace(" ", "").replace("\n", "").replace("\t", "");
        self.idx  = 0;
        self.pidx = 0;
        self.buf  = "";
    def debug(self, name=None):
        nl = "\n"
        if name is not None:
            print(name)
        else:
            print("\n\n")
        print(f"Buffer: {self.buf}{nl}Tape: {repr(self.text[self.idx+self.pidx:])}{nl}Index: {self.idx}{nl}Pindx: {self.pidx} ")
        #traceback.print_stack()
        #print("\n\n")
        
    def peek(self):
        idx = self.idx + self.pidx;
        if idx >= len(self.text):
            raise RuntimeError("EOF Parsing"); #TODO FIXME more verbose error
        self.pidx += 1;
        return self.text[idx];
    def unpeek(self):
        if self.pidx < 1:
            # this should never happen because we don't unpeek if we haven't peeked
            raise RuntimeError("Internal problem. See comment for details"); 
        self.pidx -= 1;
        
    def poke(self):
        idx = self.idx + self.pidx;
        if idx > len(self.text):
            raise RuntimeError("EOF Parsing"); #TODO FIXME more verbose error
        self.buf += self.text[idx-1];
        
    def consume(self, test):
        _ = False;
        while test(self.peek()):
            _ = True;
            self.poke()
        self.unpeek();
        return _;
    
    def test(self, c):
        if self.peek() == c:
            self.poke()
            return True
        else:
            self.unpeek()
            return False
    
    def pop(self):
        tmp = self.buf
        self.buf = ""
        self.idx += self.pidx
        self.pidx = 0
        return tmp;
    def drop(self):
        self.buf = ""
        self.pidx = 0;
    def unparse(self, s):
        if s.s is None:
            self.debug()
            raise RuntimeError(f"Unparsing invalid ast node with type {s.bt}")
        
        self.idx -= len(s.s)
        if(self.idx < 0):
            raise RuntimeError("Index underflow while unparsing");

    def parseConstant(self):
        # TODO: Return typed value
        if self.test("0") and self.test("x"):
            self.consume(lambda x: x in string.hexdigits)
            return ASTNode0("HEXINT", self.pop())

        self.drop()

        if self.consume(lambda x: x.isdigit()):
            p1 = self.pop();
            if self.test("."):
                if self.consume(lambda x: x.isdigit()):
                    p1 += self.pop();
            return ASTNode0("DECINT", p1);
        self.drop()
        
        if self.test('"'):
            self.consume(lambda x: x != '"')
            if not self.test('"'):
                #internal problem, consume has not left us with the trailing " as expected
                raise RuntimeError("Internal problem. Consult comment");
            
                
            return ASTNode0("STRING", self.pop());
        
        self.drop();
        return None;
    def parseVarname(self):
        if not self.peek() in string.ascii_lowercase:
            self.drop()
            return None
        self.poke();
        self.consume(lambda x: x in (string.ascii_letters + string.digits))
    
        return ASTNode0("VARNAME", self.pop())
         
        
    def parseArrayAccess(self):
        if not self.test("["):
            return None
        self.pop()
        if (rval := self.parseExpression()) is None:
            self.debug()
            raise RuntimeError("Exception while parsing: Failed rval on array index")
        if not self.test("]"):
            raise RuntimeError("Expected ] after array index")
        self.pop()
        arrv = ASTNode0("ARRAY_ACCESS", None);
        arrv.link(rval)
        return arrv

    def parseBlock(self):
        if not self.test("{"):
            return None
        self.pop()
        v = [];
        block = ASTNode0("BLOCK", None)

        if self.test("^"):
            self.pop();
            raise Exception("Unimplemented: Whence Block")
        elif self.test("?"):
            self.pop();
            raise Exception("Unimplemented: Query Block")

        else:
            pn = None
            head = None
            done = False
            while True:
                if (node := self.parseContinuation()) is None:
                    self.debug()
                    raise RuntimeError("Exception while parsing: failed to parse block")
                if head is None:
                    head = node;

                c = self.peek();
                if c == ';' or c == ',':
                    self.pop();
                    dlm = ASTNode0("DROP", None) if c == ';' else ASTNode0("PUSH", None);
                    node.link(dlm);
                    if pn is not None:
                        pn.link(node)
                    pn = dlm;
                
                else:
                    self.unpeek()
                    if pn is not None:
                        pn.link(node)
                    pn = node;
               

                if self.test("}"):
                    self.pop();
                    break;

                
            block.link(head);
            return block;
    def parseOperator(self):
        l = [
            "/",
            "*",
            "+",
            "-",
            "%",

            "&",
            "|",
            "^",
            "~",
            "!",
            "=",
            ">",
            "<",
            ]
        a = self.peek() ; b = self.peek();
        if (b == '=') and (a in l[-4:]):
            #tuple
            op = self.pop()
            return ASTNode0("OP", op)
        else:
            self.unpeek();
        if a in l:
            self.pop();
            return ASTNode0("OP", a)

    def parseEquation(self):
        if not self.test("("):
            return None
        self.pop()
        if (lv := self.parseExpression()) is None:
            self.debug()
            raise RuntimeError("Exception while parsing: failed to parse expression")
        if (op := self.parseOperator()) is not None:
            if (rv := self.parseExpression()) is None:
                self.debug();
                raise RuntimeError(f"Failed to parse rval for operator {op.s}")
            
        if not self.test(")"):
            raise RuntimeError("Expected ) after equation")
        eq = ASTNode0("EQ", None)
        eq.link(lv);
        eq.link(op);
        eq.link(rv);

        return eq;

    def parseValue(self):
        if(node := self.parseVarname()) is not None:
            pass
        elif(node := self.parseConstant()) is not None:
            pass
        
        if node is None:
            return None;
        
        if (aa := self.parseArrayAccess()) is not None:
            aa.link(node)
            return aa
        return node
        
    def parseInvoke(self):
        if not self.test("~"):
            return None
        self.pop();

        i = ASTNode0("INVOKE", None);
        if (n := self.parseBlock()) is not None:
            i.link(n)
        elif (n := self.parseValue()) is not None:
            i.link(n)
        else:
            self.debug();
            raise RuntimeError("Failed to parse invoke target!")
        return i;
        #TODO: check invokation type at compile time


    def parseMagic(self):
        if self.test("|"):
            self.pop();
            return ASTNode0("IO", None);
        return self.parseInvoke()

           


    def parseExpression(self):
        if (node := self.parseBlock()) is not None:
            return node
        if (node := self.parseEquation()) is not None:
            return node
        if (node := self.parseValue()) is not None:
            return node
        if (node := self.parseMagic()) is not None:
            return node
        return None;


    def parseContinuation(self):
        head = None
        node = None
        pn = None
        done = False
        v = [];

        while True:
            if (node := self.parseExpression()) is None:
                self.debug();
                raise RuntimeError("Expected Expression!")
            if head is None:
                head = node   
            if self.test("-"):
                if self.test(">"):
                    self.pop();
                    ct = ASTNode0("YEET", None);
                    node.link(ct)
                    if pn is not None:
                        pn.link(node)
                    pn = ct;
                    continue
                else:
                    raise RuntimeError("invalid syntax")
            else:
                done = True
        
            if pn is not None:
                pn.link(node)
            pn = node
            if done:
                return head

    def parse(self):
        return self.parseBlock();
         