Usage
=====

The `tokenize` module has several quirks which make it complicated to work
with (in my opinion, more complicated than necessary, but it is what it is).

The primary motivation of this guide is to document these quirks and
behaviors, as such a document would have been very helpful to me when I first
started using the module. Most of these behaviors were learned from
experimentation and reading the [source
code](https://github.com/python/cpython/blob/master/Lib/tokenize.py). I have
no idea what behaviors can be considered API guarantees, that is, the CPython
developers may decide to change them in future Python versions. With that
being said, the CPython developers are generally very conservative about
changes to the standard library that might break downstream code, even for
major releases. I will try to keep this guide updated as new Python versions
are released. [Issue
reports](https://github.com/asmeurer/brown-water-python/issues) and [pull
requests](https://github.com/asmeurer/brown-water-python/pulls) are most
welcome.

## Calling Syntax

The first thing you'll notice when using `tokenize()` is that its calling API
is rather odd. It does not accept a string. It does not accept a file-like
object either. Rather, it requires **the `readline` method of a bytes-mode file-like
object**. The bytes-mode part is important. If a file is opened in text
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
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=60 (COMMENT), string='# This is a an example file to be tokenized', start=(1, 0), end=(1, 43), line='# This is a an example file to be tokenized\n')
TokenInfo(type=61 (NL), string='\n', start=(1, 43), end=(1, 44), line='# This is a an example file to be tokenized\n')
TokenInfo(type=61 (NL), string='\n', start=(2, 0), end=(2, 1), line='\n')
TokenInfo(type=1 (NAME), string='def', start=(3, 0), end=(3, 3), line='def two():\n')
TokenInfo(type=1 (NAME), string='two', start=(3, 4), end=(3, 7), line='def two():\n')
TokenInfo(type=54 (OP), string='(', start=(3, 7), end=(3, 8), line='def two():\n')
TokenInfo(type=54 (OP), string=')', start=(3, 8), end=(3, 9), line='def two():\n')
TokenInfo(type=54 (OP), string=':', start=(3, 9), end=(3, 10), line='def two():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 10), end=(3, 11), line='def two():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(4, 0), end=(4, 4), line='    return 1 + 1\n')
TokenInfo(type=1 (NAME), string='return', start=(4, 4), end=(4, 10), line='    return 1 + 1\n')
TokenInfo(type=2 (NUMBER), string='1', start=(4, 11), end=(4, 12), line='    return 1 + 1\n')
TokenInfo(type=54 (OP), string='+', start=(4, 13), end=(4, 14), line='    return 1 + 1\n')
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
>>> import io
>>> def tokenize_string(s):
...     return tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline)
>>> for tok in tokenize_string('hello + tokenize\n'):
...     print(tok)
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=1 (NAME), string='hello', start=(1, 0), end=(1, 5), line='hello + tokenize\n')
TokenInfo(type=54 (OP), string='+', start=(1, 6), end=(1, 7), line='hello + tokenize\n')
TokenInfo(type=1 (NAME), string='tokenize', start=(1, 8), end=(1, 16), line='hello + tokenize\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 16), end=(1, 17), line='hello + tokenize\n')
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
purposes. Not only is this inefficient, it makes it impossible to deal with [exceptions](#exceptions).

## `TokenInfo`

The `tokenize()` generator yields `TokenInfo` namedtuple objects, with the
following fields:

```py
>>> tokenize.TokenInfo._fields
('type', 'string', 'start', 'end', 'line')
```

The meaning of each field is outlined [below](#tokeninfo-fields).

There are two ways to work with `TokenInfo` objects. One is to unpack the
tuple, typically in the `for` statement:

```py
>>> for toknum, tokval, start, end, line in tokenize_string('hello + tokenize\n'):
...     print("toknum:", toknum, "tokval:", repr(tokval), "start:", start, "end:", end, "line:", repr(line))
toknum: 62 tokval: 'utf-8' start: (0, 0) end: (0, 0) line: ''
toknum: 1 tokval: 'hello' start: (1, 0) end: (1, 5) line: 'hello + tokenize\n'
toknum: 54 tokval: '+' start: (1, 6) end: (1, 7) line: 'hello + tokenize\n'
toknum: 1 tokval: 'tokenize' start: (1, 8) end: (1, 16) line: 'hello + tokenize\n'
toknum: 4 tokval: '\n' start: (1, 16) end: (1, 17) line: 'hello + tokenize\n'
toknum: 0 tokval: '' start: (2, 0) end: (2, 0) line: ''
```

By tradition, unused values are often replaced by `_`. You can also unpack the
`start` and `end` tuples directly.

```py
>>> for _, tokval, (start_line, start_col), (end_line, end_col), _ in tokenize_string('hello + tokenize\n'):
...     print("{tokval!r} on lines {start_line} to {end_line} on columns {start_col} to {end_col}".format(tokval=tokval, start_line=start_line, end_line=end_line, start_col=start_col, end_col=end_col))
'utf-8' on lines 0 to 0 on columns 0 to 0
'hello' on lines 1 to 1 on columns 0 to 5
'+' on lines 1 to 1 on columns 6 to 7
'tokenize' on lines 1 to 1 on columns 8 to 16
'\n' on lines 1 to 1 on columns 16 to 17
'' on lines 2 to 2 on columns 0 to 0
```

The other is to use it as-is, and access the members via attributes. I like
using `tok` as the variable name for the tokens. `token` can be confused with
the [module name](https://docs.python.org/3/library/token.html), so I don't
recommend using that (even though I recommend only importing `tokenize`, which
includes all the names from `token`).

```py
>>> for tok in tokenize_string('hello + tokenize\n'):
...     print("type:", tok.type, "string:", repr(tok.string), "start:", tok.start, "end:", tok.end, "line:", repr(tok.line))
type: 62 string: 'utf-8' start: (0, 0) end: (0, 0) line: ''
type: 1 string: 'hello' start: (1, 0) end: (1, 5) line: 'hello + tokenize\n'
type: 54 string: '+' start: (1, 6) end: (1, 7) line: 'hello + tokenize\n'
type: 1 string: 'tokenize' start: (1, 8) end: (1, 16) line: 'hello + tokenize\n'
type: 4 string: '\n' start: (1, 16) end: (1, 17) line: 'hello + tokenize\n'
type: 0 string: '' start: (2, 0) end: (2, 0) line: ''
```

One advantage of this second way is that the `TokenInfo` object contains an
additional attribute, `exact_type`, which contains the exact token type of an
[`OP` token](tokens.html#op). However, this can also be determined from the
`string`. Additionally, the first form is less verbose, but the second form
avoids errors from getting the attributes in the wrong order. The form that
you should use depends on your preference on these tradeoffs. I personally
recommend the second form (`for tok in tokenize(...): ... tok.type, etc.`),
unless you have the `(toknum, tokstr, start, end, line)` order memorized.

### `TokenInfo` Fields

#### `type`

The token types are outlined in detail in the [Token Types](tokens.md)
section.

#### `string`

The chunk of code that is tokenized. For token types where the string is
meaningless, such as [`ENDMARKER`](tokens.html#endmarker), the string is
empty.

For the [`ENCODING`](tokens.html#encoding) token, the string is the encoding,
which does not appear literally in the code, which is why for `ENCODING` the
line and column numbers are 0 and the `line` is the empty string.

#### `start` and `end`

`start` and `end` are tuples of (line number, column number) for the line and
column numbers of the start and end of the tokenized string. **Line numbers
start at 1 and column numbers start at 0**. The line and column numbers for
the [`ENCODING`](tokens.html#encoding) token, which is always the first token
emitted, are both `(0, 0)`.

Because Python tuples compare lexicographically (i.e., `(a, b) < (c, d)` is
equivalent to `a < c or (a == c and b <= d)`), these tuples can be compared
directly to determine which comes earlier in the input. The `start` and `end`
tuples as emitted from `tokenize()` are always nondecreasing (that is, `start
<= end` will always be True for a single `TokenInfo`, and `tok0.start <=
tok1.start` and `tok0.end <= tok1.end` will be True for consecutive
`TokenInfo`s, `tok0` and `tok1`).

You should always use the `start` and `end` tuples to deduce line or column
information. `tokenize()` ignores syntactically irrelevant whitespace, which
can include newlines (in particular, escaped newlines, see
[`NL`](tokens.html#nl)).

#### `line`

`line` gives the full line that the token comes from. This is useful for
reconstructing the whitespace between tokens (never assume that the whitespace
between tokens is space characters---it could also consist of escaped newlines
or tabs). `line` can also be useful for providing contextual error messages
relating to the tokenization.

## Exceptions

`tokenize()` has two failure modes: [`ERRORTOKEN`](tokens.html#errortoken) and
exceptions. When a non-fatal error occurs, some text will be tokenized as an
[`ERRORTOKEN`](tokens.html#errortoken), and tokenizing will continue on the
remainder of the input. This happens, for instance, for unrecognized
characters, such as `$`, and unclosed single-quoted strings. See the
[`ERRORTOKEN`](tokens.html#errortoken) and
[`STRING`](tokens.html#error-behavior) references for more information.

Other failures are so fatal that tokenization cannot continue, causing an
exception to be raised. Depending on what you are doing, you may want to catch
the exception and deal with it or let it bubble up to the caller.

These are the exceptions that can be raised from `tokenize()`. An exception
other than these likely indicates incorrect [input](#calling-syntax).

### `SyntaxError`

`SyntaxError` is raised when the input has an invalid encoding. The encoding
is detected using the [`detect_encoding()`](helper-functions.html#detect-encoding-readline)
function, which uses either a [PEP
263](https://www.python.org/dev/peps/pep-0263/) formatted comment at the
beginning of the input (like `# -*- coding: utf-8 -*-`), or a Unicode BOM
character. If both are present, or if the PEP 263 encoding is invalid,
`SyntaxError` is raised.

```py
>>> tokenize.tokenize(io.BytesIO(b"# -*- coding: invalid -*-\n").readline)
Traceback (most recent call last):
  ...
SyntaxError: unknown encoding: invalid
```

See also [`ENCODING`](tokens.html#encoding).

### `TokenError`

`tokenize.TokenError` is raised in two situations. The only way to distinguish
the two is to inspect the exception message. In both cases, `TokenError` is
raised if the end of the input (`EOF`) is reached without a delimiter being
closed. Tokens before the end of the input are still emitted, so it is
typically desirable to process the tokens from `tokenize()` and handle
`TokenError` as an end of input condition.

The second argument of the exception (`e.args[1]`) is a tuple of the
[start](#start-and-end) line and column number for the part of the input that
was not tokenized due to the exception.

1. **EOF in multi-line string**

   This happens if a triple-quoted string (i.e., a multi-line string, or
   "docstring"), is not closed at the end of the input. This exception can be
   detected by checking `'string' in e.args[0]`.

   ```py
   >>> for tok in tokenize.tokenize(io.BytesIO(b"""
   ... def f():
   ...     '''
   ...     unclosed docstring
   ... """).readline):
   ...     print(tok) # doctest: +SKIP
   TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
   TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
   TokenInfo(type=1 (NAME), string='def', start=(2, 0), end=(2, 3), line='def f():\n')
   TokenInfo(type=1 (NAME), string='f', start=(2, 4), end=(2, 5), line='def f():\n')
   TokenInfo(type=54 (OP), string='(', start=(2, 5), end=(2, 6), line='def f():\n')
   TokenInfo(type=54 (OP), string=')', start=(2, 6), end=(2, 7), line='def f():\n')
   TokenInfo(type=54 (OP), string=':', start=(2, 7), end=(2, 8), line='def f():\n')
   TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 8), end=(2, 9), line='def f():\n')
   TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line="    '''\n")
   Traceback (most recent call last):
     ...
   tokenize.TokenError: ('EOF in multi-line string', (3, 4))

   ```

2. **EOF in multi-line statement**

   This error occurs when an unclosed brace is found. Note that `tokenize`
   does not necessarily stop parsing as soon as the input is syntactically
   invalid, as it only has limited knowledge of Python syntax. In fact, in the
   current implementation, this exception is only raised after all tokens have
   been emitted, except possibly [`DEDENT`](tokens.html#dedent) tokens. This
   exception can be detected by checking `'statement' in e.args[0]`.

   ```py
   >>> for tok in tokenize.tokenize(io.BytesIO(b"""
   ... (1 +
   ... def f():
   ...     pass
   ... """).readline):
   ...     print(tok) # doctest: +SKIP
   TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
   TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
   TokenInfo(type=54 (OP), string='(', start=(2, 0), end=(2, 1), line='(1 +\n')
   TokenInfo(type=2 (NUMBER), string='1', start=(2, 1), end=(2, 2), line='(1 +\n')
   TokenInfo(type=54 (OP), string='+', start=(2, 3), end=(2, 4), line='(1 +\n')
   TokenInfo(type=61 (NL), string='\n', start=(2, 4), end=(2, 5), line='(1 +\n')
   TokenInfo(type=1 (NAME), string='def', start=(3, 0), end=(3, 3), line='def f():\n')
   TokenInfo(type=1 (NAME), string='f', start=(3, 4), end=(3, 5), line='def f():\n')
   TokenInfo(type=54 (OP), string='(', start=(3, 5), end=(3, 6), line='def f():\n')
   TokenInfo(type=54 (OP), string=')', start=(3, 6), end=(3, 7), line='def f():\n')
   TokenInfo(type=54 (OP), string=':', start=(3, 7), end=(3, 8), line='def f():\n')
   TokenInfo(type=61 (NL), string='\n', start=(3, 8), end=(3, 9), line='def f():\n')
   TokenInfo(type=1 (NAME), string='pass', start=(4, 4), end=(4, 8), line='    pass\n')
   TokenInfo(type=61 (NL), string='\n', start=(4, 8), end=(4, 9), line='    pass\n')
   Traceback (most recent call last):
     ...
   tokenize.TokenError: ('EOF in multi-line statement', (5, 0))

   ```

The following example shows how `TokenError` might be caught and processed.
See also the [examples](examples.md).

```py
>>> def tokens_with_errors(s):
...     try:
...         for tok in tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline):
...             print(tok)
...     except tokenize.TokenError as e:
...         if 'string' in e.args[0]:
...             print("TokenError: Unclosed multi-line string starting at", e.args[1])
...         elif 'statement' in e.args[0]:
...             print("TokenError: Unclosed brace(s)")
...         else:
...             # Unrecognized TokenError. Shouldn't happen
...             raise
>>> tokens_with_errors("""
... def f():
...     '''
...     unclosed docstring
... """)
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='def', start=(2, 0), end=(2, 3), line='def f():\n')
TokenInfo(type=1 (NAME), string='f', start=(2, 4), end=(2, 5), line='def f():\n')
TokenInfo(type=54 (OP), string='(', start=(2, 5), end=(2, 6), line='def f():\n')
TokenInfo(type=54 (OP), string=')', start=(2, 6), end=(2, 7), line='def f():\n')
TokenInfo(type=54 (OP), string=':', start=(2, 7), end=(2, 8), line='def f():\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 8), end=(2, 9), line='def f():\n')
TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line="    '''\n")
TokenError: Unclosed multi-line string starting at (3, 4)
>>> tokens_with_errors("""
... (1 +
... def f():
...     pass
... """)
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=54 (OP), string='(', start=(2, 0), end=(2, 1), line='(1 +\n')
TokenInfo(type=2 (NUMBER), string='1', start=(2, 1), end=(2, 2), line='(1 +\n')
TokenInfo(type=54 (OP), string='+', start=(2, 3), end=(2, 4), line='(1 +\n')
TokenInfo(type=61 (NL), string='\n', start=(2, 4), end=(2, 5), line='(1 +\n')
TokenInfo(type=1 (NAME), string='def', start=(3, 0), end=(3, 3), line='def f():\n')
TokenInfo(type=1 (NAME), string='f', start=(3, 4), end=(3, 5), line='def f():\n')
TokenInfo(type=54 (OP), string='(', start=(3, 5), end=(3, 6), line='def f():\n')
TokenInfo(type=54 (OP), string=')', start=(3, 6), end=(3, 7), line='def f():\n')
TokenInfo(type=54 (OP), string=':', start=(3, 7), end=(3, 8), line='def f():\n')
TokenInfo(type=61 (NL), string='\n', start=(3, 8), end=(3, 9), line='def f():\n')
TokenInfo(type=1 (NAME), string='pass', start=(4, 4), end=(4, 8), line='    pass\n')
TokenInfo(type=61 (NL), string='\n', start=(4, 8), end=(4, 9), line='    pass\n')
TokenError: Unclosed brace(s)
```

### `IndentationError`

`tokenize()` raises `IndentationError` if an unindent does not match an outer
indentation level.

```py
>>> for tok in tokenize.tokenize(io.BytesIO(b"""
... if x:
...     pass
...  f
... """).readline):
...     print(tok) # doctest: +SKIP
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='if', start=(2, 0), end=(2, 2), line='if x:\n')
TokenInfo(type=1 (NAME), string='x', start=(2, 3), end=(2, 4), line='if x:\n')
TokenInfo(type=54 (OP), string=':', start=(2, 4), end=(2, 5), line='if x:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 5), end=(2, 6), line='if x:\n')
TokenInfo(type=5 (INDENT), string='    ', start=(3, 0), end=(3, 4), line='    pass\n')
TokenInfo(type=1 (NAME), string='pass', start=(3, 4), end=(3, 8), line='    pass\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 8), end=(3, 9), line='    pass\n')
Traceback (most recent call last):
  ...
  File "<tokenize>", line 4
    f
    ^
IndentationError: unindent does not match any outer indentation level

```

This error is difficult to recover from. If you need to handle tokenizing
input with invalid indentation, my best recommendation is to instead use the
[parso](https://parso.readthedocs.io/en/latest/) library, which does not raise
`IndentationError` (it also does not raise any of the other exceptions
discussed here). See also the [discussion](alternatives.html#parso) of parso in the
alternatives section.

This is the only indentation error `tokenize` cares about. It does not care
about other syntactically invalid constructs such as inconsistently mixing
tabs and spaces.

```py
>>> for tok in tokenize.tokenize(io.BytesIO(b"""
... if x:
...     \tpass
... \t    pass
... """).readline):
...     print(tok)
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=61 (NL), string='\n', start=(1, 0), end=(1, 1), line='\n')
TokenInfo(type=1 (NAME), string='if', start=(2, 0), end=(2, 2), line='if x:\n')
TokenInfo(type=1 (NAME), string='x', start=(2, 3), end=(2, 4), line='if x:\n')
TokenInfo(type=54 (OP), string=':', start=(2, 4), end=(2, 5), line='if x:\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(2, 5), end=(2, 6), line='if x:\n')
TokenInfo(type=5 (INDENT), string='    \t', start=(3, 0), end=(3, 5), line='    \tpass\n')
TokenInfo(type=1 (NAME), string='pass', start=(3, 5), end=(3, 9), line='    \tpass\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(3, 9), end=(3, 10), line='    \tpass\n')
TokenInfo(type=5 (INDENT), string='\t    ', start=(4, 0), end=(4, 5), line='\t    pass\n')
TokenInfo(type=1 (NAME), string='pass', start=(4, 5), end=(4, 9), line='\t    pass\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(4, 9), end=(4, 10), line='\t    pass\n')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='')
TokenInfo(type=6 (DEDENT), string='', start=(5, 0), end=(5, 0), line='')
TokenInfo(type=0 (ENDMARKER), string='', start=(5, 0), end=(5, 0), line='')
>>> exec("""
... if x:
...     \tpass
... \t    pass
... """)
Traceback (most recent call last):
  ...
  File "<string>", line 4
    pass
       ^
TabError: inconsistent use of tabs and spaces in indentation
```
