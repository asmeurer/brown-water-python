Usage
=====

The `tokenize` module has several quirks which make it complicated to work
with (in my opinion, more complicated than necessary, but it is what it is).

The primary motivation of this guide is to document these quirks and
behaviors, and such a document would have been very helpful to me when I first
started using the module. Many of these behaviors were learned from
experimentation and reading the [source
code](https://github.com/python/cpython/blob/master/Lib/tokenize.py).
Therefore, things that are not obviously API guarantees should not be
considered API guarantees, that is, the CPython developers may decide to
change them in future Python versions. I will try to keep this guide updated
as new Python versions are released. [issue
reports](https://github.com/asmeurer/brown-water-python/issues) and [pull
requests](https://github.com/asmeurer/brown-water-python/pulls) are most
welcome.

## Calling syntax

The first thing you'll notice when using `tokenize()` is that its calling API
is rather odd. It does not accept a string. It does not accept a file-like
object either. Rather, it requires **the `readline` method of a bytes-mode file-like
object**. The bytes-encoded part is important. If a file is opened in text
mode (`'r'` instead of `'br'`), `tokenize()` will fail with an exception:

```py
>>> import tokenize
>>> with open('example.py') as f: # Incorrect, the default mode is 'r', not 'br'
...     for tok in tokenize.tokenize(f.readline):
...         print(tok)
Traceback (most recent call last):
  ...
TypeError: startswith first arg must be str or a tuple of str, not bytes
>>> with open('example.py', 'br') as f:
...     for tok in tokenize.tokenize(f.readline):
...         print(tok)
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=57 (COMMENT), string='# This is a an example file to be tokenized', start=(1, 0), end=(1, 43), line='# This is a an example file to be tokenized\n')
TokenInfo(type=58 (NL), string='\n', start=(1, 43), end=(1, 44), line='# This is a an example file to be tokenized\n')
TokenInfo(type=58 (NL), string='\n', start=(2, 0), end=(2, 1), line='\n')
TokenInfo(type=1 (NAME), string='def', start=(3, 0), end=(3, 3), line='def two():\n')
TokenInfo(type=1 (NAME), string='two', start=(3, 4), end=(3, 7), line='def two():\n')
TokenInfo(type=53 (OP), string='(', start=(3, 7), end=(3, 8), line='def two():\n')
TokenInfo(type=53 (OP), string=')', start=(3, 8), end=(3, 9), line='def two():\n')
TokenInfo(type=53 (OP), string=':', start=(3, 9), end=(3, 10), line='def two():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 10), end=(3, 11), line='def two():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(4, 0), end=(4, 4), line='    return 1 + 1\n')
TokenInfo(type=1 (NAME), string='return', start=(4, 4), end=(4, 10), line='    return 1 + 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(4, 11), end=(4, 12), line='    return 1 + 1\n')
TokenInfo(type=53 (OP), string='+', start=(4, 13), end=(4, 14), line='    return 1 + 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(4, 15), end=(4, 16), line='    return 1 + 1\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 16), end=(4, 17), line='    return 1 + 1\n')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(5, 0), end=(5, 0), line='')

```

To tokenize a string, you must encode it into a `bytes`, create an
`io.BytesIO` object (*not `StringIO`*), and use the `readline` method of that
object. If you find yourself doing this often, it may be useful to define a
helper function.


```py
>>> def tokenize_string(s):
...     import io
...     return tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline)
>>> for tok in tokenize_string('hello + tokenize'):
...     print(tok)
TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='hello', start=(1, 0), end=(1, 5), line='hello + tokenize')
TokenInfo(type=53 (OP), string='+', start=(1, 6), end=(1, 7), line='hello + tokenize')
TokenInfo(type=1 (NAME), string='tokenize', start=(1, 8), end=(1, 16), line='hello + tokenize')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

```

The reason for this API is that `tokenize()` is a streaming API, which works
line-by-line on a Python document. This is also why the `tokenize()` function
returns a generator. The typical pattern when using `tokenize()` is to iterate
over it with a `for` loop (see the next section). If you are finished doing
whatever you are doing before you reach the
[`ENDMARKER`](tokens.html#endmarker) token, you can break early from the loop
efficiently without tokenizing the rest of the document. It is not recommended
to convert the `tokenize()` generator into a list, except for debugging
purposes.

## `TokenInfo`

The `tokenize()` generator yields `TokenInfo` namedtuple objects. There are
two ways to work with `TokenInfo` objects. One is to unpack the tuple,
typically in the `for` statement:

```py
>>> for toknum, tokval, start, end, line in tokenize_string('hello + tokenize'):
...     print("toknum:", toknum, "tokval:", repr(tokval), "start:", start, "end:", end, "line:", repr(line))
toknum: 59 tokval: 'utf-8' start: (0, 0) end: (0, 0) line: ''
toknum: 1 tokval: 'hello' start: (1, 0) end: (1, 5) line: 'hello + tokenize'
toknum: 53 tokval: '+' start: (1, 6) end: (1, 7) line: 'hello + tokenize'
toknum: 1 tokval: 'tokenize' start: (1, 8) end: (1, 16) line: 'hello + tokenize'
toknum: 0 tokval: '' start: (2, 0) end: (2, 0) line: ''

```

By tradition, unused values are often replaced by `_`. You can also unpack the
`start` and `end` tuples directly.

```py
>>> for _, tokval, (start_line, start_col), (end_line, end_col), _ in tokenize_string('hello + tokenize'):
...     print("{tokval!r} on lines {start_line} to {end_line} on columns {start_col} to {end_col}".format(tokval=tokval, start_line=start_line, end_line=end_line, start_col=start_col, end_col=end_col))
'utf-8' on lines 0 to 0 on columns 0 to 0
'hello' on lines 1 to 1 on columns 0 to 5
'+' on lines 1 to 1 on columns 6 to 7
'tokenize' on lines 1 to 1 on columns 8 to 16
'' on lines 2 to 2 on columns 0 to 0

```

The other is to use it as-is, and access the members via attributes.

```py
>>> for tok in tokenize_string('hello + tokenize'):
...     print("type:", tok.type, "string:", repr(tok.string), "start:", tok.start, "end:", tok.end, "line:", repr(tok.line))
type: 59 string: 'utf-8' start: (0, 0) end: (0, 0) line: ''
type: 1 string: 'hello' start: (1, 0) end: (1, 5) line: 'hello + tokenize'
type: 53 string: '+' start: (1, 6) end: (1, 7) line: 'hello + tokenize'
type: 1 string: 'tokenize' start: (1, 8) end: (1, 16) line: 'hello + tokenize'
type: 0 string: '' start: (2, 0) end: (2, 0) line: ''

```

The advantage of this second way is that the `TokenInfo` object contains an
additional attribute, `exact_type`, which contains the exact token type of an
[`OP` token](tokens.html#op). However, this can also be determined from the
`string`. The first form is also less verbose, but the second form avoids
errors from getting the attributes in the wrong order. The form that you
should use depends on your preference on these tradeoffs.

### `type`

The token types are outlined in detail in the [Token Types](tokens.html)
section.

### `string`

The chunk of code that is tokenized. For token types where the string is
    meaningless, such as [`ENDMARKER`](tokens.html#endmarker), the string is
    empty. For the [`ENCODING`](tokens.html#encoding) token, the string is the
    encoding. It does not appear literally in the code, which is why the line
    and column numbers are 0 and the line is the empty string.

## `start` and `end`

`start` and `end` are tuples of (line number, column number) for the line and
column numbers of the start and end of the tokenized string. **Line numbers
start at 1 and column numbers start at 0**. The line and column numbers for the
[`ENCODING`](tokens.html#encoding) token, which is always the first token
emitted, are both `(0, 0)`. The start and end tuples always nondecreasing
(that is, `start <= end` will always be true for a single `TokenInfo`, and
`tok0.start <= tok1.start` and `tok0.end <= tok1.end` will be true for
consecutive `TokenInfo`s, `tok0` and `tok1`).

You should always use the `start` and `end` tuples to deduce line or column
information. `tokenize()` ignores syntactically irrelevant whitespace, which
can include newlines (in particular, escaped newlines, see
[`NL`](tokens.html#nl)).

## `line`

`line` gives the full line that the token comes from. This is useful for
reconstructing the whitespace between tokens (never assume that the whitespace
between tokens is space characters---they could also be escaped newlines or
tabs). `line` can also be useful for providing contextual error messages
relating to the tokenization.

## Exceptions