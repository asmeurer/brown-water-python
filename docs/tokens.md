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

## The tokens

To simplify the below sections, the following utility function is used for all
the examples:

```py
>>> import io
>>> def print_tokens(s):
...     for i in tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline):
...         print(i)

```

### `ENDMARKER`

This is always the last token emitted by `tokenize()`, unless it raises an
exception. The `string` and `line` are always `''`. For most applications it
is not necessary to explicitly worry about `ENDMARKER` because `tokenize()`
stops iteration after the last token is yielded.

```py
>>> print_tokens('x + 1')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='x', start=(1, 0), end=(1, 1), line='x + 1')
TokenInfo(type=53 (OP), string='+', start=(1, 2), end=(1, 3), line='x + 1')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 4), end=(1, 5), line='x + 1')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

```py
>>> print_tokens('')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(1, 0), end=(1, 0), line='')

```

### `NAME`

The `NAME` token type is used for any Python identifier, as well as every keyword. *keywords* are Python syntactic elements that consist only of alphabetic
characters, such as `for`, `def` and `True`. To tell if a `NAME` token is a
keyword, use
[`keyword.iskeyword()`](https://docs.python.org/3/library/keyword.html#keyword.iskeyword).

As a side note, internally, the `tokenize` module uses the
[`str.isidentifier()`](https://docs.python.org/3/library/stdtypes.html#str.isidentifier)
method to test if a token should be a `NAME` token. The full rules for what
makes a [valid
identifier](https://docs.python.org/3/reference/lexical_analysis.html?highlight=identifiers#identifiers)
are somewhat complicated, as they involve a large table of [Unicode
characters](https://www.dcl.hpi.uni-potsdam.de/home/loewis/table-3131.html).
One should always use the `str.isidentifier()` method to test if a string is a
valid Python identifier, combined with a `keyword.iskeyword()` check. Testing
if a string is an identifier using regular expressions is generally
discouraged.

```py
>>> print_tokens('a or α')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='a', start=(1, 0), end=(1, 1), line='a or α')
TokenInfo(type=1 (NAME), string='or', start=(1, 2), end=(1, 4), line='a or α')
TokenInfo(type=1 (NAME), string='α', start=(1, 5), end=(1, 6), line='a or α')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

```py
>>> import keyword
>>> keyword.iskeyword('or')
True

```

```py
>>> 'α'.isidentifier()
True
>>> 'or'.isidentifier()
True

```

### `NUMBER`

### `STRING`

### `NEWLINE`

### `INDENT`

### `DEDENT`

### `RARROW`

### `ELLIPSIS`

### `OP`

`OP` is a generic token type for all operations, delimiters, and the ellipsis
literal. This does not include characters that are not recognized by the
parser (these are parsed as `ERRORTOKEN`).

When using `tokenize`, the token type for an operation, delimiter, or ellipsis
literal token will be `OP`. To get the exact token type, use the `exact_type`
property of the namedtuple. `exact_type` is equivalent to `type` for the
remaining token types.

```py
>>> import io
>>> for i in tokenize.tokenize(io.BytesIO(b'[1+2]').readline):
...     print(tokenize.tok_name[i.type], repr(i.string))
ENCODING 'utf-8'
OP '['
NUMBER '1'
OP '+'
NUMBER '2'
OP ']'
ENDMARKER ''
>>> for i in tokenize.tokenize(io.BytesIO(b'[1+2]').readline):
...     print(tokenize.tok_name[i.exact_type], repr(i.string))
ENCODING 'utf-8'
LSQB '['
NUMBER '1'
PLUS '+'
NUMBER '2'
RSQB ']'
ENDMARKER ''

```

The following table lists all exact `OP` types and their corresponding
characters.

<!-- The table below is generated with exact_type_table.py -->

<!-- ```eval_rst -->

<!-- .. include:: exact_type_table.txt -->
<!-- ``` -->

### `AWAIT`

### `ASYNC`

### `ERRORTOKEN`

### `COMMENT`

### `NL`

### `ENCODING`

### `NT_OFFSET`


## Additional helper functions

The `token` and `tokenize` module mimic the modules in the C parser. Some
additional helper functions are included, even though they are mostly useless
outside of the C parser.

For some context, the Python
[grammar](https://docs.python.org/3/reference/grammar.html) contains
*terminal* and *nonterminal* nodes. The terminal nodes are the ones that stop
the parsing (they are leaf nodes, that is, no other node in the grammar can be
contained in them). These nodes are represented in uppercase. Every terminal
node in the grammar is a token type, for example, `NAME`, `NUMBER`, or
`STRING`. Most terminal nodes in the [grammar
file](https://github.com/python/cpython/blob/master/Grammar/Grammar) are
represented by their string value (for instance, the grammar references `'('`
instead of `LPAR`). The C parser re-uses the tokenize node types when it
constructs its internal parse tree. Nonterminal nodes are represented by numbers greater than
`NT_OFFSET`, which is currently 256. You can see the list of nonterminal nodes
in the
[`graminit.h`](https://github.com/python/cpython/blob/master/Include/graminit.h)
file, or by using the
[`symbol`](https://docs.python.org/3/library/symbol.html) module.

The [`parser`](https://docs.python.org/3/library/parser.html) module can be
used from within Python to access the parse tree. The `parser` and `symbol`
modules aren't discussed further in this guide because the `tokenize` and
`ast` modules are generally preferable for almost all use-cases (see the
[alternatives](alternatives.html) section). In particular, the `parser` module
has all the same limitations as the `ast` module (it requires complete,
syntactically valid Python code), but is much more difficult to work with. The
`parser` module exists mainly as a relic from before the `ast` module existed
in the standard library (`ast` was introduced in Python 2.5).

The following example gives an idea of what the `parser` syntax trees look
like for the code `("a") + True`.

```py
>>> import parser
>>> import pprint
>>> import token
>>> import symbol
>>> def pretty(st):
...     l = st.tolist()
...
...     def toname(t):
...         for i, val in enumerate(t[:]):
...             if isinstance(val, int):
...                 if token.ISTERMINAL(t[0]):
...                     t[i] = token.tok_name[val]
...                 else:
...                     t[i] = symbol.sym_name[val]
...             if isinstance(val, list):
...                 toname(t[i])
...
...     toname(l)
...     return l
>>> st = parser.expr('("a") + True')
>>> pprint.pprint(pretty(st))
['eval_input',
 ['testlist',
  ['test',
   ['or_test',
    ['and_test',
     ['not_test',
      ['comparison',
       ['expr',
        ['xor_expr',
         ['and_expr',
          ['shift_expr',
           ['arith_expr',
            ['term',
             ['factor',
              ['power',
               ['atom_expr',
                ['atom',
                 ['LPAR', '('],
                 ['testlist_comp',
                  ['test',
                   ['or_test',
                    ['and_test',
                     ['not_test',
                      ['comparison',
                       ['expr',
                        ['xor_expr',
                         ['and_expr',
                          ['shift_expr',
                           ['arith_expr',
                            ['term',
                             ['factor',
                              ['power',
                               ['atom_expr',
                                ['atom', ['STRING', '"a"']]]]]]]]]]]]]]]]],
                 ['RPAR', ')']]]]]],
            ['PLUS', '+'],
            ['term',
             ['factor',
              ['power', ['atom_expr', ['atom', ['NAME', 'True']]]]]]]]]]]]]]]]],
 ['NEWLINE', ''],
 ['ENDMARKER', '']]

```

Compare this to the `tokenize` representation seen in the [intro](intro.html),
or the `ast` representation:

```py
>>> import ast
>>> ast.dump(ast.parse('("a") + True'))
"Module(body=[Expr(value=BinOp(left=Str(s='a'), op=Add(), right=NameConstant(value=True)))])"

```

The following functions are included in the `token` module, but aren't
particularly useful outside of the `parser` module.

### `ISTERMINAL(x)`

`ISTERMINAL(x)` returns `True` is `x` is a terminal token type. It is
equivalent to `x < NT_OFFSET`. Every token in the `token` module (except for
`NT_OFFSET`) is a terminal node. It returns `False` for every token in the
`symbol` module.

### `ISNONTERMINAL(x)`

`ISNONTERMINAL(x)` returns `True` if `x` is a nonterminal token type. It is
equivalent to `x >= NT_OFFSET`. The only nonterminal "token" in the `token`
module is `NT_OFFSET` itself. It returns `True` for every token in the
`symbol` module.

### `ISEOF(x)`

`ISEOF(x)` returns true if `x` is the end of input marker token type. It is
equivalent to `x == ENDMARKER`. This is also mostly useless, as the
`tokenize()` function ends iteration after it emits this token.
