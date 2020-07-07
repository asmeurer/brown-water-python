What is Tokenization?
=====================

In the field of parsing, a
[*tokenizer*](https://en.wikipedia.org/wiki/Lexical_analysis), also called a
*lexer*, is a program that takes a string of characters and splits it into
tokens. A token is a substring that has semantic meaning in the grammar of the
language.

An example should clarify things. Consider the string of partial Python code,
`("a") + True -`.

``` py
>>> import tokenize
>>> import io
>>> string = '("a") + True -\n'
>>> for tok in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
...     print(tok)
TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
TokenInfo(type=54 (OP), string='(', start=(1, 0), end=(1, 1), line='("a") + True -\n')
TokenInfo(type=3 (STRING), string='"a"', start=(1, 1), end=(1, 4), line='("a") + True -\n')
TokenInfo(type=54 (OP), string=')', start=(1, 4), end=(1, 5), line='("a") + True -\n')
TokenInfo(type=54 (OP), string='+', start=(1, 6), end=(1, 7), line='("a") + True -\n')
TokenInfo(type=1 (NAME), string='True', start=(1, 8), end=(1, 12), line='("a") + True -\n')
TokenInfo(type=54 (OP), string='-', start=(1, 13), end=(1, 14), line='("a") + True -\n')
TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 14), end=(1, 15), line='("a") + True -\n')
TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
```

The string is split into the following tokens: `(`, `"a"`, `)`, `+`, `True`, and
`-` (ignore the `BytesIO` bit and the `ENCODING` and `ENDMARKER` tokens for
now).

I chose this example to demonstrate a few things:

-   The *Tokens* in Python are things like parentheses, strings, operators,
    keywords, and variable names.

-   Every token is a represented by `namedtuple` called `TokenInfo`, which has
    a `type`, represented by an integer constant, and a `string`, which is the
    substring of the input representing the given token. The `namedtuple` also
    gives line and column information that indicates exactly where in the
    input string the token was found.

-   The input does not need to be valid Python. Our input, `("a") + True -` is
    not valid Python. It is, however, a potential beginning of a valid Python
    string. If a valid Python expression were to be added to the end of the
    input, completing the subtraction operator, such as `("a") + True - x`, it
    would become valid Python. **This illustrates an important aspect of
    tokenize, which is that it fundamentally works on a stream of
    characters.** This means that tokens are output as they are seen, without
    regard to what comes later (the tokenize module does do lookahead on the
    input stream internally to ensure that the correct tokens are output, but
    from the point of view of a user of `tokenize`, each token can be
    processed as it is seen). This is why `tokenize.tokenize` produces a
    generator.

    However, it should be noted that tokenize does raise
    [exceptions](exceptions) on certain incomplete or invalid
    Python statements. For example, if we omit the closing parenthesis,
    tokenize produces all the tokens as before, but then raises `TokenError`:

    <!-- We have to skip this doctest, as it doesn't support output and an
    exception in the same snippet. -->

    ```py
    >>> string = '("a" + True -'
    >>> for tok in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
    ...     print(tok) # doctest: +SKIP
    TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
    TokenInfo(type=54 (OP), string='(', start=(1, 0), end=(1, 1), line='("a" + True -')
    TokenInfo(type=3 (STRING), string='"a"', start=(1, 1), end=(1, 4), line='("a" + True -')
    TokenInfo(type=54 (OP), string='+', start=(1, 5), end=(1, 6), line='("a" + True -')
    TokenInfo(type=1 (NAME), string='True', start=(1, 7), end=(1, 11), line='("a" + True -')
    TokenInfo(type=54 (OP), string='-', start=(1, 12), end=(1, 13), line='("a" + True -')
    Traceback (most recent call last):
    ...
    tokenize.TokenError: ('EOF in multi-line statement', (2, 0))
    ```

    One of the goals of this guide is to quantify exactly when these error
    conditions can occur, so that code that attempts to tokenize partial
    Python code can deal with them properly.

-   Syntactically irrelevant aspects of the input such as redundant
    parentheses are maintained. The parentheses around the `"a"` in the input
    string are completely unnecessary, but they are included as tokens anyway.
    This does not apply to whitespace, however
    ([indentation](indent) is an exception to this, as we will see
    later), although the whitespace between tokens can generally be deduced
    from the additional information procided in the `TokenInfo`.

-   The input need not be semantically meaningful in anyway. The input string,
    even if completed, can only raise a `TypeError` because `"a" + True` is
    not allowed by Python. The tokenize module does not know or care about
    objects, types, or any high-level Python constructs.

-   Some tokens can be right next to one another in the input string. Other
    tokens must be separated by a space (for instance, `foriinrange(10)` will
    tokenize differently from `for i in range(10)`). The complete set of rules
    for when spaces are required or not required to separate Python tokens is
    quite
    [complicated](https://docs.python.org/3/reference/lexical_analysis.html),
    especially when multi-line statements with indentation are considered (as
    an example, consider that `1jand2` is valid Python---it's tokenized
    into three tokens, `NUMBER` (`1j`), `NAME` (`and`), and `NUMBER` (`2`)).
    One use-case of the `tokenize` module is to combine tokens into valid
    Python using the [`untokenize`](untokenize)
    function, which handles these details automatically.

-   All parentheses and operators are tokenized as [`OP`](op). Both variable
    names and keywords are tokenized as [`NAME`](name). To determine the exact
    type of a token often requires further inspection than simply looking at
    the `type` (this guide will detail exactly how to do this).

-   The above example does not show it, but even code that can never be valid
    Python is often tokenized. For example:

    ```py
    >>> string = 'a$b\n'
    >>> for tok in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
    ...     print(tok)
    TokenInfo(type=62 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
    TokenInfo(type=1 (NAME), string='a', start=(1, 0), end=(1, 1), line='a$b\n')
    TokenInfo(type=59 (ERRORTOKEN), string='$', start=(1, 1), end=(1, 2), line='a$b\n')
    TokenInfo(type=1 (NAME), string='b', start=(1, 2), end=(1, 3), line='a$b\n')
    TokenInfo(type=4 (NEWLINE), string='\n', start=(1, 3), end=(1, 4), line='a$b\n')
    TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')
    ```

    This can be useful for dealing with code that has minor typos that makes
    it invalid. It can also be used to build modules that extend the Python
    language in limited ways, but be warned that the `tokenize` module makes
    no guarantees about how it tokenizes invalid Python. For example, if a
    future version of Python added `$` as an operator, the above string could
    tokenize completely differently. This exact thing happened, for instance,
    with f-strings. In Python 3.5, `f"{a}"` tokenizes as two tokens, `NAME`
    (`f`) and `STRING` (`"{a}"`). In Python 3.6, it tokenizes as one token,
    `STRING` (`f"{a}"`).

-   Finally, the key thing to understand about tokenization is that tokens are
    a very low level abstraction of the Python syntax. The same token may have
    different meanings in different contexts. For example, in `[1]`, the `[`
    token is part of a list literal, whereas in `a[1]`, the `[` token is part
    of a slice. If you want to manipulate higher level abstractions, you might
    want to use the `ast` module instead (see the [next
    section](alternatives.md)).

This guide does not detail how things are tokenized, that is, how `tokenize`
chooses which tokens to use for a given input string, except in the ways that
this matters as an end-user of `tokenize`. For details on how Python is lexed,
see the page on [lexical
analysis](https://docs.python.org/3/reference/lexical_analysis.html) in the
official Python documentation.
