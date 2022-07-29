
import sys

from parse import Parser;

#src = '{"hello world"->|;}->main;~main;
src = '{ "hello world" -> (a * 2) -> ~b -> {c,d;} -> |; } -> main; ~main;'
#src = 'a -> b -> c;'


p = Parser("{" + src + "}");
z = p.parse();


print(src);
print(z);

print(z.graph());

