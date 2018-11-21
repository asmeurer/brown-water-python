The Token Types
===============

Every token produced by the tokenizer has a type. These types are represented
by integer constants. The actual integer value of the token constants is not
important (except for [`N_TOKENS`](#n-tokens)), and should never be used or
relied on. Instead, refer to tokens by their variable names, and use the
`tok_name` dictionary to get the name of a token type. The exact integer value
could change between Python versions, for instance, if new tokens are added or
removed (and indeed, certain token integer values are different between Python
3.6 and 3.7 due to the [`ASYNC`](#async) and [`AWAIT`](#await) tokens being
removed). In the examples below, the token number shown in the output is the
number from Python 3.7 (except in the examples that do not run in Python 3.7).
I note this only for clarity: one should always use the token variable names
and never use the integer value of a token directly.

The reason the token types are represented this way is that the actual
tokenizer used by the Python interpreter is not the `tokenize` module; it is a
much more [efficient, but equivalent
implementation](https://github.com/python/cpython/blob/master/Parser/tokenizer.c)
written in C. C does not have an object system like Python. Instead,
enumerated types are represented by integers (actually, `tokenizer.c` has a
large array of the token types. The integer value of each token is its index
in that array). The `tokenize` module is written in pure Python, but the token
type values and names mirror those from the C tokenizer, with three
exceptions: [`COMMENT`](#comment), [`NL`](#nl), and [`ENCODING`](#nl).

All token types are defined in the `token` module, but the `tokenize` module
does `from token import *`, so they can be imported from `tokenize` as well.
Therefore, it is easiest to just import everything from `tokenize`.
Furthermore, the aforementioned [`COMMENT`](#nl), [`NL`](#nl), and
[`ENCODING`](#nl) tokens are not importable from `token` prior to Python 3.7,
only from `tokenize`.

## The `tok_name` Dictionary

The dictionary `tok_name` maps the tokens back to their names:

```py
>>> import tokenize
>>> tokenize.STRING
3
>>> tokenize.tok_name[tokenize.STRING] # Can also use token.tok_name
'STRING'
```

## The Tokens

To simplify the below sections, the following utility function is used for all
the examples:

```py
>>> import io
>>> def print_tokens(s):
...     for tok in tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline):
...         print(tok)
```

### `ENDMARKER`

This is always the last token emitted by `tokenize()`, unless it raises an
exception. The `string` and `line` attributes are always `''`. The `start` and
`end` lines are always one more than the total number of lines in the input,
and the `start` and `end` columns are always 0.

For most applications it is not necessary to explicitly worry about
`ENDMARKER`, because `tokenize()` stops iteration after the last token is
yielded.

```py
>>> print_tokens('x + 1\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='x', start=(1, 0), end=(1, 1), line='x + 1\n')
TokenInfo(type=53 (OP), string='+', start=(1, 2), end=(1, 3), line='x + 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 4), end=(1, 5), line='x + 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 5), end=(1, 6), line='x + 1\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

```py
>>> print_tokens('')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(1, 0), end=(1, 0), line='')
```

### `NAME`

The `NAME` token type is used for any Python identifier, as well as every
keyword.
[*Keywords*](https://docs.python.org/3/reference/lexical_analysis.html#keywords)
are Python names that are reserved, that is, they cannot be assigned to, such
as `for`, `def`, and `True`.


```py
>>> print_tokens('a or α\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='a', start=(1, 0), end=(1, 1), line='a or α\n')
TokenInfo(type=1 (NAME), string='or', start=(1, 2), end=(1, 4), line='a or α\n')
TokenInfo(type=1 (NAME), string='α', start=(1, 5), end=(1, 6), line='a or α\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 6), end=(1, 7), line='a or α\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

To tell if a `NAME` token is a keyword, use
[`keyword.iskeyword()`](https://docs.python.org/3/library/keyword.html#keyword.iskeyword)
on the `string`.

```py
>>> import keyword
>>> keyword.iskeyword('or')
True
```

As a side note, internally, the `tokenize` module uses the
[`str.isidentifier()`](https://docs.python.org/3/library/stdtypes.html#str.isidentifier)
method to test if a token should be a `NAME` token. The full rules for what
makes a [valid
identifier](https://docs.python.org/3/reference/lexical_analysis.html?highlight=identifiers#identifiers)
are somewhat complicated, as they involve a large table of [Unicode
characters](https://www.dcl.hpi.uni-potsdam.de/home/loewis/table-3131.html).
One should always use the `str.isidentifier()` method to test if a string is a
valid Python identifier, combined with a `keyword.iskeyword()` check. Testing
if a string is an identifier using regular expressions is highly
discouraged.

```py
>>> 'α'.isidentifier()
True
>>> 'or'.isidentifier()
True
```

### `NUMBER`

The `NUMBER` token type is used for any numeric literal, including (decimal) integer literals,
binary, octal, and hexadecimal integer literals, floating point numbers
(including scientific notation), and imaginary number literals (like `1j`).

```py
>>> print_tokens('10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='10', start=(1, 0), end=(1, 2), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 3), end=(1, 4), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='0b101', start=(1, 5), end=(1, 10), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 11), end=(1, 12), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='0o10', start=(1, 13), end=(1, 17), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 18), end=(1, 19), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='0xa', start=(1, 20), end=(1, 23), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='-', start=(1, 24), end=(1, 25), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='1.0', start=(1, 26), end=(1, 29), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 30), end=(1, 31), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='1e1', start=(1, 32), end=(1, 35), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 36), end=(1, 37), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=2 (NUMBER), string='1j', start=(1, 38), end=(1, 40), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 40), end=(1, 41), line='10 + 0b101 + 0o10 + 0xa - 1.0 + 1e1 + 1j\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

Note that even though literals like `1+2j` are a single `complex` type, they
tokenize as `NUMBER` (`1`), `OP` (`+`), `NUMBER` (`2j`).

```py
>>> print_tokens('1+2j\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 0), end=(1, 1), line='1+2j\n')
TokenInfo(type=53 (OP), string='+', start=(1, 1), end=(1, 2), line='1+2j\n')
TokenInfo(type=2 (NUMBER), string='2j', start=(1, 2), end=(1, 4), line='1+2j\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 4), end=(1, 5), line='1+2j\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

Invalid numeric literals may tokenize as multiple numeric literals.

```py
>>> print_tokens('012\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0', start=(1, 0), end=(1, 1), line='012\n')
TokenInfo(type=2 (NUMBER), string='12', start=(1, 1), end=(1, 3), line='012\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 3), end=(1, 4), line='012\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens('0x1.0\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0x1', start=(1, 0), end=(1, 3), line='0x1.0\n')
TokenInfo(type=2 (NUMBER), string='.0', start=(1, 3), end=(1, 5), line='0x1.0\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 5), end=(1, 6), line='0x1.0\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens('0o184\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='0o1', start=(1, 0), end=(1, 3), line='0o184\n')
TokenInfo(type=2 (NUMBER), string='84', start=(1, 3), end=(1, 5), line='0o184\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 5), end=(1, 6), line='0o184\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

One advantage of using `tokenize` over `ast` is that floating point numbers
are not rounded at the tokenization stage, so it is possible to access the
full input.

<!-- The ast doctest is skipped in Python 3.8 because it changes Num to Constant. -->
<!-- TODO: When 3.8 is released, change these to skip in 3.5-3.7. -->

```py
>>> 1.0000000000000001
1.0
>>> print_tokens('1.0000000000000001\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1.0000000000000001', start=(1, 0), end=(1, 18), line='1.0000000000000001\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 18), end=(1, 19), line='1.0000000000000001\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> import ast
>>> ast.dump(ast.parse('1.0000000000000001')) # doctest: +SKIP38
'Module(body=[Expr(value=Num(n=1.0))])'
```

This can be used, for instance, to wrap floating point numbers with a type
that supports arbitrary precision, such as
[`decimal.Decimal`](https://docs.python.org/3/library/decimal.html). See the
[examples](examples.html#wrapping-floats-with-decimal-decimal).

In Python >=3.6, numeric literals can have [underscore
separators](https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep515),
like `123_456`.

```py
>>> # Python 3.6+ only.
>>> print_tokens('123_456\n') # doctest: +SKIP35
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='123_456', start=(1, 0), end=(1, 7), line='123_456\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 7), end=(1, 8), line='123_456\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

In Python 3.5, this will tokenize as two tokens, `NUMBER` (`123`) and `NAME`
(`_456`) (and will not be syntactically valid in any context).

```py
>>> # The behavior in Python 3.5
>>> print_tokens('123_456\n') # doctest: +SKIP36 +SKIP37, +SKIP38
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='123', start=(1, 0), end=(1, 3), line='123_456\n')
TokenInfo(type=1 (NAME), string='_456', start=(1, 3), end=(1, 7), line='123_456\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 7), end=(1, 8), line='123_456\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

In the [examples](examples.html#backporting-underscores-in-numeric-literals)
we will see how to use `tokenize` to backport this feature to Python 3.5.

### `STRING`

The `STRING` token type matches any string literal, including single quoted,
double quoted strings, triple- single and double quoted strings (i.e.,
multi-line strings, or "docstrings"), raw, "unicode", bytes, and f-strings
(Python 3.6+).

```py
>>> print_tokens("""
... "I" + 'love' + '''tokenize'''
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
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
>>> print_tokens('"this is" " fun"\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string='"this is"', start=(1, 0), end=(1, 9), line='"this is" " fun"\n')
TokenInfo(type=3 (STRING), string='" fun"', start=(1, 10), end=(1, 16), line='"this is" " fun"\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 16), end=(1, 17), line='"this is" " fun"\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```


In the case of raw, "unicode", bytes, and f-strings, the string prefix is
included in the tokenized string.

```py
>>> print_tokens(r"rb'\hello'" + '\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="rb'\\hello'", start=(1, 0), end=(1, 10), line="rb'\\hello'\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 10), end=(1, 11), line="rb'\\hello'\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

f-strings (Python 3.6+) are parsed as a single `STRING` token.

```py
>>> # Python 3.6+ only.
>>> print_tokens('f"{a + b}"\n') # doctest: +SKIP35
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string='f"{a + b}"', start=(1, 0), end=(1, 10), line='f"{a + b}"\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 10), end=(1, 11), line='f"{a + b}"\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

The `string.Format.parse()` function can be used to parse format strings
(including f-strings).

```py
>>> a = 1
>>> b = 2
>>> # f-strings are Python 3.6+ only
>>> f'a + b is {a + b!r}' # doctest: +SKIP35
'a + b is 3'
>>> import string
>>> list(string.Formatter().parse('a + b is {a + b!r}'))
[('a + b is ', 'a + b', '', 'r')]
```

To get the string value from a tokenized string literal (i.e., to strip away
the quote characters), use `ast.literal_eval()`. This is recommended over
trying to strip the quotes manually, which is error prone, or using raw
`eval`, which can execute arbitrary code in the case of an f-string.

```py
>>> ast.literal_eval("rb'a\\''")
b"a\\'"
```

#### Error Behavior

If a single quoted string is unclosed, the opening string delimiter is
tokenized as [`ERRORTOKEN`](#errortoken), and the remainder is tokenized as if
it were not in a string.

```py
>>> print_tokens("'unclosed + string\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=54 (ERRORTOKEN), string="'", start=(1, 0), end=(1, 1), line="'unclosed + string\n")
TokenInfo(type=1 (NAME), string='unclosed', start=(1, 1), end=(1, 9), line="'unclosed + string\n")
TokenInfo(type=53 (OP), string='+', start=(1, 10), end=(1, 11), line="'unclosed + string\n")
TokenInfo(type=1 (NAME), string='string', start=(1, 12), end=(1, 18), line="'unclosed + string\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 18), end=(1, 19), line="'unclosed + string\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

This behavior can be useful for handling error situations. For example, if you
were to build a syntax highlighter using `tokenize`, you might not necessarily
want an unclosed string to highlight the rest of the document as a string
(such things are common in "live" editing environments).

However, if a triple quoted string (i.e., multi-line string, or "docstring")
is not closed, `tokenize` will raise [`TokenError`](usage.html#tokenerror)
when it reaches it.

```py
>>> print_tokens("'an ' + '''unclosed multi-line string\n") # doctest: +SKIP
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="'an '", start=(1, 0), end=(1, 5), line="'an ' + '''unclosed multi-line string\n")
TokenInfo(type=53 (OP), string='+', start=(1, 6), end=(1, 7), line="'an ' + '''unclosed multi-line string\n")
Traceback (most recent call last):
    ...
    raise TokenError("EOF in multi-line string", strstart)
tokenize.TokenError: ('EOF in multi-line string', (1, 8))
```

This behavior can be annoying to deal with in practice. For many applications,
the correct way to handle this scenario is to consider that since the unclosed
string is multi-line, the remainder of the input from where the
[`TokenError`](usage.html#tokenerror) is raised is inside the unclosed string.

As a final note, beware that it is possible to construct string literals that
tokenize without any errors, but raise `SyntaxError` when parsed by the
interpreter.

```py
>>> print_tokens(r"'\N{NOT REAL}'" + '\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="'\\N{NOT REAL}'", start=(1, 0), end=(1, 14), line="'\\N{NOT REAL}'\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 14), end=(1, 15), line="'\\N{NOT REAL}'\n")
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

The `NEWLINE` token type represents a newline character (`\n` or `\r\n`) that
ends a logical line of Python code. Newlines that do not end a logical line of
Python code use [`NL`](#nl).

```py
>>> print_tokens("""\
... def hello():
...     return 'hello world'
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='def', start=(1, 0), end=(1, 3), line='def hello():\n')
TokenInfo(type=1 (NAME), string='hello', start=(1, 4), end=(1, 9), line='def hello():\n')
TokenInfo(type=53 (OP), string='(', start=(1, 9), end=(1, 10), line='def hello():\n')
TokenInfo(type=53 (OP), string=')', start=(1, 10), end=(1, 11), line='def hello():\n')
TokenInfo(type=53 (OP), string=':', start=(1, 11), end=(1, 12), line='def hello():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 12), end=(1, 13), line='def hello():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(2, 0), end=(2, 4), line="    return 'hello world'\n")
TokenInfo(type=1 (NAME), string='return', start=(2, 4), end=(2, 10), line="    return 'hello world'\n")
TokenInfo(type=3 (STRING), string="'hello world'", start=(2, 11), end=(2, 24), line="    return 'hello world'\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 24), end=(2, 25), line="    return 'hello world'\n")
TokenInfo(type=6 (DEDENT), string='', start=(3, 0), end=(3, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(3, 0), end=(3, 0), line='')
```

Windows-style newlines (`\r\n`) are tokenized as a single token.

```py
>>> print_tokens("1\n2\r\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 0), end=(1, 1), line='1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 1), end=(1, 2), line='1\n')
TokenInfo(type=2 (NUMBER), string='2', start=(2, 0), end=(2, 1), line='2\r\n')
TokenInfo(type=4 (NEWLINE), string='\r\n', start=(2, 1), end=(2, 3), line='2\r\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(3, 0), end=(3, 0), line='')
```

Starting in Python 3.6.7 and 3.7.1, `NEWLINE` is emitted at the end of all
tokenize input even if it doesn't end in a newline (with the exception of
lines that are just comments). This change was made for consistency with the
internal tokenize.c module used by Python itself. Implicit `NEWLINE`s have the
`line` set to `''`. This change was not made to Python 3.5, which is already
in ["security fix
only"](https://devguide.python.org/#status-of-python-branches). The examples
in this document all use the 3.6.7+ behavior. If consistency is desired, one
can always force the input to end in a newline. This is why every example in
this file has a newline at the end.

### `INDENT`
### `DEDENT`

The `INDENT` token type represents the indentation for indented blocks. The
indentation itself (the text from the beginning of the line to the first
nonwhitespace character) is in the `string` attribute. `INDENT` is emitted
once per block of indented text, not once per line.

The `DEDENT` token type represents a dedentation. Every `INDENT` token is
matched by a corresponding `DEDENT` token. The `string` attribute of `DEDENT`
is always `''`. The `start` and `end` positions of a `DEDENT` token are the
first position in the line after the indentation (even if there are multiple
consecutive `DEDENT`s).

Consider the following pseudo-example:

```py
>>> print_tokens("""
... 1
...     2
...     3
...         4
... 5
...
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=2 (NUMBER), string='1', start=(2, 0), end=(2, 1), line='1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 1), end=(2, 2), line='1\n')
TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line='    2\n')
TokenInfo(type=2 (NUMBER), string='2', start=(3, 4), end=(3, 5), line='    2\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 5), end=(3, 6), line='    2\n')
TokenInfo(type=2 (NUMBER), string='3', start=(4, 4), end=(4, 5), line='    3\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 5), end=(4, 6), line='    3\n')
TokenInfo(type=5 (INDENT), string='        ', start=(5, 0), end=(5, 8), line='        4\n')
TokenInfo(type=2 (NUMBER), string='4', start=(5, 8), end=(5, 9), line='        4\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(5, 9), end=(5, 10), line='        4\n')
TokenInfo(type=6 (DEDENT), string='', start=(6, 0), end=(6, 0), line='5\n')
TokenInfo(type=6 (DEDENT), string='', start=(6, 0), end=(6, 0), line='5\n')
TokenInfo(type=2 (NUMBER), string='5', start=(6, 0), end=(6, 1), line='5\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(6, 1), end=(6, 2), line='5\n')
TokenInfo(type=56 (NL), string='\n', start=(7, 0), end=(7, 1), line='\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(8, 0), end=(8, 0), line='')
```

There is one `INDENT` before the `2-3` block, one `INDENT` before `4`, and two
`DEDENTS` before `5`

`INDENT` is not used for indentations on line continuations.

```py
>>> print_tokens("""
... (1 +
...     2)
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=53 (OP), string='(', start=(2, 0), end=(2, 1), line='(1 +\n')
TokenInfo(type=2 (NUMBER), string='1', start=(2, 1), end=(2, 2), line='(1 +\n')
TokenInfo(type=53 (OP), string='+', start=(2, 3), end=(2, 4), line='(1 +\n')
TokenInfo(type=56 (NL), string='\n', start=(2, 4), end=(2, 5), line='(1 +\n')
TokenInfo(type=2 (NUMBER), string='2', start=(3, 4), end=(3, 5), line='    2)\n')
TokenInfo(type=53 (OP), string=')', start=(3, 5), end=(3, 6), line='    2)\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 6), end=(3, 7), line='    2)\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(4, 0), end=(4, 0), line='')
```

Indentation can be any number of spaces or tabs. The only restriction is that
every unindented indentation level must match a previous outer indentation
level. If an unindent does not match an outer indentation level, `tokenize()`
raises [`IndentationError`](usage.html#indentationerror).

```py
>>> print_tokens("""
... def countdown(x):
... \tassert x>=0
... \twhile x:
... \t\tprint(x)
... \t\tx -= 1
... \tprint('Go!')
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='def', start=(2, 0), end=(2, 3), line='def countdown(x):\n')
TokenInfo(type=1 (NAME), string='countdown', start=(2, 4), end=(2, 13), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string='(', start=(2, 13), end=(2, 14), line='def countdown(x):\n')
TokenInfo(type=1 (NAME), string='x', start=(2, 14), end=(2, 15), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string=')', start=(2, 15), end=(2, 16), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string=':', start=(2, 16), end=(2, 17), line='def countdown(x):\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 17), end=(2, 18), line='def countdown(x):\n')
TokenInfo(type=5 (INDENT), string='\t', start=(3, 0), end=(3, 1), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='assert', start=(3, 1), end=(3, 7), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='x', start=(3, 8), end=(3, 9), line='\tassert x>=0\n')
TokenInfo(type=53 (OP), string='>=', start=(3, 9), end=(3, 11), line='\tassert x>=0\n')
TokenInfo(type=2 (NUMBER), string='0', start=(3, 11), end=(3, 12), line='\tassert x>=0\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 12), end=(3, 13), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='while', start=(4, 1), end=(4, 6), line='\twhile x:\n')
TokenInfo(type=1 (NAME), string='x', start=(4, 7), end=(4, 8), line='\twhile x:\n')
TokenInfo(type=53 (OP), string=':', start=(4, 8), end=(4, 9), line='\twhile x:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 9), end=(4, 10), line='\twhile x:\n')
TokenInfo(type=5 (INDENT), string='\t\t', start=(5, 0), end=(5, 2), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='print', start=(5, 2), end=(5, 7), line='\t\tprint(x)\n')
TokenInfo(type=53 (OP), string='(', start=(5, 7), end=(5, 8), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='x', start=(5, 8), end=(5, 9), line='\t\tprint(x)\n')
TokenInfo(type=53 (OP), string=')', start=(5, 9), end=(5, 10), line='\t\tprint(x)\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(5, 10), end=(5, 11), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='x', start=(6, 2), end=(6, 3), line='\t\tx -= 1\n')
TokenInfo(type=53 (OP), string='-=', start=(6, 4), end=(6, 6), line='\t\tx -= 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(6, 7), end=(6, 8), line='\t\tx -= 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(6, 8), end=(6, 9), line='\t\tx -= 1\n')
TokenInfo(type=6 (DEDENT), string='', start=(7, 1), end=(7, 1), line="\tprint('Go!')\n")
TokenInfo(type=1 (NAME), string='print', start=(7, 1), end=(7, 6), line="\tprint('Go!')\n")
TokenInfo(type=53 (OP), string='(', start=(7, 6), end=(7, 7), line="\tprint('Go!')\n")
TokenInfo(type=3 (STRING), string="'Go!'", start=(7, 7), end=(7, 12), line="\tprint('Go!')\n")
TokenInfo(type=53 (OP), string=')', start=(7, 12), end=(7, 13), line="\tprint('Go!')\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(7, 13), end=(7, 14), line="\tprint('Go!')\n")
TokenInfo(type=6 (DEDENT), string='', start=(8, 0), end=(8, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(8, 0), end=(8, 0), line='')
>>> print_tokens("""
... def countdown(x):
... \tassert x>=0
... \twhile x:
... \t\tprint(x)
... \t\tx -= 1
...     print('Go!')
... """) # doctest: +SKIP
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='def', start=(2, 0), end=(2, 3), line='def countdown(x):\n')
TokenInfo(type=1 (NAME), string='countdown', start=(2, 4), end=(2, 13), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string='(', start=(2, 13), end=(2, 14), line='def countdown(x):\n')
TokenInfo(type=1 (NAME), string='x', start=(2, 14), end=(2, 15), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string=')', start=(2, 15), end=(2, 16), line='def countdown(x):\n')
TokenInfo(type=53 (OP), string=':', start=(2, 16), end=(2, 17), line='def countdown(x):\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 17), end=(2, 18), line='def countdown(x):\n')
TokenInfo(type=5 (INDENT), string='\t', start=(3, 0), end=(3, 1), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='assert', start=(3, 1), end=(3, 7), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='x', start=(3, 8), end=(3, 9), line='\tassert x>=0\n')
TokenInfo(type=53 (OP), string='>=', start=(3, 9), end=(3, 11), line='\tassert x>=0\n')
TokenInfo(type=2 (NUMBER), string='0', start=(3, 11), end=(3, 12), line='\tassert x>=0\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 12), end=(3, 13), line='\tassert x>=0\n')
TokenInfo(type=1 (NAME), string='while', start=(4, 1), end=(4, 6), line='\twhile x:\n')
TokenInfo(type=1 (NAME), string='x', start=(4, 7), end=(4, 8), line='\twhile x:\n')
TokenInfo(type=53 (OP), string=':', start=(4, 8), end=(4, 9), line='\twhile x:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 9), end=(4, 10), line='\twhile x:\n')
TokenInfo(type=5 (INDENT), string='\t\t', start=(5, 0), end=(5, 2), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='print', start=(5, 2), end=(5, 7), line='\t\tprint(x)\n')
TokenInfo(type=53 (OP), string='(', start=(5, 7), end=(5, 8), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='x', start=(5, 8), end=(5, 9), line='\t\tprint(x)\n')
TokenInfo(type=53 (OP), string=')', start=(5, 9), end=(5, 10), line='\t\tprint(x)\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(5, 10), end=(5, 11), line='\t\tprint(x)\n')
TokenInfo(type=1 (NAME), string='x', start=(6, 2), end=(6, 3), line='\t\tx -= 1\n')
TokenInfo(type=53 (OP), string='-=', start=(6, 4), end=(6, 6), line='\t\tx -= 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(6, 7), end=(6, 8), line='\t\tx -= 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(6, 8), end=(6, 9), line='\t\tx -= 1\n')
Traceback (most recent call last):
  ...
    print('Go!')
    ^
IndentationError: unindent does not match any outer indentation level
```

The level of indentation at a particular point in the token stream can be
determined by incrementing and decrementing a counter for each `INDENT` and
`DEDENT` token. See the [examples](examples.html#indentation-level).



### `RARROW`
### `ELLIPSIS`

The `RARROW` and `ELLIPSIS` tokens tokenize as [`OP`](#op). However, due to a
[bug](https://bugs.python.org/issue24622) present in Python versions prior to
3.7, the `exact_type` attribute of these tokens will be `OP` instead of the
correct type.


```py
>>> # Python 3.5 and 3.6 behavior
>>> for tok in tokenize.tokenize(io.BytesIO(b'def func() -> list: ...\n').readline):
...     print(tokenize.tok_name[tok.type], tokenize.tok_name[tok.exact_type], repr(tok.string)) # doctest: +SKIP37, +SKIP38
ENCODING ENCODING 'utf-8'
NAME NAME 'def'
NAME NAME 'func'
OP LPAR '('
OP RPAR ')'
OP OP '->'
NAME NAME 'list'
OP COLON ':'
OP OP '...'
NEWLINE NEWLINE '\n'
ENDMARKER ENDMARKER ''
```

This bug has been fixed in Python 3.7.

```py
>>> # Python 3.7+ behavior
>>> for tok in tokenize.tokenize(io.BytesIO(b'def func() -> list: ...\n').readline):
...     print(tokenize.tok_name[tok.type], tokenize.tok_name[tok.exact_type], repr(tok.string)) # doctest: +SKIP35, +SKIP36
ENCODING ENCODING 'utf-8'
NAME NAME 'def'
NAME NAME 'func'
OP LPAR '('
OP RPAR ')'
OP RARROW '->'
NAME NAME 'list'
OP COLON ':'
OP ELLIPSIS '...'
NEWLINE NEWLINE '\n'
ENDMARKER ENDMARKER ''
```

### `OP`

`OP` is a generic token type for all operators, delimiters, and the ellipsis
literal. This does not include characters and operators that are not
recognized by the parser (these are parsed as [`ERRORTOKEN`](#errortoken)).

When using `tokenize()`, the token type for an operator, delimiter, or
ellipsis literal token will be `OP`. To get the exact token type, use the
`exact_type` property of the namedtuple. `tok.exact_type` is equivalent to
`tok.type` for the remaining token types (with two exceptions, see the notes
below).

```py
>>> import io
>>> for tok in tokenize.tokenize(io.BytesIO(b'[1+2]\n').readline):
...     print(tokenize.tok_name[tok.type], repr(tok.string))
ENCODING 'utf-8'
OP '['
NUMBER '1'
OP '+'
NUMBER '2'
OP ']'
NEWLINE '\n'
ENDMARKER ''
>>> for tok in tokenize.tokenize(io.BytesIO(b'[1+2]\n').readline):
...     print(tokenize.tok_name[tok.exact_type], repr(tok.string))
ENCODING 'utf-8'
LSQB '['
NUMBER '1'
PLUS '+'
NUMBER '2'
RSQB ']'
NEWLINE '\n'
ENDMARKER ''
```

The following table lists all exact `OP` types and their corresponding
characters.

<!-- The table below is generated with exact_type_table.py -->

```eval_rst

.. include:: exact_type_table.txt
```

### `AWAIT`

### `ASYNC`

The `AWAIT` and `ASYNC` token types are used to tokenize the `await` and
`async` keywords in Python 3.5 and 3.6. They do not exist in Python 3.7+.

In Python 3.5 and 3.6, `await` and `async` are pseudo-keywords. To aid the
transition in the addition of new keywords, `await` and `async` were kept as
valid variable names outside of an `async def` blocks.

```py
>>> # This is valid Python in Python 3.5 and 3.6. It isn't in Python 3.7.
>>> async = 1 # doctest: +SKIP37, +SKIP38
>>> print_tokens("async = 1\n") # doctest: +SKIP37, +SKIP38
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='async', start=(1, 0), end=(1, 5), line='async = 1\n')
TokenInfo(type=53 (OP), string='=', start=(1, 6), end=(1, 7), line='async = 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 8), end=(1, 9), line='async = 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 9), end=(1, 10), line='async = 1\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

To support this, in Python 3.5 and 3.6 when `async def` is encountered,
`tokenize` keeps track of its indentation level, and all `await` and `async`
tokens that are nested under it are tokenized as `AWAIT` and `ASYNC`,
respectively (including the `async` from the `async def`). Otherwise, `await`
and `async` are tokenized as `NAME`, as in the example above.

```py
>>> # This is the behavior in Python 3.5 and 3.6
>>> print_tokens("""
... async def coro():
...     async with lock:
...         await f()
... await = 1
... """) # doctest: +SKIP37, +SKIP38
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=58 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=55 (ASYNC), string='async', start=(2, 0), end=(2, 5), line='async def coro():\n')
TokenInfo(type=1 (NAME), string='def', start=(2, 6), end=(2, 9), line='async def coro():\n')
TokenInfo(type=1 (NAME), string='coro', start=(2, 10), end=(2, 14), line='async def coro():\n')
TokenInfo(type=53 (OP), string='(', start=(2, 14), end=(2, 15), line='async def coro():\n')
TokenInfo(type=53 (OP), string=')', start=(2, 15), end=(2, 16), line='async def coro():\n')
TokenInfo(type=53 (OP), string=':', start=(2, 16), end=(2, 17), line='async def coro():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 17), end=(2, 18), line='async def coro():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line='    async with lock:\n')
TokenInfo(type=55 (ASYNC), string='async', start=(3, 4), end=(3, 9), line='    async with lock:\n')
TokenInfo(type=1 (NAME), string='with', start=(3, 10), end=(3, 14), line='    async with lock:\n')
TokenInfo(type=1 (NAME), string='lock', start=(3, 15), end=(3, 19), line='    async with lock:\n')
TokenInfo(type=53 (OP), string=':', start=(3, 19), end=(3, 20), line='    async with lock:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 20), end=(3, 21), line='    async with lock:\n')
TokenInfo(type=5 (INDENT), string='        ', start=(4, 0), end=(4, 8), line='        await f()\n')
TokenInfo(type=54 (AWAIT), string='await', start=(4, 8), end=(4, 13), line='        await f()\n')
TokenInfo(type=1 (NAME), string='f', start=(4, 14), end=(4, 15), line='        await f()\n')
TokenInfo(type=53 (OP), string='(', start=(4, 15), end=(4, 16), line='        await f()\n')
TokenInfo(type=53 (OP), string=')', start=(4, 16), end=(4, 17), line='        await f()\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 17), end=(4, 18), line='        await f()\n')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='await = 1\n')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='await = 1\n')
TokenInfo(type=1 (NAME), string='await', start=(5, 0), end=(5, 5), line='await = 1\n')
TokenInfo(type=53 (OP), string='=', start=(5, 6), end=(5, 7), line='await = 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(5, 8), end=(5, 9), line='await = 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(5, 9), end=(5, 10), line='await = 1\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(6, 0), end=(6, 0), line='')
```

In Python 3.7, `async` and `await` are proper keywords, and are tokenized as
[`NAME`](#name) like all other keywords. In Python 3.7, the `AWAIT` and
`ASYNC` token types have been removed from the `token` module.

```py
>>> # This is the behavior in Python 3.7+
>>> print_tokens("""
... async def coro():
...     async with lock:
...         await f()
... """) # doctest: +SKIP35, +SKIP36
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='async', start=(2, 0), end=(2, 5), line='async def coro():\n')
TokenInfo(type=1 (NAME), string='def', start=(2, 6), end=(2, 9), line='async def coro():\n')
TokenInfo(type=1 (NAME), string='coro', start=(2, 10), end=(2, 14), line='async def coro():\n')
TokenInfo(type=53 (OP), string='(', start=(2, 14), end=(2, 15), line='async def coro():\n')
TokenInfo(type=53 (OP), string=')', start=(2, 15), end=(2, 16), line='async def coro():\n')
TokenInfo(type=53 (OP), string=':', start=(2, 16), end=(2, 17), line='async def coro():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 17), end=(2, 18), line='async def coro():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line='    async with lock:\n')
TokenInfo(type=1 (NAME), string='async', start=(3, 4), end=(3, 9), line='    async with lock:\n')
TokenInfo(type=1 (NAME), string='with', start=(3, 10), end=(3, 14), line='    async with lock:\n')
TokenInfo(type=1 (NAME), string='lock', start=(3, 15), end=(3, 19), line='    async with lock:\n')
TokenInfo(type=53 (OP), string=':', start=(3, 19), end=(3, 20), line='    async with lock:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 20), end=(3, 21), line='    async with lock:\n')
TokenInfo(type=5 (INDENT), string='        ', start=(4, 0), end=(4, 8), line='        await f()\n')
TokenInfo(type=1 (NAME), string='await', start=(4, 8), end=(4, 13), line='        await f()\n')
TokenInfo(type=1 (NAME), string='f', start=(4, 14), end=(4, 15), line='        await f()\n')
TokenInfo(type=53 (OP), string='(', start=(4, 15), end=(4, 16), line='        await f()\n')
TokenInfo(type=53 (OP), string=')', start=(4, 16), end=(4, 17), line='        await f()\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 17), end=(4, 18), line='        await f()\n')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(5, 0), end=(5, 0), line='')
```

### `ERRORTOKEN`

The `ERRORTOKEN` type is used for any character that isn't recognized. Inputs
that tokenize `ERRORTOKEN`s cannot be valid Python, but this token type is
used so that applications that process tokens can do error recovery, as the
remainder of the input stream is tokenized normally. It can also be used to
process extensions to Python syntax (see the
[examples](examples.html#extending-python-s-syntax)). Every unrecognized
character is tokenized separately.

```py
>>> print_tokens("1!!\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 0), end=(1, 1), line='1!!\n')
TokenInfo(type=54 (ERRORTOKEN), string='!', start=(1, 1), end=(1, 2), line='1!!\n')
TokenInfo(type=54 (ERRORTOKEN), string='!', start=(1, 2), end=(1, 3), line='1!!\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 3), end=(1, 4), line='1!!\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens('💯\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=54 (ERRORTOKEN), string='💯', start=(1, 0), end=(1, 1), line='💯\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 1), end=(1, 2), line='💯\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

`ERRORTOKEN` is also used for single-quoted strings that are not closed before
a newline. See the [`STRING`](#error-behavior) section for more information.


```py
>>> print_tokens("'unclosed + string\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=54 (ERRORTOKEN), string="'", start=(1, 0), end=(1, 1), line="'unclosed + string\n")
TokenInfo(type=1 (NAME), string='unclosed', start=(1, 1), end=(1, 9), line="'unclosed + string\n")
TokenInfo(type=53 (OP), string='+', start=(1, 10), end=(1, 11), line="'unclosed + string\n")
TokenInfo(type=1 (NAME), string='string', start=(1, 12), end=(1, 18), line="'unclosed + string\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 18), end=(1, 19), line="'unclosed + string\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

If the string is continued and unclosed, the entire string is tokenized as an
error token. Otherwise only the start quote delimiter is.

```py
>>> print_tokens(r"""
... 'unclosed \
... continued string
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=54 (ERRORTOKEN), string="'unclosed \\\ncontinued string\n", start=(2, 0), end=(3, 17), line="'unclosed \\\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(4, 0), end=(4, 0), line='')
```

In the case of uncontinued unclosed single quoted strings, the spaces before
the string are also tokenized as `ERRORTOKEN`:

```py
>>> print_tokens("'an' +  'unclosed string\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=3 (STRING), string="'an'", start=(1, 0), end=(1, 4), line="'an' +  'unclosed string\n")
TokenInfo(type=53 (OP), string='+', start=(1, 5), end=(1, 6), line="'an' +  'unclosed string\n")
TokenInfo(type=54 (ERRORTOKEN), string=' ', start=(1, 6), end=(1, 7), line="'an' +  'unclosed string\n")
TokenInfo(type=54 (ERRORTOKEN), string=' ', start=(1, 7), end=(1, 8), line="'an' +  'unclosed string\n")
TokenInfo(type=54 (ERRORTOKEN), string="'", start=(1, 8), end=(1, 9), line="'an' +  'unclosed string\n")
TokenInfo(type=1 (NAME), string='unclosed', start=(1, 9), end=(1, 17), line="'an' +  'unclosed string\n")
TokenInfo(type=1 (NAME), string='string', start=(1, 18), end=(1, 24), line="'an' +  'unclosed string\n")
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 24), end=(1, 25), line="'an' +  'unclosed string\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

This doesn't apply to unclosed continued strings:

```py
>>> print_tokens(r"""
... 'an' +  'unclosed\
... continued string
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=3 (STRING), string="'an'", start=(2, 0), end=(2, 4), line="'an' +  'unclosed\\\n")
TokenInfo(type=53 (OP), string='+', start=(2, 5), end=(2, 6), line="'an' +  'unclosed\\\n")
TokenInfo(type=54 (ERRORTOKEN), string="'unclosed\\\ncontinued string\n", start=(2, 8), end=(3, 17), line="'an' +  'unclosed\\\n")
TokenInfo(type=0 (ENDMARKER), string='', start=(4, 0), end=(4, 0), line='')
```

Therefore, code that handles `ERRORTOKEN` specifically for unclosed strings
should check `tok.string[0] in '"\''`.

### `COMMENT`

The `COMMENT` token type represents a comment. If a comment spans multiple
lines, each line is tokenized separately.

```py
>>> print_tokens("""
... # This is a comment
... # This is another comment
... f() # This is a third comment
... """)
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=55 (COMMENT), string='# This is a comment', start=(2, 0), end=(2, 19), line='# This is a comment\n')
TokenInfo(type=56 (NL), string='\n', start=(2, 19), end=(2, 20), line='# This is a comment\n')
TokenInfo(type=55 (COMMENT), string='# This is another comment', start=(3, 0), end=(3, 25), line='# This is another comment\n')
TokenInfo(type=56 (NL), string='\n', start=(3, 25), end=(3, 26), line='# This is another comment\n')
TokenInfo(type=1 (NAME), string='f', start=(4, 0), end=(4, 1), line='f() # This is a third comment\n')
TokenInfo(type=53 (OP), string='(', start=(4, 1), end=(4, 2), line='f() # This is a third comment\n')
TokenInfo(type=53 (OP), string=')', start=(4, 2), end=(4, 3), line='f() # This is a third comment\n')
TokenInfo(type=55 (COMMENT), string='# This is a third comment', start=(4, 4), end=(4, 29), line='f() # This is a third comment\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 29), end=(4, 30), line='f() # This is a third comment\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(5, 0), end=(5, 0), line='')
```

The `COMMENT` token type exists only in the standard library Python
implementation of `tokenize`. The C implementation used by the interpreter
ignores comments. In Python versions prior to 3.7, `COMMENT` is only
importable from the `tokenize` module. In 3.7, it is added to the `token`
module as well.

### `NL`

The `NL` token type represents newline characters (`\n` or `\r\n`) that do not
end logical lines of code. Newlines that do end logical lines of Python code
area tokenized using the [`NEWLINE`](#newline) token type.

There are two situations where newlines are tokenized as `NL`:

1. Newlines that end lines that are continued after unclosed braces.

   ```py
   >>> print_tokens("""(1 +
   ... 2)
   ... """)
   TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
   TokenInfo(type=53 (OP), string='(', start=(1, 0), end=(1, 1), line='(1 +\n')
   TokenInfo(type=2 (NUMBER), string='1', start=(1, 1), end=(1, 2), line='(1 +\n')
   TokenInfo(type=53 (OP), string='+', start=(1, 3), end=(1, 4), line='(1 +\n')
   TokenInfo(type=56 (NL), string='\n', start=(1, 4), end=(1, 5), line='(1 +\n')
   TokenInfo(type=2 (NUMBER), string='2', start=(2, 0), end=(2, 1), line='2)\n')
   TokenInfo(type=53 (OP), string=')', start=(2, 1), end=(2, 2), line='2)\n')
   TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 2), end=(2, 3), line='2)\n')
   TokenInfo(type=0 (ENDMARKER), string='', start=(3, 0), end=(3, 0), line='')
   ```

2. Newlines that end empty lines or lines that only have comments.

   ```py
   >>> print_tokens("""
   ... # Comment line
   ...
   ... """)
   TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
   TokenInfo(type=56 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
   TokenInfo(type=55 (COMMENT), string='# Comment line', start=(2, 0), end=(2, 14), line='# Comment line\n')
   TokenInfo(type=56 (NL), string='\n', start=(2, 14), end=(2, 15), line='# Comment line\n')
   TokenInfo(type=56 (NL), string='\n', start=(3, 0), end=(3, 1), line='\n')
   TokenInfo(type=0 (ENDMARKER), string='', start=(4, 0), end=(4, 0), line='')
   ```

Note that newlines that are escaped (preceded with `\`) are treated like
whitespace, that is, they do not tokenize at all. Consequently, you should
always use the line numbers in the `start` and `end` attributes of the
`TokenInfo` namedtuple. Never try to determine line numbers by counting
[`NEWLINE`](#newline) and `NL` tokens.

```py
>>> print_tokens('1 + \\\n2\n')
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=2 (NUMBER), string='1', start=(1, 0), end=(1, 1), line='1 + \\\n')
TokenInfo(type=53 (OP), string='+', start=(1, 2), end=(1, 3), line='1 + \\\n')
TokenInfo(type=2 (NUMBER), string='2', start=(2, 0), end=(2, 1), line='2\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 1), end=(2, 2), line='2\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(3, 0), end=(3, 0), line='')
```

The `NL` token type exists only in the standard library Python implementation
of `tokenize`. The C implementation used by the interpreter only has
[`NEWLINE`](#newline). In Python versions prior to 3.7, `NL` is only
importable from `tokenize` module. In 3.7, it is added to the `token` module
as well.

### `ENCODING`

`ENCODING` is a special token type that represents the encoding of the input.
It is always the first token emitted by `tokenize()`, unless the detected
encoding is invalid, in which case it raises [`SyntaxError`](usage.html#syntaxerror). The encoding is detected via either a [PEP
263](https://www.python.org/dev/peps/pep-0263/) formatted comment in one of
the first two lines of the input (like `# -*- coding: utf-8 -*-`; such
comments are still tokenized as a [`COMMENT`](#comment) as well), or a
Unicode BOM character.

The detected encoding is in the `string` attribute of the `TokenInfo`.
`ENCODING` is the only token type where `tok.string` does not appear literally
in the input. The default encoding is `utf-8`.

If you only want to detect the encoding and nothing else, use
[`detect_encoding()`](helper-functions.html#detect-encoding-readline). If you
only need the encoding to pass to `open()`, use
[`tokenize.open()`](helper-functions.html#tokenize-open-filename).

The `start` and `end` line and column numbers for `ENCODING` will always be
`(0, 0)`.

```py
>>> print_tokens("# The default encoding is utf-8\n")
TokenInfo(type=57 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=55 (COMMENT), string='# The default encoding is utf-8', start=(1, 0), end=(1, 31), line='# The default encoding is utf-8\n')
TokenInfo(type=56 (NL), string='\n', start=(1, 31), end=(1, 32), line='# The default encoding is utf-8\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
>>> print_tokens("# -*- coding: ascii -*-\n")
TokenInfo(type=57 (ENCODING), string='ascii', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=55 (COMMENT), string='# -*- coding: ascii -*-', start=(1, 0), end=(1, 23), line='# -*- coding: ascii -*-\n')
TokenInfo(type=56 (NL), string='\n', start=(1, 23), end=(1, 24), line='# -*- coding: ascii -*-\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

The `ENCODING` token is not typically used when processing tokens, although
its guaranteed presence as the first token can be useful when processing tokens
as it will guarantee that every other token type will have some previous token
from the stream (see the [examples](examples.html#backporting-underscores-in-numeric-literals)).

Strictly speaking, the `string` of every token in a token stream should be
decodable by the encoding of the `ENCODING` token (e.g., if the encoding is
`ascii`, the tokens cannot include any non-ASCII characters).

The `ENCODING` token type exists only in the standard library Python
implementation of `tokenize`. The C implementation used by the interpreter
detects the encoding separately. In Python versions prior to 3.7, `ENCODING`
is only importable from `tokenize` module. In 3.7, it is added to the `token`
module as well.

### `N_TOKENS`

The number of token types (not including
[`NT_OFFSET`](helper-functions.html#nt-offset) or itself).

In Python 3.5 and 3.6, `token.N_TOKENS` and `tokenize.N_TOKENS` are different,
because [`COMMENT`](#comment), [`NL`](#nl), and [`ENCODING`](#encoding) are in
`tokenize` but not in `token`. In these versions, `N_TOKENS` is also not in
the `tok_name` dictionary. Additionally, Python 3.7 removed the
[`AWAIT`](#await) and [`ASYNC`](#async) tokens, so the value of `N_TOKENS` is
different than in 3.5 and 3.6.

```py
>>> # In Python 3.7
>>> tokenize.N_TOKENS # doctest: +SKIP35, +SKIP36
58
```
