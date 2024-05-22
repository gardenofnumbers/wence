```
'hello world' -> #{stdout};
```
### Hello World

Wence is an experimental dataflow oriented programming language currently in the early prototyping stage, developed as a toy and learning project by numbers. Wence is syntactically flexible by design, often allowing multiple equivilent expressions of the same semantics, and also allowing for certain semantically useless constructions. This design decision is intended to enable a motivated programmer to elegantly express complex programs, while simplifying the parser and compiler.

This document is intended to provide both a first-look onboarding to the syntax and semantics of Wence, as well as to provide a snapshot of design principles for the language. For additional details about language implementation, and for information on wence's grammar DSL ("Wither"), see other docs (pending).  

Programs in wence are defined by the flow of data between nodes, primarily by using the wire operator "->". A special node type, a "flowpoint", is provided to allow for IO and nonlocal dataflow. Statements are composed by a series of nodes joined by the wire operator, and organized into blocks. Wence does not have a strictly familiar analogue to "functions" in a traditional language. Blocks provide much of the functionality expected from traditional functions, such as encapsulation of scope ("local variables", "closures") and input/output abstraction ("arguments", "return values").  

The wire operator `->` can be thought of as saying "take the wire value output from the node on the left, and provide it as input to the node on the right." The wire value is an abstract object which contains both a runtime snapshot of the current scope (analoguous to a closure) and an ordered array of values (explicit output from the source node). Often, the explicit array can be ignored, in which case the wire operator primarily defines execution order and dependencies for nodes.

### Starter Example (Euclid GCD)

For a simple example of a program in Wence, let us examine an implementation of Euclid's GCD algorithm, which can be expressed in recursive, controlflow driven code as:  

```
function gcd(a, b)
    if b = 0
        return a
    else
        return gcd(b, a mod b)
```
(source: wikipedia)

In wence, Euclid's algorithm can be implemented as:
```
#{a, b} -> ?{
        (b==0) : { a -> #{stdout} },
        (1)    : { @{b, (a%b)} -> #{a, b} }
};
@{2740, 5984} -> #{a, b};
```

Let's break this down node by node:

```
#{a, b}
```
This is a flowpoint. Flowpoints take the form: `#{label, ...}` 
Downstream nodes from a flowpoint will be executed once all labels within the flowpoint have received data.
Labels within a flowpoint are "in scope" for all dependant nodes, allowing their values to be accessed directly.

In this example, all subsequent code depends on this flowpoint, so it will not execute until data becomes available on both `a` and `b`.

```
?{
```
This is a filter. Filters take the form:
```
?{
    (condition) : { block },
    (condition) : { block }
}
```
Conditions can utilize any in-scope values. Conditions are evaluated sequentially, halting at the first true condition, and executing it's associated block. These blocks inherit scope from the filter's parent, and also receive any wire input from the filter itself. Output from the selected block is then provided to any wire children of the filter. (note: wire inputs and outputs for blocks described later. this example does not utilize this feature)

```
(b==0) : { a -> #{stdout} },
```
The first condition is simple. If the `b` received from the flowpoint is 0, write `a` to stdout.

```
(1)    : { @{b, (a%b)} -> #{a, b} }
```
The second condition is always evaluated if the first condition is false. 

```
{ @{b, (a%b)} -> #{a, b} }
```
`@{}` is a glom node. A glom node takes the form `@{expression, ...}`, and provides a mechanism for bundling values for the wire operator. 
E.g. `@{foo, bar} -> #{bizz, buzz}` could also be written as:
```
foo -> #{bizz};
bar -> #{buzz};
```
However, code written in this way quickly becomes unwieldy due to dependancy duplication. 

In this example, `b` is written to `a` and a new value for `b` is computed and written to `b`. Note that this forms a "loop" with the statement utilizing the same flowpoint for both input and output.


```
@{2740, 5984} -> #{a, b};
```
This statement provides static input to `a` and `b` in order to provide starting conditions for execution. A more 'useful' program might retrieve these values from stdin.

### More dataflow details
When all dependencies of a given flowpoint become available, that flowpoint and it's children are added to the execution queue. Each dependency chain will be executed once, after which the flowpoint state is reset. 

TODO: design decision, how should multiple desynchronized writes be handled to nontrivial dependencies (e.g. depend on `a,b` and write to `a` twice before `b`)

The wire value can be directly accessed using the special node `%`. 

The "unglom" node can be used to assign labels into the current scope from the wire value.
```
@{1,2} -> !{foo, bar} -> ...
```

Forkpoints are a syntax sugar which simplifies sending the wire value to multiple children, e.g.
```
a ->
    |-> b
    |-> c -> 
        |-> d
        |-> e;  
    |-> f;
```
`a` is sent to `b,c,f`, `c` is sent to `d,e` 

### A more detailed study of blocks
#### the basics
Blocks are near equal in importance to the wire operator in providing expressivity to wence. Blocks are first class objects, and can either be invoked inline (executing immediately when all dependancies become available) or passed along the wire to subsequent nodes as a value. Invoking a block uses the `~` character. 

```
... -> { /* do stuff */ } -> #{foo}
```
Code elsewhere could depend on foo and invoke the block when needed:
```
#{foo} -> { 
    /* do stuff */
    ... -> ~foo -> ...
}
```
Blocks encapsulate their scope at declaration time (analogous to closures). This is useful for situations where you want to compute a value once and use it repeatedly. 
```
#{bar} -> {
    bar -> ...
} -> baz;

#{baz} -> ~{
    1 -> ~baz;
    2 -> ~baz;
}
```
Naturally, this same language feature can be used for block dependencies (analagous to named functions)
```
#{foo, bar} -> {
    ~foo;
    ~bar;
} -> #{baz}

{ ... } -> #{foo}
{ ... } -> #{bar}

#{baz} -> ~{
    ~baz;
}
```
Unglom can be used to implement block arguments

```
... -> {
    !{argA, argB, ...} -> /* do stuff */
} -> ... 
```

Blocks can also access themselves via the special node `_`. This is useful for certain recursive constructions, e.g. loop from 0 to 10 and print:
```
@{0} -> ~{
    !{i} -> @{_} -> !{r} -> ?{
        (i>10) : { }
        (1)    : { (i+1) -> |-> ~r
                            |-> #{stdout};     
                 }
    }
}
Note that `@{_}` is a nesseccary syntax for utilizing `_` as a this-accessor in the middle of a wire, as otherwise `-> _` would be interpreted as a yield.

```
#### yielding
Blocks can yield a value by sinking to `_`:
```
{ 1 -> _; } -> !{foo} -> ~{
    ~foo -> #{stdout};
}
```
As a block can have multiple dependant nodes, particularly valuized blocks or in the case of recursion, yielding a value can cause multiple wires to resume execution. Consider the following example:
```
@{0} -> ~{
    !{i} -> @{_} -> !{r} -> ?{
        (0) : { 1 -> ~r -> #{foo}; }
        (1) : { 2 -> _; }
    } -> #{bar};
}
```
This simple state machine recurses on the outermost block. When it yields a value in the second condition, both original dependant of the block (bar) and the variable dependant (foo) will receive the value. This behavior means you do not need to "bubble up" values in recursive constructions. In fact, what we have been calling recursion is perhaps more accurately conceptualized as a loop.

If a block does not yeild a value, it's dependants simply do not execute.

A block can yeild values multiple times. Consider this more contrived version of the "loop from 1 to 10" example from earlier:
```
@{0} -> ~{
    !{i} -> @{_} -> !{r} -> ?{
        (i<10) : {
            (i+1) -> |-> ~r
                     |-> _; 
        },
        (1)    : {
            i -> _;
        }
    } -> _;
} -> #{stdout}
```


 
#### Advanced scope manipulation
Writing to a variable containing a block allows for overriding / extending the scope encapsulated by that block. The variable itself is not modified, and the concatenated block object is forwarded on the wire. Note this allows for the creation of blocks which access variables that do not exist in scope at declaration time, so long as all invokers wrap them with all neccessary dependancies.
```
#{stdlib} -> {
    @{1} -> ~{ !{bar} ->
        {
            bar -> #{stdout};
        } -> _;
    } -> #{foo};

    #{foo} -> ~{
        ~foo; //prints 1
        @{2} -> !{bar} -> foo -> ~%; //prints 2
   };
}
```

### Summary
Yielding and scope manipulation provide enable rich metaprogramming-esque constructions. For example, multiple yields can be used to construct a generator-esque block, as we did above. Scope overriding can be used to manipulate code flow by replacing blocks used by an invokee. Wence currently lacks a mechanism to "lift" scope from a block instance, for example in order to enable decorator style block wrapping, but one will likely be added soon. 

Exploring these constructions, and the algorithmic space carved out by wence's unusual design, is the ultimate purpose of this project. Wence is a "toy" language in the purest sense of the term. It is meant to delight and enlighten, to bewilder, not in the hostile way of a traditional esolang, but as a puzzle. 

If wence interests you, please contact me on discord @numbers ! I get alot of bot friend requests, so please send a message request mentioning this project!



### Misc 

TODO document:

Data types: Int, String, Array, Dictionary





