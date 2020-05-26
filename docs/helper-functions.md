Helper Functions
================

In addition to the primary [`tokenize()`](usage.html) entry-point, the
`tokenize` module has several additional helper functions.

## `untokenize(iterable)`

Converts an iterable of tokens into a bytes string. The string is encoded
using the encoding of the [`ENCODING`](tokens.html#encoding) token. If there
is no `ENCODING` token present, the string is returned decoded (a `str`
instead of `bytes`). The iterable can be `TokenInfo` objects, or tuples of
`(TOKEN_TYPE, TOKEN_STRING)`.

This function always round-trips in one direction, namely,
`tokenize(io.BytesIO(untokenize(tokens)).readline)` will always return the
same tokens.

If full `TokenInfo` tuples are given with correct `start` and `end`
information (iterable of 5-tuples), this function also round-trips in the
other direction, for the most part (it assumes space characters between
tokens). However, be aware that the `start` and `end` tuples must be
nondecreasing. If the `start` of one token is before the `end` of the previous
token, it raises `ValueError`. Therefore, if you want to modify tokens and use
`untokenize()` to convert back to a string, using full 5-tuples, you must keep
track of and maintain the line and column information in `start` and `end`.

```py
>>> import tokenize
>>> import io
>>> string = b'sum([[1, 2]][0])'
>>> tokenize.untokenize(tokenize.tokenize(io.BytesIO(string).readline))
b'sum([[1, 2]][0])'
```

If only the token type and token names are given (iterable of 2-tuples),
`untokenize()` does not round-trip, and in fact, for any nontrivial input, the
resulting bytes string will be very different than the original input. This is
because `untokenize()` adds spaces after certain tokens to ensure the
resulting string is syntactically valid (or rather, to ensure that it
tokenizes back in the same way).

```py
>>> tokenize.untokenize([(i, j) for (i, j, _, _, _) in tokenize.tokenize(io.BytesIO(string).readline)])
b'sum ([[1 ,2 ]][0 ])'
```

2-tuples and 5-tuples can be mixed (for instance, you can add new tokens to a
list of `TokenInfo` objects using only 2-tuples), but in this case, it will
ignore the column information for the 5-tuples.

Consider this simple example which replaces all [`STRING`](tokens.html#string)
tokens with a list of [`STRING`](tokens.html#string) tokens of individual
characters (making use of implicit string concatenation). Once `untokenize()`
encounters the newly added 2-tuple tokens, it ignores the column information
and uses its own spacing.

```py
>>> import ast
>>> def split_string(s):
...     """
...     Split string tokens into constituent characters
...     """
...     new_tokens = []
...     for toknum, tokstr, start, end, line in tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline):
...         if toknum == tokenize.STRING:
...             for char in ast.literal_eval(tokstr):
...                 new_tokens.append((toknum, repr(char)))
...         else:
...             new_tokens.append((toknum, tokstr, start, end, line))
...     return tokenize.untokenize(new_tokens).decode('utf-8')
>>> split_string("print('hello ') and print('world')")
"print('h' 'e' 'l' 'l' 'o' ' ')and print ('w' 'o' 'r' 'l' 'd')"
```

If you want to use the `tokenize` module to extend the Python language
injecting or modifying tokens in a token stream, then using `exec` or `eval`
to convert the resulting source into executable code, and you do not care what
the code itself looks like, you can simply pass this function tuples of
`(TOKEN_TYPE, TOKEN_STRING)` and it will work fine. However, if your end goal
is to translate code in a human-readable way, you must keep track of line and
column information near the tokens you modify. The `tokenize` module does not
provide any tools to help with this.

## `detect_encoding(readline)`

The [official
docs](https://docs.python.org/3/library/tokenize.html#tokenize.detect_encoding)
for this function are helpful. This is the function used by `tokenize()` to
generate the [`ENCODING`](tokens.html#encoding) token. It can be used separately to
determine the encoding of some Python code. The calling syntax is the [same as
for `tokenize()`](usage.html#calling-syntax).

Returns a tuple of the encoding, and a list of any lines (in bytes) that it
has read from the function (it will read at most two lines from the file).
Invalid encodings will cause it to raise a
[`SyntaxError`](usage.html#syntaxerror).

```py
>>> tokenize.detect_encoding(io.BytesIO(b'# -*- coding: ascii -*-').readline)
('ascii', [b'# -*- coding: ascii -*-'])
```

This function should be used to detect the encoding of a Python source file
before opening it in text mode. For example

```py
with open('file.py', 'br') as f:
    encoding, _ = tokenize.detect_encoding(f.readline)

with open('file.py', encoding=encoding) as f:
    ...
```

Otherwise, the text read from the file may not be parsable as Python. For
example, `ast.parse` may fail if text from the file is read with the wrong
encoding. For example, if a file starts with a [Unicode BOM
character](https://en.wikipedia.org/wiki/Byte_order_mark), `ast.parse` will
fail if the file is not opened with the proper encoding.

## `tokenize.open(filename)`

This is an alternative to the built-in `open()` function that automatically
opens a Python file in text mode with the correct encoding, as detected by
[`detect_encoding()`](#detect-encoding-readline).

This function is not particularly useful in conjunction with the `tokenize()`
function (remember that `tokenize()` requires opening a file in binary mode,
whereas this function opens it in text mode). Rather, this is a function that
uses the functionality of the `tokenize` module, in particular,
`detect_encoding()`, to provide a higher level task that would be difficult to
do otherwise (opening a Python source file in text mode using the syntactically
correct encoding).

## Command Line Usage

The `tokenize` module can be called from the command line using `python -m
tokenize filename.py`. This prints three columns, representing the start-end
line and column positions, the token type, and the token string. If the `-e`
flag is used, the token type for operators is the exact type. Otherwise the
[`OP`](tokens.html#op) type is used.

```bash
$ python -m tokenize example.py
0,0-0,0:            ENCODING       'utf-8'
1,0-1,43:           COMMENT        '# This is a an example file to be tokenized'
1,43-1,44:          NL             '\n'
2,0-2,1:            NL             '\n'
3,0-3,3:            NAME           'def'
3,4-3,7:            NAME           'two'
3,7-3,8:            OP             '('
3,8-3,9:            OP             ')'
3,9-3,10:           OP             ':'
3,10-3,11:          NEWLINE        '\n'
4,0-4,4:            INDENT         '    '
4,4-4,10:           NAME           'return'
4,11-4,12:          NUMBER         '1'
4,13-4,14:          OP             '+'
4,15-4,16:          NUMBER         '1'
4,16-4,17:          NEWLINE        '\n'
5,0-5,0:            DEDENT         ''
5,0-5,0:            ENDMARKER      ''
$ python -m tokenize -e example.py
0,0-0,0:            ENCODING       'utf-8'
1,0-1,43:           COMMENT        '# This is a an example file to be tokenized'
1,43-1,44:          NL             '\n'
2,0-2,1:            NL             '\n'
3,0-3,3:            NAME           'def'
3,4-3,7:            NAME           'two'
3,7-3,8:            LPAR           '('
3,8-3,9:            RPAR           ')'
3,9-3,10:           COLON          ':'
3,10-3,11:          NEWLINE        '\n'
4,0-4,4:            INDENT         '    '
4,4-4,10:           NAME           'return'
4,11-4,12:          NUMBER         '1'
4,13-4,14:          PLUS           '+'
4,15-4,16:          NUMBER         '1'
4,16-4,17:          NEWLINE        '\n'
5,0-5,0:            DEDENT         ''
5,0-5,0:            ENDMARKER      ''
```
## Helper Functions Related to the `parser` Module

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
[`NT_OFFSET`](#nt-offset). You can see the list of nonterminal nodes
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
>>> pprint.pprint(pretty(st)) # doctest: +SKIP35, +SKIP36, +SKIP37
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
                  ['namedexpr_test',
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
                                 ['atom', ['STRING', '"a"']]]]]]]]]]]]]]]]]],
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
>>> ast.dump(ast.parse('("a") + True')) # doctest: +SKIP38
"Module(body=[Expr(value=BinOp(left=Str(s='a'), op=Add(), right=NameConstant(value=True)))])"
```

The following are included in the `token` module, but aren't particularly
useful outside of the `parser` module.

### `NT_OFFSET`

The greatest possible terminal token number. This is not useful unless you
intend to use the `parser` module. `tokenize()` never emits this token. Even
if you are using the `parser` module, you would generally use one of the
functions below instead of this token type. The current value of this constant
is 256.

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
