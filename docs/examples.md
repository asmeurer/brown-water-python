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

## Processing tokens

These examples show different ways that you can process tokens.

### `inside_string()`

`inside_string(s, row, col)` takes the string `s` and determines if position
at `(row, col)` is inside a `STRING` token.

To simplify the example for the purposes of illustration, `inside_string`
returns `True` even if `(row, col)` is on the quote delimiter of the string,
or a prefix character (like `r` or `f`).


```py
>>> def inside_string(s, row, col):
...     """
...     Returns True if row, col is inside a string in s, False otherwise.
...
...     row starts at 1 and col starts at 0.
...     """
...     try:
...         for toknum, tokval, start, end, _ in tokenize_string(s):
...             if toknum == tokenize.ERRORTOKEN:
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

Let's walk through the code. We start with the loop


We don't want the function to raise `TokenError` on uncompleted delimiters or
unclosed multi-line strings, so we wrap the loop in a `try` block that excepts
[`tokenize.TokenError`](usage.html#tokenerror).

```py
try:
```

Next we have the main loop. We don't use the `line` attribute, so we use `_`
instead to indicate it isn't used.

```py
    for toknum, tokval, start, end, _ in tokenize_string(s):
```

The idea is to loop through the tokens until we find one that our `(row, col)`
is contained in (it is between the `start` and `end` tokens). This may not
actually happen, for instance, if the `(row, col)` is inside whitespace that
isn't tokenized.

The first thing to check for is [`ERRORTOKEN`](tokens.html#errortoken). If an
unclosed single quote (not multiline) string is encountered, that is, it is
closed by a newline, like

```
"an unclosed string
```

and we haven't reached our `(row, col)` yet, then we assume our `(row, col)`
is inside this unclosed string. This implicitly makes the rest of the document
part of the unclosed string. We could also easily modify this to only assume
the rest of the line is inside the unclosed string.


```py
         if toknum == tokenize.ERRORTOKEN:
             # There is an unclosed string. We haven't gotten to the
             # position yet, so it must be inside this string
             return True
```

Now we have the main condition. If the `(row, col)` is between `start` and
`end` of a token, we have gone as far as we need to.

```py
         if start <= (row, col) <= end:
```

That token is either a `STRING` token, in which case, we should return `True`,
or it is another token type, which means our `(row, col)` is not on a `STRING`
token and we can return `False`. This can be written as simply:

```py
             return toknum == tokenize.STRING
```

Now the exceptional case. If we see a [`TokenError`](usage.html#tokenerror),
we don't want the function to fail.

```py
except tokenize.TokenError as e:
```

Remember that there are two possibilities for a `TokenError`. If `'statement'`
is in the error message, there is an unclosed brace somewhere. This case also
only happens when `tokenize` has reached the end of the token stream, so if
the above checks haven't returned `True` yet, then `(row, col)` must not be
inside a `STRING` token, so we should return `False`.

If `'string'` is inside the error message, there is an unclosed multi-line
string. In this case, we want to check if we are inside this string. We can
check the start of the multiline string in the `TokenError`. Remember that the
message is in `e.args[0]` and the start is in `e.args[1]`. So we should return
`True` in this case if the `(row, col)` are after the `e.args[1]`, and `False`
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
... """, 2, 10) # 'n' in name
False
>>> # Check unclosed string delimieters
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

###
