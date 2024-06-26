```
'hello world' -> #{stdout};
```
### Hello World

Wence is an experimental dataflow oriented programming language currently in the early prototyping stage, developed as a toy and learning project by numbers.

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
The current wire context (scope and value array) can be written into the wire by using a glom node and restored using the lift operator `^` 
```
@{1,2,3} -> { 
    @{%} -> !{args} -> ... -> ^args -> //wire value is now [1,2,3]
}
```
This is explored in more detail later in the document. 

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
```
Note that `@{_}` is a nesseccary syntax for utilizing `_` as a this-accessor in the middle of a wire, as otherwise `-> _` would be interpreted as a yield.

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


 
#### Advanced scope considerations
Wence can be thought of as having two scopes, the encapsulated scope of the current block, and the ongoing wire scope of the execution. Wire scope is checked before encapsulated scope, allowing the invoker to override names which will then be accessed by the invokee. 
```
#{stdlib} -> {
    @{1} -> ~{ !{bar} ->
        {
            bar -> #{stdout};
        } -> _;
    } -> #{foo};

    #{foo} -> ~{
        ~foo; //prints 1
        @{2} -> !{bar} -> ~foo; //prints 2
   };
}
```
 Note this enables using blocks which access variables that do not exist in their encapsulated scope, so long as all invokers wrap them with all neccessary dependancies. Accessing a name which is not currently in scope is a runtime error.

Note that as side effect of Wence's scope flexibility an invoker may inadvertently override encapsulated values in an invokee. This can be avoided by careful consideration of namespace asignment, and certain compile-time and runtime debug helpers will eventually be provided to introspect this scenario.

Blocks which may be invoked repeatedly can update their encapsulated scope. This "make counter" example takes an integer and returns a block. Invoking that block takes an integer and adds it to a running total, returning the new total. Separate invokations of make_counter return blocks that manage different running totals.
```
{
   !{n} -> { !{i} -> @{(i+n)} -> !{n} -> _; } -> _;
} -> make_counter


```



#### The lift operator and scopes
The lift operator `^` can be used on a block or stored wire context, concatenating the scope of the target into the wire scope. This can be used to access variables as encapsulated on a block, or to save and restore scope for more complex constructions. 

When lifting a block, no change is made to the wire value.
When lifting a stored wire context, the wire value is replaced completely.
In both cases, the stored scope is concatenated to the wire scope, adding any new names and overriding existing ones.

Consider the following example of a "decorator" style construction, which takes a block and returns a block which calls it, wrapping `baz` if it is called by the target block. 
```
#{stdlib} -> {
    {(%) -> _;} -> !{baz} -> ~{
        { % -> ~baz -> _ } -> _;
    } -> #{foo};

    {
        !{block, wrapper} -> ~{ ^block -> @{baz} -> _ } -> !{tgt} -> {
            @{%} -> !{args} -> {
                % -> ~wrapper -> ~tgt -> _;
            } -> !{baz} -> ^args -> ~block -> _;
        } -> _;
    } -> #{wrap};

    {
        (%+1)->_;
    } -> #{wrapper};
                
    #{foo, wrap, wrapper} -> @{foo, wrapper} -> ~wrap -> #{wrapped};

    #{foo, wrapped} -> ~{
        1 -> ~foo -> #{stdout};
        1 -> ~wrapped -> #{stdout};
    }
}
```



### Closing Remarks

Exploring the algorithmic space carved out by wence's unusual design is the ultimate purpose of this project. Wence is a "toy" language in the purest sense of the term. It is meant to delight and enlighten, to bewilder, not in the hostile way of a traditional esolang, but as a puzzle. 

If wence interests you, please contact me on discord @numbers ! I get alot of bot friend requests, so please send a message request mentioning this project!



### Misc 

TODO document:

Data types: Int, String, Array, Dictionary

#### Vague notes:
Wence semantics are intented to be as generalized as possible. E.g., a node's semantic behavior should not care if it has some special structural positioning (e.g. at the beginning of a wire or block).



