import json
from parse import witherParser
src = """
printable   := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | "<" | "=" | ">" | "?" | "@" | "[" | "\\" | "]" | "^" | "_" | "`" | "{" | "|" | "}" | "~" 
letter      := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"
hex         := "a" | "b" | "c" | "d" | "e" | "f"
digit       := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
operator    := "<<" | ">>" | "<=" | ">=" | "!=" | "==" | "/" | "*" | "+" | "-" | "%" | "&" | "|" | "^" | "~" | "!" | "=" | ">" | "<" 
glob        := "%"
this        := "_"
sysc        := "^"
invoke      := "~"
string      := "'" ?( *{ printable } ) "'"
integer     := "0x" *{ digit | hex } | digit ?( *{ digit } )
array       := "[" *{ expression ?( comma ) } "]"
constant    := integer | string | array
name        := letter ?( *{ letter | digit } ) 
subscript   := "[" expression "]
equation    := "(" expression ?( operator expression ) ")"
statement   := expression ?( *{ "->" expression } )
block       := "{" ?( unglom ) *{ statement semicolon } "}"
twople      := expression colon expression
dict        := "${" *{ twople ?( comma ) } "}"
filter      := "?{" *{ twople ?( comma ) } "}"
glom        := "@{" *{ expression ?( comma ) } "}"
unglom      := "#{" *{ name ?( comma ) } "}" semicolon
expression2 := block | filter | dict | glom | unglom | equation | name | constant | glob | this | sysc
expression  := ?( invoke ) expression2 ?( *{ subscript } ) 
semicolon   := ";"
colon       := ":"
comma       := ","
file        := *{ statement semicolon } 

"""




class WitherStack(object):
    def __init__(self):
        self.s  = []
        self.b = []
    def new_frame(self):
        self.s.insert(0, self.b)
        self.b = []
        print(f"@@@@ -> @@@ {json.dumps(self.s)}")
    def end_frame(self):
        print(f"@@@@ <- @@@ {json.dumps(self.s)}")
        print(f"            {json.dumps(self.b)}")
        _ = self.b
        self.b = self.s.pop(0)
        return _
    def buffer(self, v):
        self.b.append(v)
        print(f"@@@@    @@@ {json.dumps(self.b)}")
    def extend(self, v):
        self.b += v
        print(f"@@@@ ## @@@ {json.dumps(self.b)}")
class WitherInterpreter(object):
    def __init__(self, machine):
        self.machine = machine
        self.stack   = WitherStack();
        self.tags    = [ 
                        'this', 
                        'sysc', 
                        'string', 
                        'integer', 
                        'array', 
                        'constant', 
                        'name', 
                        'subscript', 
                        'equation', 
                        'statement', 
                        'block',
                        'twople', 
                        'dict', 
                        'filter', 
                        'glom', 
                        'unglom', 
                        'invoke',
                        'file']
        self.drop = [';', '{', '}','(', ')', '[',']', ',', '@{', '${', '?{', ',', ':', '->', '#{', '~', '%']
        
    def run(self, source):
        self.tape = source.replace(" ", "").replace("\n", "").replace("\t", "") 
        self.stack.new_frame();
        (v, l) = self.recurse("file", self.machine["file"], self.tape)
        if not v:
            print(f"Error while processing at {l}")
        out = {
            'id':"file"
        }
        for i,s in enumerate(self.stack.end_frame()):
            out[i] = s
        return out
         

    def recurse(self, i, sl, tape):
        for s in sl:
            match s["id"]:
                case "Match":
                    if tape.startswith(s[0]):
                        print(f"____ Matched {s[0]} {i} {tape}")
                        tape = tape[len(s[0]):]
                        if not s[0] in self.drop:
                            self.stack.buffer({
                                'id':i, 0:s[0]
                            })

                    else:
                        return (False, tape)
                case "Optional":
                    
                    f = s[0]
                    (v, l) = self.recurse(i, f, tape)
                    if v:
                        tape = l
                case "Repeat":
                    self.stack.new_frame();
                    f = s[0]
                    (v, l) = (True, tape)
                    while v:
                        (v, l) = self.recurse(i, f, tape)
                        if(v):
                            tape = l
                        else:
                            f = self.stack.end_frame()
                            self.stack.extend(f)
                        
                case "Goto":
                    print(f")(}}{{)( Going: {s[0]} {tape}")
                    self.stack.new_frame()
                    (v, l) = self.recurse(s[0], self.machine[s[0]], tape)
                    if not v:
                        self.stack.end_frame();
                        return (False, tape)
                    else:
                        f = self.stack.end_frame()
                        if s[0] in self.tags:
                            print(f")(}}{{)( from {s[0]} {json.dumps(f)}")                            
                            self.stack.buffer({"id": s[0], 0: f})
                        else:
                            self.stack.extend(f)
                    tape = l

                case "Any":
                    for v in [s[v] for v in s if type(v) is int]:
                        (v, l) = self.recurse(i, v, tape)
                        if v:
                            tape = l
                            break;
                    else:
                        return (False, tape)
        return (True, tape)
                    
                    


p = witherParser();
i = WitherInterpreter(p.ingest(src));
print(src)
print(json.dumps(p.states))
print()
print()
print()
#import code; code.interact(local=locals());

src = """
{
    
    @{a,b} -> ?{ 
        (b==0) : {a;}, 
        (1): { a % b - > r; @{b,r} -> ~e;}
    };
} -> e;
{
    @{2740, 1760} -> ~e;
} -> m;
~m;
"""
src = """
{
    #{a, l, h}; 
    % -> ~p ->{
        @{a,l,(%-1)} -> ~q;
        @{d,(%+1),h} -> ~q;
    };
} -> q;
{
    #{a, i, j};
    @{a[i], a[j]}
    -> ~{
        #{ai, aj}; 
        aj->a[i]; 
        ai->a[j];
    };
} -> s;
{
    #{a, l, h};
    @{(l - 1), l, a[h]} -> ~{
        #{i, j, v};
        _ -> ?{
            (j < (h-1)):{
                % -> ?{
                    (a[j] < v): {
                        @{a, (i+1), j} -> ~s;
                        @{(i+1), (j+1), v} -> ~%;                            
                    }
                }; 
            }
        };
    };
    @{a, (i+1), h} -> ~s;
    (i+1);
}-> p;
"""
print(src)

tree = i.run(src)

print("finished!?")
print()
print(json.dumps(tree))