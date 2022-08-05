import json

src = """
printable   := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "!" | "#" | "$" | "%" | "&" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | "<" | "=" | ">" | "?" | "@" | "[" | "\\" | "]" | "^" | "_" | "`" | "{" | "|" | "}" | "~" 
letter      := "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
hex         := "a" | "b" | "c" | "d" | "e" | "f"
digit       := "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
operator    := "/" | "*" | "+" | "-" | "%" | "&" | "|" | "^" | "~" | "!" | "=" | ">" | "<" | "<<" | ">>" | "<=" | ">=" | "!=" | "=="
this        := "%"
sysc        := "^"
string      := "'" ?( *{ printable } ) "'"
integer     := "0x" *{ digit | hex } | digit ?( *{ digit } )
array       := "[" *{ expression ?( "," ) } "]"
constant    := integer | string | array
name       := letter ?( *{ letter | digit } ) 
subscript   := "[" expression "]
equation    := "(" expression ?( operator expression ) ")"
statement   := expression ?( *{ "->" expression } )
block       := "{" ?( unglom ) *{ statement ?( ";" ) } "}"
dict        := "${" *{ expression ":" expression ?( "," ) } "}"
filter      := "?{" *{ expression ":" expression ?( "," ) } "}"
glom        := "@{" *{ statement ?( "," ) } "}"
unglom      := "#{" *{ name ?( "," ) } "}"
expression2 := block | filter | dict | glom | equation | name | constant | this | sysc
expression  := ?( "~" ) expression2 ?( *{ subscript } ) """


class TerminationFound(Exception):
    pass
class SourceProvider(object):
    def __init__(self, source):
        self.source = source
    
class WitherInterpreter(object):
    def __init__(self, machine):
        self.machine = machine
        
    def run(self, source):
        self.tape = source.replace(" ", "").replace("\n", "").replace("\t", "") 
        (v, l) = self.recurse("block", self.machine["block"], self.tape)
        if not v:
            print(f"Error while processing at {l}")

    def recurse(self, i, sl, tape):
        #print(f"Enter node {i} {tape}")
        for s in sl:
            #print(f"subnode {s}")
            match s["id"]:
                case "Match":
                    if tape.startswith(s[0]):
                        print(f"Matched {s[0]} {i} {tape}")
                        tape = tape[len(s[0]):]
                    else:
                        return (False, tape)
                case "Optional":
                    f = s[0]
                    (v, l) = self.recurse(i, f, tape)
                    if v:
                        tape = l
                case "Repeat":
                    f = s[0]
                    (v, l) = (True, tape)
                    while v:
                        (v, l) = self.recurse(i, f, tape)
                        if(v):
                            tape = l
                        else:
                            print(f"Done matching repeat for {i}")
                        
                case "Goto":
                    #print(f"Going: {self.machine[s[0]]}")
                    (v, l) = self.recurse(s[0], self.machine[s[0]], tape)
                    if not v:
                        return (False, tape)
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
                    
                    

class witherParser(object):
    def __init__(self):
        self.states = {}
    def ingest(self, source):
        source = list(filter(None, source.split ("\n")))
        print(f"Processing {len(source)} lines of wither")
        for line in source:
            self.ingestLine(line);
        return WitherInterpreter(self.states)
    def ingestLine(self, line):
        words = list(filter(None, line.split(" ")))
        print(f"Processing {len(words)} words of wither {words}")
        s = words[0]
        if s in self.states:
            raise RuntimeError(f"Redeclaration of state {s}!")
        if words[1] != ":=":
            raise RuntimeError("Syntax error (expected := after state name)")
        stateSeries = {0: [], "id":"Any"}#SparseList()
        self.recurse(words[2:], stateSeries)
        if 1 not in stateSeries:
            stateSeries = stateSeries[0]
        else:
            stateSeries = [stateSeries]
        self.states[s] = stateSeries
        
    def recurse(self, tape, series, terminate = "", idx=0):
        if len(tape) == 0:
            if terminate != "":
                raise RuntimeError(f"Expected to reach {terminate} before EOL")
            return
        word = tape.pop(0)
        if word == terminate:
            raise TerminationFound
        if word.startswith('"'):
            series[idx].append({"id":"Match", 0: word.strip('"')})
        elif word == "?(":
            subseries = {0: [], "id":"Any"}#SparseList()         
            try:
                self.recurse(tape, subseries, terminate=")", idx=0)
            except TerminationFound:
                if not 1 in subseries:
                    subseries = subseries[0]
                else:
                    subseries = [subseries]
                series[idx].append({"id":"Optional", 0:  subseries})
            else:
                raise RuntimeError("This should be unreachable?? parsing ?( fail")
        elif word == "*{":
            subseries = {0: [], "id":"Any"}#SparseList()#{0: []}
            try:
                self.recurse(tape, subseries, terminate="}", idx=0)
            except TerminationFound:
                if not 1 in subseries:
                    subseries = subseries[0]
                else:
                    subseries = [subseries]
                series[idx].append({"id":"Repeat", 0: subseries})
            else:
                raise RuntimeError("This should be unreachable?? parsing *{ fail")
        elif word.isalnum():
            series[idx].append({"id":"Goto", 0:  word})
        elif word == "|":
            idx += 1;
            series[idx] = []
        else:
            raise RuntimeError(f"Unimplemented word {word}")
        self.recurse(tape, series, terminate=terminate, idx=idx)

p = witherParser();
i = p.ingest(src);
print(src)
print(json.dumps(p.states))
print()
print()
print()
input()
src = """
{
    a -> b;
    c -> d;
    @{e->g->z,f} -> {m->n;};
}
"""
i.run(src)
print("finished!?")