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

The `NUMBER` token type is used for any numeric literal, including (decimal) integer literals,
binary, octal, and hexidecimal integer literals, floating point numbers
(including scientific notation), and imaginary number literals (like `1j`).

```py
>>> print_tokens('10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='10', start=(1, 0), end=(1, 2), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='+', start=(1, 3), end=(1, 4), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='0b101', start=(1, 5), end=(1, 10), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='+', start=(1, 11), end=(1, 12), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='0o10', start=(1, 13), end=(1, 17), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='+', start=(1, 18), end=(1, 19), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='0xa', start=(1, 20), end=(1, 23), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='-', start=(1, 24), end=(1, 25), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='1.0', start=(1, 26), end=(1, 29), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='+', start=(1, 30), end=(1, 31), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='1e1', start=(1, 32), end=(1, 35), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=53 (OP), string='+', start=(1, 36), end=(1, 37), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=2 (NUMBER), string='1j', start=(1, 38), end=(1, 40), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

Note that even though literals like `1+2j` are a single `complex` type, they
tokenize as `NUMBER` (`1`), `OP` (`+`), `NUMBER` (`2j`).

```py
>>> print_tokens('1+2j')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 0), end=(1, 1), line='1+2j')
TokenInfo(type=53 (OP), string='+', start=(1, 1), end=(1, 2), line='1+2j')
TokenInfo(type=2 (NUMBER), string='2j', start=(1, 2), end=(1, 4), line='1+2j')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

Invalid numeric literals may tokenize as multiple numeric literals.

```py
>>> print_tokens('012')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0', start=(1, 0), end=(1, 1), line='012')
TokenInfo(type=2 (NUMBER), string='12', start=(1, 1), end=(1, 3), line='012')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens('0x1.0')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0x1', start=(1, 0), end=(1, 3), line='0x1.0')
TokenInfo(type=2 (NUMBER), string='.0', start=(1, 3), end=(1, 5), line='0x1.0')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens('0o184')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0o1', start=(1, 0), end=(1, 3), line='0o184')
TokenInfo(type=2 (NUMBER), string='84', start=(1, 3), end=(1, 5), line='0o184')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

One advantage of using `tokenize` over `ast` is that floating point numbers
are not rounded at the tokenization stage, so it is possible to access the
full input. This can be used, for instance, to wrap floating point numbers
with a type that supports arbitrary precision, such as `decimal.Decimal`. See
the [example](https://docs.python.org/3/library/tokenize.html#examples) in the
official `tokenize` documentation.

```py
>>> 1.0000000000000001
1.0
>>> print_tokens('1.0000000000000001')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1.0000000000000001', start=(1, 0), end=(1, 18), line='1.0000000000000001')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> import ast
>>> ast.dump(ast.parse('1.0000000000000001'))
'Module(body=[Expr(value=Num(n=1.0))])'

```

In Python >=3.6, numeric literals can have [underscore
separators](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep515),
like `123_456`.

```py
>>> # Python 3.6+ only.
>>> print_tokens('123_456') # doctest: +SKIP
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='123_456', start=(1, 0), end=(1, 7), line='123_456')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

In Python 3.5, this will tokenize as two tokens, `NUMBER` (`123`) and `NAME` (`_456`).

```py
>>> # The behavior in Python 3.5
>>> print_tokens('123_456') # doctest: +SKIP
    TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
    TokenInfo(type=2 (NUMBER), string='123', start=(1, 0), end=(1, 3), line='123_456')
    TokenInfo(type=1 (NAME), string='_456', start=(1, 3), end=(1, 7), line='123_456')
    TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

### `STRING`

The `STRING` token type matches any string literal, including single quoted,
double quoted strings, triple- single and double quoted strings (i.e.,
docstrings), raw, "unicode", bytes, and f-strings (Python 3.6+).

```py
>>> print_tokens("""
... "I" + \'love\' + '''tokenize'''
... """)
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=58 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=3 (STRING), string='"I"', start=(2, 0), end=(2, 3), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=53 (OP), string='+', start=(2, 4), end=(2, 5), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=3 (STRING), string="'love'", start=(2, 6), end=(2, 12), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=53 (OP), string='+', start=(2, 13), end=(2, 14), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=3 (STRING), string="'''tokenize'''", start=(2, 15), end=(2, 29), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 29), end=(2, 30), line='"I" + \'love\' + \'\'\'tokenize\'\'\'\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(3, 0), end=(3, 0), line='')


```


Note that even though Python implicitly concatenates string literals,
`tokenize` tokenizes them separately.

```py
>>> print_tokens('"this is" " fun"')
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string='"this is"', start=(1, 0), end=(1, 9), line='"this is" " fun"')
TokenInfo(type=3 (STRING), string='" fun"', start=(1, 10), end=(1, 16), line='"this is" " fun"')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```


In the case of raw, "unicode", bytes, and f-strings, the string prefix is
included in the tokenized string.

```py
>>> print_tokens("rb'\hello'")
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="rb'\\hello'", start=(1, 0), end=(1, 10), line="rb'\\hello'")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

f-strings (Python 3.6+) are parsed as a single `STRING` token.

```py
>>> # Python 3.6+ only.
>>> print_tokens('f"{a + b}"') # doctest: +SKIP
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string='f"{a + b}"', start=(1, 0), end=(1, 10), line='f"{a + b}"')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

The `string.Format.parse()` function can be used to parse format strings
(including f-strings).

```py
>>> a = 1
>>> b = 2
>>> # f-strings are Python 3.6+ only
>>> f'a + b is {a + b!r}' # doctest: +SKIP
'a + b is 3'
>>> import string
>>> list(string.Formatter().parse('a + b is {a + b!r}'))
[('a + b is ', 'a + b', '', 'r')]

```

#### **Error behavior**

If a single quoted strings is unclosed, the opening string delimiter is
tokenized as `ERRORTOKEN`, and the remainder is tokenized as if it were not in
a string.

```py
>>> print_tokens("'unclosed + string")
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (ERRORTOKEN), string="'", start=(1, 0), end=(1, 1), line="'unclosed + string")
TokenInfo(type=1 (NAME), string='unclosed', start=(1, 1), end=(1, 9), line="'unclosed + string")
TokenInfo(type=53 (OP), string='+', start=(1, 10), end=(1, 11), line="'unclosed + string")
TokenInfo(type=1 (NAME), string='string', start=(1, 12), end=(1, 18), line="'unclosed + string")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

This behavior can be useful for handling error situations. For example, if you
were to build a syntax highlighter using `tokenize`, you might not necessarily
want an unclosed string to highlight the rest of the document as a string
(such things are common in "live" editing environments).

However, if a triple quoted string (i.e., multiline string, or docstring) is
not closed, `tokenize` will raise `TokenError` when it reaches it.

```py
>>> print_tokens("'an ' + '''unclosed multiline string") # doctest: +SKIP
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="'an '", start=(1, 0), end=(1, 5), line="'an ' + '''unclosed multiline string")
TokenInfo(type=53 (OP), string='+', start=(1, 6), end=(1, 7), line="'an ' + '''unclosed multiline string")
Traceback (most recent call last):
    ...
    raise TokenError("EOF in multi-line string", strstart)
tokenize.TokenError: ('EOF in multi-line string', (1, 8))

```

This behavior can be annoying to deal with in practice. For many applications,
the correct way to handle this scenario is to consider that since the unclosed
string is multiline, the remainder of the input from where the `TokenError` is
raised is inside the unclosed string.

As a final note, beware that it is possible to construct string literals that
tokenize without any errors, but raise SyntaxError when parsed by the
interpreter.

```py
>>> print_tokens(r"'\N{NOT REAL}'")
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="'\\N{NOT REAL}'", start=(1, 0), end=(1, 14), line="'\\N{NOT REAL}'")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> eval(r"'\N{NOT REAL}'")
Traceback (most recent call last):
  ...
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 0-11: unknown Unicode character name

```

To test if a string literal is valid, you can use the `ast.literal_eval()`
function, which is safe to use on untrusted input.

```py
>>> ast.literal_eval(r"'\N{NOT REAL}'")
Traceback (most recent call last):
  ...
SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 0-11: unknown Unicode character name

```

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
