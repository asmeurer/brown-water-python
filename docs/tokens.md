The Token Types
===============

Every token produced by the tokenizer has a type. These types are represented
by integer constants. The actual integer value of the token constants should
never be used or relied on. Instead, refer to tokens by its variable name, and
use the `tok_name` dictionary to go from get the name of a token type. The
integer value could change between Python versions, for instance, if new
tokens are added or removed.

The reason the token types are represented this way is that the true tokenizer
for Python is written in C. C does not have an object system like Python.
Instead, enumerated types are represented by integers (actually, `tokenizer.c`
has a large array of the token types. The integer value of each token is its
index in that array). The `tokenize` module is written in pure Python, but the
token type values and names mirror those from the C tokenizer, with three
exceptions: `COMMENT`, `NL`, and `ENCODING`.

All token types are defined in the `token` module, but the `tokenize` module
does `from token import *`. Therefore, it is easiest to just import everything
from `tokenize`. Furthermore, the aforementioned `COMMENT`, `NL`, and
`ENCODING` tokens are not importable from `token` prior to Python 3.7, only
from `tokenize`.

## The `tok_name` Dictionary

The dictionary `tok_name` maps the tokens back to their names:

```py
>>> import tokenize
>>> tokenize.STRING
3
>>> tokenize.tok_name[tokenize.STRING] # Can also use token.tok_name
'STRING'
```

## Additional helper functions

The `token` and `tokenize` module mimick the modules in the C parser. Some
additional helper functions are included, even though they are mostly useless
outside of the C parser.

For some context, the Python
[grammar](https://docs.python.org/3/reference/grammar.html), contains
*terminal* and *nonterminal* nodes. The terminal nodes are the ones that stop
the parsing (they are leaf nodes, that is, no other node in the grammar can be
contained in them). These nodes are represented in uppercase. Every terminal
node in the grammar is a token type, for example, `NAME`, `NUMBER`, or
`STRING`. Not all token types are terminal nodes. The C parser re-uses the
tokenize node types when it constructs the AST. Nonterminal nodes are
represented by numbers greater than `NT_OFFSET`, which is currently 256. You
can see the list of nonterminal nodes in the
[`graminit.h`](https://github.com/python/cpython/blob/master/Include/graminit.h)
file.

The following functions are included in the `token` module, but aren't likely
useful outside of the Python C parser.

### `ISTERMINAL(x)`

`ISTERMINAL(x)` returns `True` is `x` is a terminal token type. It is
equivalent to `x < NT_OFFSET`. Every token in the `token` module (except for
`NT_OFFSET`) is a terminal node.

### `ISNONTERMINAL(x)`

`ISNONTERMINAL(x)` returns `True` if `x` is a nonterminal token type. It is
equivalent to `x >= NT_OFFSET`. The only nonterminal "token" in the `token`
module is `NT_OFFSET` itself.

### `ISEOF(x)`

`ISEOF(x)` returns true if `x` is the end of input marker token type. It is
equivalent to `x == ENDMARKER`.
