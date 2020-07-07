Examples
========

Here are some examples that use `tokenize`.

To copy the examples, click the **<code style="color:#c65d09;
font-size:18px">\>\>\></code>** button on the top right of the code block to
hide the Python prompts and outputs.

To simplify the examples, the following helper function is used.

```py
>>> import tokenize
>>> import io
>>> def tokenize_string(s):
...     """
...     Generator of tokens from the string s
...     """
...     return tokenize.tokenize(io.BytesIO(s.encode('utf-8')).readline)
```

## Processing Tokens

These examples show different ways that tokens can be processed.

### `inside_string()`

`inside_string(s, row, col)` takes the Python code `s` and determines if
position at `(row, col)` is inside a `STRING` token.

To simplify the example for the purposes of illustration, `inside_string`
returns `True` even if `(row, col)` is on the quote delimiter or prefix
character (like `r` or `f`) of the string.


```py
>>> def inside_string(s, row, col):
...     """
...     Returns True if (row, col) is inside a string in s, False otherwise.
...
...     row starts at 1 and col starts at 0.
...     """
...     try:
...         for toknum, tokval, start, end, _ in tokenize_string(s):
...             if toknum == tokenize.ERRORTOKEN and tokval[0] in '"\'':
...                 # There is an unclosed string. We haven't gotten to the
...                 # position yet, so it must be inside this string
...                 return True
...             if start <= (row, col) <= end:
...                 return toknum == tokenize.STRING
...     except tokenize.TokenError as e:
...         # Uncompleted docstring or braces.
...         # 'string' in the exception means uncompleted multi-line string
...         return 'string' in e.args[0]
...
...     return False
```

Let's walk through the code.

We don't want the function to raise [`TokenError`](tokenerror) on
uncompleted delimiters or unclosed multi-line strings, so we wrap the loop in
a `try` block.

```py
try:
```

Next we have the main loop. We don't use the `line` attribute, so we use `_`
instead to indicate it isn't used.

```py
    for toknum, tokval, start, end, _ in tokenize_string(s):
```

The idea is to loop through the tokens until we find one that `(row, col)` is
contained in (it is between the [`start`](start-and-end) and
[`end`](start-and-end) tokens). This may not actually happen, for
instance, if the `(row, col)` is inside whitespace that isn't tokenized.

The first thing to check for is an [`ERRORTOKEN`](errortoken)
caused by an unclosed single-quoted string. If an unclosed single-quoted (not
multi-line) string is encountered, that is, it is closed by a newline, like
`"an unclosed string`, and we haven't reached our `(row, col)` yet, then we
assume our `(row, col)` is inside this unclosed string. This implicitly makes
the rest of the document part of the unclosed string. We could also easily
modify this to only assume the rest of the line is inside the unclosed string.


```py
         if toknum == tokenize.ERRORTOKEN and tokval[0] in '"\'':
             # There is an unclosed string. We haven't gotten to the
             # position yet, so it must be inside this string
             return True
```

Now we have the main condition. If the `(row, col)` is between the
[`start`](start-and-end) and [`end`](start-and-end) of a
token, we have gone as far as we need to.

```py
         if start <= (row, col) <= end:
```

That token is either a `STRING` token, in which case, we should return `True`,
or it is another token type, which means our `(row, col)` is not on a `STRING`
token and we can return `False`. This can be written as simply:

```py
             return toknum == tokenize.STRING
```

Now the exceptional case. If we see a [`TokenError`](tokenerror),
we don't want the function to fail.

```py
except tokenize.TokenError as e:
```

Remember that there are two possibilities for a
[`TokenError`](tokenerror). If `'statement'` is in the error
message, there is an unclosed brace somewhere. This case only happens when
`tokenize()` has reached the end of the token stream, so if the above checks
haven't returned `True` yet, then `(row, col)` must not be inside a `STRING`
token, so we should return `False`.

If `'string'` is inside the error message, there is an unclosed multi-line
string. In this case, we want to check if we are inside this string. We can
check the start of the multi-line string in the
[`TokenError`](tokenerror). Remember that the message is in
`e.args[0]` and the start is in `e.args[1]`. So we should return `True` in
this case if the `(row, col)` are after the `e.args[1]`, and `False`
otherwise.

This logic can all be written succinctly as

```py
    # Uncompleted docstring or braces.
    # 'string' in the exception means uncompleted multi-line string
    return 'string' in e.args[0] and (row, col) >= e.args[1]
```

Finally, if we reach the end of the token stream without returning anything,
it means we never found a `STRING` that is on our `(row, col)`.

```py
return False
```

Here are some test cases to verify the code is correct

```py
>>> # Basic test. Remember that lines start at 1 and columns start at 0.
>>> inside_string("print('a string')", 1, 4) # 't' in print
False
>>> inside_string("print('a string')", 1, 9) # 'a' in 'a string'
True
>>> # Note: because our input uses """, the first line is empty
>>> inside_string("""
... "an unclosed single quote string
... 1 + 1
... """, 2, 4) # 'u' in 'unclosed'
True
>>> # Check for whitespace right before TokenError
>>> inside_string("""
...  '''an unclosed multi-line string
... 1 + 1
... """, 1, 0) # the space before '''
False
>>> # Check inside an unclosed multi-line string
>>> inside_string("""
...  '''an unclosed multi-line string
... 1 + 1
... """, 1, 4) # 'a' in 'an'
True
>>> # Check for whitespace between tokens
>>> inside_string("""
... def hello(name):
...     return 'hello %s' % name
... """, 2, 3) # ' ' before hello(name)
False
>>> # Check TokenError from unclosed delimiters
>>> inside_string("""
... def hello(name:
...     return 'hello %s' % name
... """, 4, 0) # Last character in the input
False
>>> inside_string("""
... def hello(name:
...     return 'hello %s' % name
... """, 3, 12) # 'h' in 'hello'
True
```

#### Exercises

- Modify `inside_string` to return `False` if `(row, col)` is on a prefix or
  quote character. For instance in `rb'abc'` it should only return True on the
  `abc` part of the string. (*This is more challenging than it may sound. Be
  sure to write lots of test cases*)

- Right now if `(row, col)` is a whitespace character that is not tokenized,
  the loop will pass over it and tokenize the entire input before returning
  `False`. Make this more efficient

- Only consider characters to be inside an unclosed single-quoted string if
  they are on the same line.

- Write a version of `inside_string()` using
  [parso](https://parso.readthedocs.io/en/latest/)'s tokenizer
  (`parso.python.tokenize.tokenize()`).

### `line_numbers()`

Let's go back to our motivating example from the [`tokenize` vs.
Alternatives](alternatives) section, a function that prints the line
numbers of every function definition. [Our
function](tokenize) looked like this (rewritten to use our
`tokenize_string()` helper):

```py
>>> def line_numbers(s):
...     for tok in tokenize_string(s):
...         if tok.type == tokenize.NAME and tok.string == 'def':
...             print(tok.start[0])
```

As we noted, this function works, but it doesn't handle any of our
[error](errortoken) [conditions](exceptions).

Looking at our exceptions list, [`SynatxError`](syntaxerror) and
[`IndentationError`](indentationerror) are unrecoverable, so we
will just let them bubble up. However, [`TokenError`](tokenerror)
simply means that the input had an unclosed brace or multi-line string. In the
former case, the tokenization reaches the end of the input before the
exception is raised, and in the latter case, the remainder of the input is
inside the unclosed multi-line string, so we can safely ignore
[`TokenError`](tokenerror) in either case.


```py
>>> def line_numbers(s):
...     try:
...         for tok in tokenize_string(s):
...             if tok.type == tokenize.NAME and tok.string == 'def':
...                 print(tok.start[0])
...     except tokenize.TokenError:
...         pass
```

Finally, let's consider [`ERRORTOKEN`](errortoken) due to unclosed
single-quoted strings. Our motivation for using `tokenize` to solve this
problem is to handle incomplete or invalid Python (otherwise, we should use
the [`ast` implementation](ast), which is much simpler).
Thus, it makes sense to treat unclosed single-quoted strings as if they were
closed at the end of the line.


```py
>>> def line_numbers(s):
...     try:
...         skip_line = -1
...         for tok in tokenize_string(s):
...             if tok.start[0] == skip_line:
...                 continue
...             elif tok.start[0] >= skip_line:
...                 # reset skip_line
...                 skip_line = -1
...             if tok.type == tokenize.ERRORTOKEN and tok.string in '"\'':
...                 # Unclosed single-quoted string. Ignore the rest of this line
...                 skip_line = tok.start[0]
...                 continue
...             if tok.type == tokenize.NAME and tok.string == 'def':
...                 print(tok.start[0])
...     except tokenize.TokenError:
...         pass
```

Here are our original test cases, plus some additional ones for our added
behavior.

```py
>>> code = """\
... def f(x):
...     pass
...
... class MyClass:
...     def g(self):
...         pass
... """
>>> line_numbers(code)
1
5
>>> code = '''\
... FUNCTION_SKELETON = """
... def {name}({args}):
...     {body}
... """
... '''
>>> line_numbers(code) # no output
>>> code = """\
... def f():
...     '''
...     an unclosed docstring.
... """
>>> line_numbers(code)
1
>>> code = """\
... def f(: # Unclosed parenthesis
...     pass
... """
>>> line_numbers(code)
1
>>> code = """\
... def f():
...     "an unclosed single-quoted string. It should not match this def
... def g():
...     pass
... """
>>> line_numbers(code)
1
3
```

(indentation-level)=
### Indentation Level

[`INDENT`](indent) and [`DEDENT`](dedent) tokens are
always balanced in the token stream (unless there is an
[`IndentationError`](indentationerror)), so it is easy to detect the
indentation level of a block of code by incrementing and decrementing a
counter.

```py
>>> def indentation_level(s, row, col):
...     """
...     Returns the indentation level of the code at (row, col)
...     """
...     level = 0
...     try:
...         for tok in tokenize_string(s):
...             if tok.start >= (row, col):
...                 return level
...             if tok.type == tokenize.INDENT:
...                 level += 1
...             if tok.type == tokenize.DEDENT:
...                 level -= 1
...     except tokenize.TokenError:
...         # Ignore TokenError (we don't care about incomplete code)
...         pass
...     return level
```

To demonstrate the function, let's apply it to itself.

```py
>>> indentation_level_source = '''\
... def indentation_level(s, row, col):
...     """
...     Returns the indentation level of the code at (row, col)
...     """
...     level = 0
...     try:
...         for tok in tokenize_string(s):
...             if tok.start >= (row, col):
...                 return level
...             if tok.type == tokenize.INDENT:
...                 level += 1
...             if tok.type == tokenize.DEDENT:
...                 level -= 1
...     except tokenize.TokenError:
...         # Ignore TokenError (we don't care about incomplete code)
...         pass
...     return level
... '''
>>> # Use a large column number so it always looks at the fully indented line.
>>> for i in range(1, indentation_level_source.count('\n') + 2): # doctest: +NORMALIZE_WHITESPACE
...     print(indentation_level(indentation_level_source, i, 100), indentation_level_source.split('\n')[i-1])
0 def indentation_level(s, row, col):
1     """
1     Returns the indentation level of the code at (row, col)
1     """
1     level = 0
1     try:
2         for tok in tokenize_string(s):
3             if tok.start >= (row, col):
4                 return level
3             if tok.type == tokenize.INDENT:
4                 level += 1
3             if tok.type == tokenize.DEDENT:
4                 level -= 1
1     except tokenize.TokenError:
1         # Ignore TokenError (we don't care about incomplete code)
2         pass
1     return level
0
```

An oddity worth mentioning: the comment near the end of the function is not
considered indented more than the `except` line. Remember that the C parser,
which `tokenize` is based on, ignores [comments](comment), so true
indentations with [`INDENT`](indent) must occur on lines with real
code.

### Mismatched Parentheses


This example shows how to use a very important tool when processing tokens, a
stack. A [*stack*](https://en.wikipedia.org/wiki/Stack_(abstract_data_type))
is a data structure that operates as Last In, First Out. A stack has two basic
operations, *push*, which adds something to the stack, and *pop*, which
removes the most recently added item.

In Python, a stack is usually implemented using a list. The push method is
`list.append()` and the pop method is `list.pop()`.

```py
>>> stack = []
>>> stack.append(1)
>>> stack.append(2)
>>> stack.pop()
2
>>> stack.append(3)
>>> stack.pop()
3
>>> stack.pop()
1
```

Stacks are important because they allow keeping track of nested structures.
Going down one level of nesting can be represented by pushing something on the
stack, and going up can be represented by popping. The stack allows keeping
track of the opening of the nested structure to ensure it properly matches the
closing.

In particular, for a set of parentheses, such as `(((())())())`, a stack can
be used to check if they are properly balanced. Every time we encounter an
opening parenthesis, we push it on the stack, and every time we encounter a
closing parenthesis, we pop the stack. If the stack is empty when we try to
pop it, or if it still has items when we finish processing all the
parentheses, it means they are not balanced. Otherwise, they are. In this
case, we could simply use a counter like we did for the previous example, and
make sure it doesn't go negative and ends at 0, but a stack is required to
handle more than one type of brace, like `(())([])[]`, which, of course, is
the case in Python.

Here is an example showing how to use a stack to find all the mismatched
parentheses or braces in a piece of Python code. The function handles `()`,
`[]`, and `{}` type braces.

```py
>>> braces = {
...     tokenize.LPAR: tokenize.RPAR, # ()
...     tokenize.LSQB: tokenize.RSQB, # []
...     tokenize.LBRACE: tokenize.RBRACE, # {}
... }
...
>>> def matching_parens(s):
...     """
...     Find matching and mismatching parentheses and braces
...
...     s should be a string of (partial) Python code.
...
...     Returns a tuple (matching, mismatching).
...
...     matching is a list of tuples of matching TokenInfo objects for
...     matching parentheses/braces.
...
...     mismatching is a list of TokenInfo objects for mismatching
...     parentheses/braces.
...     """
...     stack = []
...     matching = []
...     mismatching = []
...     try:
...         for tok in tokenize_string(s):
...             exact_type = tok.exact_type
...             if exact_type == tokenize.ERRORTOKEN and tok.string[0] in '"\'':
...                 # There is an unclosed string. If we do not break here,
...                 # tokenize will tokenize the stuff after the string
...                 # delimiter.
...                 break
...             elif exact_type in braces:
...                 stack.append(tok)
...             elif exact_type in braces.values():
...                 if not stack:
...                     mismatching.append(tok)
...                     continue
...                 prevtok = stack.pop()
...                 if braces[prevtok.exact_type] == exact_type:
...                     matching.append((prevtok, tok))
...                 else:
...                     mismatching.insert(0, prevtok)
...                     mismatching.append(tok)
...             else:
...                 continue
...     except tokenize.TokenError:
...         # Either unclosed brace (what we are trying to handle here), or
...         # unclosed multi-line string (which we don't care about).
...         pass
...
...     matching.reverse()
...
...     # Anything remaining on the stack is mismatching. Keep the mismatching
...     # list in order.
...     stack.reverse()
...     mismatching = stack + mismatching
...     return matching, mismatching
```


```py
>>> matching, mismatching = matching_parens("('a', {(1, 2)}, ]")
>>> matching # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
[(TokenInfo(..., string='{', ...), TokenInfo(..., string='}', ...)),
 (TokenInfo(..., string='(', ...), TokenInfo(..., string=')', ...))]
>>> mismatching # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
[TokenInfo(..., string='(', ...), TokenInfo(..., string=']', ...)]
```

#### Exercise

Add a flag, `allow_intermediary_mismatches`, which when `True`, allows an
opening brace to still be considered matching if it is closed with the wrong
brace but later closed with the correct brace (`False` would give the current
behavior, that is, once an opening brace is closed with the wrong brace
it---and any unclosed braces before it---cannot be matched).

For example, consider `'[ { ] }'`. Currently, all the braces are considered
mismatched.

```py
>>> matching, mismatching = matching_parens('[ { ] }')
>>> matching
[]
>>> mismatching # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
[TokenInfo(..., string='[', ...),
 TokenInfo(..., string='{', ...),
 TokenInfo(..., string=']', ...),
 TokenInfo(..., string='}', ...)]
```

With `allow_intermediary_mismatches` set to `True`, the `{` and `}` should be
considered matching.

```py
>>> matching, mismatching = matching_parens('[ { ] }',
... allow_intermediary_mismatches=True) # doctest: +SKIP
>>> matching # doctest: +SKIP
[(TokenInfo(..., string='{', ...),
 TokenInfo(..., string='}', ...))]
>>> mismatching # doctest: +SKIP
[TokenInfo(..., string='[', ...),
 TokenInfo(..., string=']', ...)]
```

Furthermore, with `'[ { ] } ]'` only the middle `]` would be considered
mismatched (with the current version, all would be mismatched).

```py
>>> matching, mismatching = matching_parens('[ { ] } ]',
... allow_intermediary_mismatches=True) # doctest: +SKIP
>>> matching # doctest: +SKIP
[(TokenInfo(..., string='[', ...), TokenInfo(..., string=']', start=(1, 8), ...)),
 (TokenInfo(..., string='{', ...), TokenInfo(..., string='}', ...))]
>>> mismatching # doctest: +SKIP
[TokenInfo(..., string=']', start=(1, 4), ...)]
>>> # The current version, which would be allow_intermediary_mismatches=False
>>> matching, mismatching = matching_parens('[ { ] } ]')
>>> matching
[]
>>> mismatching # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
[TokenInfo(..., string='[', ...),
 TokenInfo(..., string='{', ...),
 TokenInfo(..., string=']', ...),
 TokenInfo(..., string='}', ...),
 TokenInfo(..., string=']', ...)]
```

The current behavior (`allow_intermediary_mismatches=False`) is a more
technically correct version, but `allow_intermediary_mismatches=True` would
provide more useful feedback for applications that might use this function to
highlight mismatching braces, as it would be more likely to highlight only the
"mistake" braces.

Since this exercise is relatively difficult, I'm providing the solution. I
recommend trying to solve it yourself first, as it will really force you to
understand how the function works.

<details>
<summary>Click here to show the solution</summary>

No really, do try it yourself first. At least think about it.

<details>
<summary>I've thought about it. Show the solution</summary>

Replace

```py
mismatching.insert(0, prevtok)
mismatching.append(tok)
```

with

```py
if allow_intermediary_mismatches:
    stack.append(prevtok)
else:
    mismatching.insert(0, prevtok)
mismatching.append(tok)
```

In this code block, `tok` is a closing brace and `prevtok` is the most
recently found opening brace (`stack.pop()`). Under the current code, we
append both braces to the `mismatching` list (keeping their order), and we
continue to do that with `allow_intermediary_mismatches=False`. However, if
`allow_intermediary_mismatches=True`, we instead put the `prevtok` back on the
stack, and still put the `tok` in the `mismatching` list. This allows
`prevtok` to be matched by a closing brace later.

For example, suppose we have `( } )`. We first append `(` to the stack, so the
stack is `['(']`. Then when we get to `}`. We pop `(` from the stack, and see
that it doesn't match. If `allow_intermediary_mismatches=False`, we consider
these both to be mismatched, and add them to the `mismatched` list in the
correct order (`['(', '}']`). If `allow_intermediary_mismatches=True`, though,
we only add `'}'` to the `mismatched` list and put `(` back on the stack.

Then we get to `)`. In the `allow_intermediary_mismatches=False` case, the
stack will be empty, so it will not be considered matching, and thus be placed
in the `mismatching` list (the `if not stack:` block prior to the code we
modified). In the `allow_intermediary_mismatches=True` case, the stack is
`['(']`, so `prevtok` will be `(`, which matches the `)`, so they are both put
in the `matching` list.

</details>
</details>


## Modifying Tokens

These examples show some ways that you can modify the token stream.

The general pattern we will apply here is to get the token stream from
`tokenize()`, modify it in some way, and convert it back to a bytes string
with [`untokenize()`](untokenize).

When new tokens are added, [`untokenize()`](untokenize) does not maintain
whitespace between tokens in a human-readable way. Doing this is possible, by
keeping track of column offsets, but we will not bother with it here except
where it is convenient. See the discussion in the [`untokenize()`](untokenize)
section.

### Converting `^` to `**`

Python's syntax uses `**` for exponentiation, although many might expect it to
use `^` instead. `^` is actually the [XOR
operator](https://docs.python.org/3/reference/expressions.html#binary-bitwise-operations).

```py
>>> bin(0b101 ^ 0b001)
'0b100'
```

Suppose you don't care about XOR, and want to allow `^` to represent
exponentiation. You might think to use the `ast` module and replace
[`BitXor`](https://greentreesnakes.readthedocs.io/en/latest/nodes.html#BitXor)
nodes with
[`Pow`](https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Pow), but
this will not work, because `^` has a different precedence than `**`:

```py
>>> import ast
>>> ast.dump(ast.parse('x**2 + 1')) # doctest: +SKIP35, +SKIP36, +SKIP37
"Module(body=[Expr(value=BinOp(left=BinOp(left=Name(id='x', ctx=Load()), op=Pow(), right=Constant(value=2, kind=None)), op=Add(), right=Constant(value=1, kind=None)))], type_ignores=[])"
>>> ast.dump(ast.parse('x^2 + 1')) # doctest: +SKIP35, +SKIP36, +SKIP37
"Module(body=[Expr(value=BinOp(left=Name(id='x', ctx=Load()), op=BitXor(), right=BinOp(left=Constant(value=2, kind=None), op=Add(), right=Constant(value=1, kind=None))))], type_ignores=[])"
```

This is difficult to read, but it basically says that `x**2 + 1` is parsed
like `(x**2) + 1` and `x^2 + 1` is parsed like `x^(2 + 1)`. There's no way to
distinguish the two in the AST representation, because it does not keep track
of redundant parentheses.

We could do a simple `s.replace('^', '**')`, but this would [also
replace](regular-expressions) any occurrences of `^` in
strings and comments.

Instead, we can use `tokenize`. The replacement is quite easy to do:

```py
>>> def xor_to_pow(s):
...     result = []
...     for tok in tokenize_string(s):
...         if tok.type == tokenize.ENCODING:
...             encoding = tok.string
...         if tok.exact_type == tokenize.CIRCUMFLEX: # CIRCUMFLEX is ^
...             result.append((tokenize.OP, '**'))
...         else:
...             result.append(tok)
...     return tokenize.untokenize(result).decode(encoding)
...
>>> xor_to_pow('x^2 + 1')
'x**2 +1 '
```

Because we are replacing a 1-character token with a 2-character token,
[`untokenize()`](untokenize) removes the
original whitespace and replaces it with its own. An exercise for the reader
is to redefine the column offsets for the new token and all subsequent tokens
on that line to avoid this issue.

(wrapping-floats-with-decimal-decimal)=
### Wrapping floats with `decimal.Decimal`

This example is modified from the [example in the standard library
docs](https://docs.python.org/3/library/tokenize.html#examples) for
`tokenize`. It is a good example for modifying tokens because the logic is not
too complex, and it is something that is not possible to do with other tools
such as the `ast` module, because `ast` does not keep the full precision of
floats as they are in the input.

```py
>>> def float_to_decimal(s):
...     result = []
...     for tok in tokenize_string(s):
...         if tok.type == tokenize.ENCODING:
...             encoding = tok.string
...         # A float is a NUMBER token with a . or e (scientific notation)
...         if tok.type == tokenize.NUMBER and '.' in tok.string or 'e' in tok.string.lower():
...             result.extend([
...                 (tokenize.NAME, 'Decimal'),
...                 (tokenize.OP, '('),
...                 (tokenize.STRING, repr(tok.string)),
...                 (tokenize.OP, ')')
...             ])
...         else:
...             result.append(tok)
...     return tokenize.untokenize(result).decode(encoding)
```

This works like this

```py
>>> 1e-1000 + 1.000000000000000000000000000000001
1.0
>>> float_to_decimal('1e-1000 + 1.000000000000000000000000000000001')
"Decimal ('1e-1000')+Decimal ('1.000000000000000000000000000000001')"
```

Notice that because new tokens were added as length 2 tuples, the whitespace
of the result is not the same as the input, and does not really follow [PEP
8](https://www.python.org/dev/peps/pep-0008/).

The transformed code can produce arbitrary precision decimals. Note that the
`decimal` module still requires setting the context precision high enough to
avoid rounding the input. An exercise for the reader is to extend
`float_to_decimal` to determine the required precision automatically.

```py
>>> from decimal import Decimal, getcontext
>>> getcontext().prec = 1001
>>> eval(float_to_decimal('1e-1000 + 1.000000000000000000000000000000001'))
Decimal('1.0000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001')
```

(extending-pythons-syntax)=
### Extending Python's Syntax

Because `tokenize()` emits [`ERRORTOKEN`](errortoken) on any
unrecognized operators, it can be used to add extensions to the Python syntax.
This can be challenging to do in general, as you may need to do significant
parsing of the tokens to ensure that your new "operator" has the correct
precedence.

You can find some more advanced examples of extending Python's syntax in
SymPy's [parser
module](https://github.com/sympy/sympy/blob/master/sympy/parsing/sympy_parser.py),
for example, implicit multiplication (`x y` ⮕ `x*y`), implicit function
application (`sin x` ⮕ `sin(x)`), factorial notation (`x!` ⮕ `factorial(x)`),
and more.

#### Emoji Math

The below example is relatively simple. It allows the "emoji" mathematical
symbols ➕, ➖, ➗, and ✖ to be used instead of their ASCII counterparts.

```py
>>> emoji_map = {
...     '➕': '+',
...     '➖': '-',
...     '➗': '/',
...     '✖': '*',
... }
>>> def emoji_math(s):
...     result = []
...     for tok in tokenize_string(s):
...         if tok.type == tokenize.ENCODING:
...             encoding = tok.string
...         if tok.type == tokenize.ERRORTOKEN and tok.string in emoji_map:
...             new_tok = (tokenize.OP, emoji_map[tok.string], *tok[2:])
...             result.append(new_tok)
...         else:
...             result.append(tok)
...     return tokenize.untokenize(result).decode(encoding)
...
>>> emoji_math('1 ➕ 2 ➖ 3➗4✖5')
'1 + 2 - 3/4*5'
```

Because we are replacing a single character with a single character, we can
use 5-tuples and keep the column offsets intact, making
[`untokenize()`](untokenize) maintain the whitespace of the input.


```{note}
These emoji may often appear as two characters, for instance, ✖ may often
appear instead as ✖️, which is ✖ (`HEAVY MULTIPLICATION X`) + (`VARIATION
SELECTOR-16`). The `VARIATION SELECTOR-16` is an invisible character which
forces it to render as an emoji. The above example does not include the
`VARIATION SELECTOR-16`. An exercise for the reader is to modify the above
function to work with this.
```

<!-- https://github.com/executablebooks/MyST-Parser/issues/181 -->
(backporting-underscores)=
#### Backporting Underscores in Numeric Literals

Python 3.6 added a new syntactic feature that allows [underscores in numeric
literals](https://docs.python.org/3/whatsnew/3.6.html#pep-515-underscores-in-numeric-literals).
To quote the docs, "single underscores are allowed between digits and after
any base specifier. Leading, trailing, or multiple underscores in a row are
not allowed."

For example,

```py
>>> # Python 3.6+ only
>>> 123_456 # doctest: +SKIP35
123456
```

We can write a function using `tokenize` to backport this feature to Python
3.5. Some experimentation shows how the new literals tokenize in Python 3.5:

- `123_456` tokenizes as [`NUMBER`](number) (`123`) and
  [`NAME`](name) (`_456`). In general, multiple underscores
  between tokens will tokenize like this.

- Additionally, underscores are allowed after base specifiers, like `0x_1`.
  This also tokenizes as [`NUMBER`](number) (`0`) and
  [`NAME`](name) (`x_1`). Since [`NUMBER`](number) and
  [`NAME`](name) tokens cannot appear next to one another in valid
  Python, we can simply combine them when they do.

- Finally, if an underscore appears before the `.` in a floating point
  literal, like `1_2.3_4` it will tokenize [`NUMBER`](number)
  (`1`), [`NAME`](name) (`_2`), [`NUMBER`](number)
  (`.3`), [`NAME`](name) (`_4`).

Note that in this example, the [`ENCODING`](encoding) token allows
us to access `result[-1]` unconditionally, as we know there must always be at
least this token already processed before any [`NAME`](name)
token. This is often a useful property the [`ENCODING`](encoding)
allows us to take advantage of.

We do some basic checks here to not allow spaces before underscores and double
underscores, which are not allowed in Python 3.6. But for simplicity, this
function takes a [garbage in, garbage
out](https://en.wikipedia.org/wiki/Garbage_in,_garbage_out) approach. Invalid
syntax in Python 3.6, like `123a_bc`, will transform to something that is
still invalid syntax in Python 3.5 (`123abc`).

```py
>>> import sys
>>> def underscore_literals(s):
...     if sys.version_info >= (3, 6):
...         return s
...
...     result = []
...     for tok in tokenize_string(s):
...         if tok.type == tokenize.ENCODING:
...             encoding = tok.string
...         if tok.type == tokenize.NAME and result[-1].type == tokenize.NUMBER:
...             # Check that there are no spaces between the tokens
...             # e.g., 123 _456 is not allowed, and there aren't multiple
...             # consecutive undercores, e.g., 123__456 is not allowed.
...             if result[-1].end == tok.start and '__' not in tok.string:
...                 new_tok = tokenize.TokenInfo(
...                     tokenize.NUMBER,
...                     result[-1].string + tok.string.replace('_', ''),
...                     result[-1].start,
...                     tok.end,
...                     tok.line,
...                     )
...                 result[-1] = new_tok
...                 continue
...         if tok.type == tokenize.NUMBER and tok.string[0] == '.' and result[-1].type == tokenize.NUMBER:
...             # Float with underscore before the ., like 1_2.0, which is 1, _2, .0
...             if result[-1].end == tok.start:
...                 new_tok = tokenize.TokenInfo(
...                     tokenize.NUMBER,
...                     result[-1].string + tok.string,
...                     result[-1].start,
...                     tok.end,
...                     tok.line,
...                 )
...                 result[-1] = new_tok
...                 continue
...         if tok.exact_type == tokenize.DOT and result[-1].type == tokenize.NUMBER:
...             # Like 1_2. which becomes 1, _2, .
...             if result[-1].end == tok.start:
...                 new_tok = tokenize.TokenInfo(
...                     tokenize.NUMBER,
...                     result[-1].string + tok.string,
...                     result[-1].start,
...                     tok.end,
...                     tok.line,
...                 )
...                 result[-1] = new_tok
...                 continue
...
...         result.append(tok)
...     return tokenize.untokenize(result).decode(encoding)
...
```

Note that by reusing the [`start`](start-and-end) and [`end`](start-and-end)
tokens, we are able to make [`untokenize()`](untokenize) keep the whitespace,
even though characters were removed. [`untokenize()`](untokenize) only uses
the differences between [`end`](start-and-end) and [`start`](start-and-end) to
determine how many spaces to add between tokens, not their absolute values
(remember that [`untokenize()`](untokenize) only requires the
[`start`](start-and-end) and [`end`](start-and-end) tuples to be
nondecreasing; it doesn't care if the actual column values are correct).

```py
>>> s = '1_0 + 0b_101 + 0o_1_0 + 0x_a - 1.0_0 + 1e1 + 1.0_0j + 1_2.3_4 + 1_2.'
>>> # In Python 3.5
>>> underscore_literals(s) # doctest: +SKIP36, +SKIP37, +SKIP38
'10 + 0b101 + 0o10 + 0xa - 1.00 + 1e1 + 1.00j + 12.34 + 12.'
```
