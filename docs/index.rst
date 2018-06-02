Brown Water Python
==================

Some better docs for the Python ``tokenize`` module.

The ``tokenize`` module in the Python standard library is very powerful, but
its `documentation <LINK>`_ is somewhat limited. In the spirit of the `Green
Tree Snakes <LINK>`_ project, which provides similar extended documentation
for the ``ast`` module, I am providing here some extended documentation for
effectively working with the ``tokenize`` module.

What is tokenization?
---------------------

In the field of parsing, a `*tokenizer*
<https://en.wikipedia.org/wiki/Lexical_analysis>`_, also called a *lexer*,
takes a string of characters and splits it into tokens. A token is a substring
that has semantic meaning in the grammar of the language.

An example should clarify things. Consider the string of Python code, ``("a") +
True -``.

.. code:: python

   >>> import tokenize
   >>> import io
   >>> string = '("a") + True -'
   >>> for token in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
   ...     print(token)
   TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
   TokenInfo(type=53 (OP), string='(', start=(1, 0), end=(1, 1), line='("a") + True -')
   TokenInfo(type=3 (STRING), string='"a"', start=(1, 1), end=(1, 4), line='("a") + True -')
   TokenInfo(type=53 (OP), string=')', start=(1, 4), end=(1, 5), line='("a") + True -')
   TokenInfo(type=53 (OP), string='+', start=(1, 6), end=(1, 7), line='("a") + True -')
   TokenInfo(type=1 (NAME), string='True', start=(1, 8), end=(1, 12), line='("a") + True -')
   TokenInfo(type=53 (OP), string='-', start=(1, 13), end=(1, 14), line='("a") + True -')
   TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

The string is split into the following tokens: ``(``, ``"a"``, ``+``,
``True``, ``)`` (ignore the ``BytesIO`` bit and the ``ENCODING`` and
``ENDMARKER`` tokens for now).

I chose this example to demonstrate a few things:

- *Tokens* are parentheses, strings, operators, keywords, and variable names.

- Every token is a named tuple which has a ``type``, which is represented by
  an integer constant, and a ``string``, which is the substring of the input
  representing the given token. The namedtuple also gives line and column
  information that indicates exactly where in the input string the token was
  found.

- The input does not need to be valid Python. Out input string, ``("a") + True
  -`` is not valid Python. It is however, a potential beginning of a valid
  Python. If a valid Python expression were to be added to the end of the
  input, completing the subtraction operator, such as ``("a") + True - x`` it
  would become valid Python. **This illustrates an important aspect of
  ``tokenize``, which is that it fundamentally works on a stream of
  characters.**. This means that tokens are output as they are seen, without
  regard to what comes later (the tokenize module does do lookahead on the
  input stream internally to ensure that the correct tokens are output, but
  from the point of view of a user of ``tokenize``, each token can be
  processed as it is seen. This is why ``tokenize.tokenize`` produces a
  generator.

  However, it should be noted that tokenize does raise an exception on certain
  incomplete Python statements. For example, if we omit the closing
  parenthesis, tokenize produces all the tokens as before, but then raises
  ``TokenError``:

  .. code:: python

     >>> for token in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
     ...     print(token)
     TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
     TokenInfo(type=53 (OP), string='(', start=(1, 0), end=(1, 1), line='("a" + True -')
     TokenInfo(type=3 (STRING), string='"a"', start=(1, 1), end=(1, 4), line='("a" + True -')
     TokenInfo(type=53 (OP), string='+', start=(1, 5), end=(1, 6), line='("a" + True -')
     TokenInfo(type=1 (NAME), string='True', start=(1, 7), end=(1, 11), line='("a" + True -')
     TokenInfo(type=53 (OP), string='-', start=(1, 12), end=(1, 13), line='("a" + True -')
     Traceback (most recent call last):
       File "<stdin>", line 1, in <module>
       File "/Users/aaronmeurer/anaconda3/lib/python3.5/tokenize.py", line 597, in _tokenize
         raise TokenError("EOF in multi-line statement", (lnum, 0))
     tokenize.TokenError: ('EOF in multi-line statement', (2, 0))

  One of the goals of this guide is to quantify exactly when these error
  conditions can occur, so that code that attempts to tokenize partial Python
  code can deal with them properly.

- Syntactically irrelevant aspects of the input such as redundant parentheses
  are maintained. The parentheses around the ``"a"`` in the input string are
  completely unnecessary, but they are included as tokens anyway. This does
  not apply to whitespace, however (indentation is an exception to this, as we
  will see later), although the whitespace between tokens can generally be
  deduced from the column information in the namedtuple.

- The input need not be semantically meaningful in anyway. The input string,
  even if completed, can only raise a ``TypeError`` because ``"a" + True`` is
  not allowed by Python. The tokenize module does not know or care about
  objects, types, or any high-level Python constructs.

- Some tokens can be right next to one another in the input string. Other
  tokens must be separated by a space (for instance, ``foriinrange(10)`` will
  tokenize differently from ``for i in range(10)``). The complete set of rules
  for when spaces are required or not required to separate Python tokens is
  quite complicated, especially when multiline statements with indentation are
  considered (as an example, consider that ``1jand2`` is valid Python and is
  tokenized into three tokens, ``NUMBER`` (``1j``), ``NAME`` (``and``), and
  ``NUMBER`` (``2``)). One potential use-case of ``tokenize`` is to combine
  tokens into valid Python using the ``untokenize`` function, which handles
  whitespace between tokens automatically.

- All parentheses and operators are tokenized as ``OP``. Both variable names
  and keywords are tokenized as ``NAME``. To determine the exact type of a
  token often requires further inspection than simply looking at the ``type``
  (this guide will detail exactly how to do this).

- The above example does not show it, but even code that can never be valid
  Python is often tokenized. For example:

  .. code:: python

     >>> string = 'a$b'
     >>> for token in tokenize.tokenize(io.BytesIO(string.encode('utf-8')).readline):
     ...     print(token)
     TokenInfo(type=59 (ENCODING), string='utf-8', start=(0, 0), end=(0, 0), line='')
     TokenInfo(type=1 (NAME), string='a', start=(1, 0), end=(1, 1), line='a$b')
     TokenInfo(type=56 (ERRORTOKEN), string='$', start=(1, 1), end=(1, 2), line='a$b')
     TokenInfo(type=1 (NAME), string='b', start=(1, 2), end=(1, 3), line='a$b')
     TokenInfo(type=0 (ENDMARKER), string='', start=(2, 0), end=(2, 0), line='')

  This can be useful for dealing with code that has minor typos that make if
  invalid. It can also be used to build modules that extend the Python
  language in limited ways, but be warned that the tokenize module makes no
  guarantees about how it tokenizes invalid Python. For example, if a future
  version of Python added ``$`` as an operator, the above string could
  tokenize completely differently. This exactly thing happened, for instance,
  with f-strings. ``f"{a}"`` tokenizes as two tokens, ``NAME`` and ``STRING``,
  in Python 3.5, and as one token, ``STRING``, in Python 3.6.

``tokenize`` vs. alternatives
-----------------------------

There are generally three methods one might use when trying to find or modify
syntatic constructs in Python source code:

- Naive matching with regular expression
- Using a lexical tokenizer (i.e., the ``tokenize`` module)
- Using an abstract syntax tree (AST) (i.e, the ``ast`` module)

Suppose you wanted to write a tool that takes a piece of Python code and
prints the line number of every function definition, that is, every occurrence
of the ``def`` keyword. Such a tool could be used by a text editor to aid in
jumping to function definitions.

Regular expressions
~~~~~~~~~~~~~~~~~~~

Using naive regular expression parsing, you might start with something like

.. code:: python

   >>> import re
   >>> FUNCTION = re.compile(r'def ')

then use the ``finditer`` method to find all instances and print their line
numbers.


.. code:: python

   >>> def line_numbers_regex(inputcode):
   ...     for lineno, line in enumerate(inputcode.splitlines(), 1):
   ...         if FUNCTION.match(line):
   ...             print(lineno)
   ...
   >>> code = """\
   ... def f(x):
   ...     pass
   ...
   ... class MyClass:
   ...     def g(self):
   ...         pass
   ... """
   ...
   >>> line_numbers_regex(code)
   1
   4

You might notice some issues with this approach. First off, the regular
expression is not correct. It will also match lines like ``indef + 1``. You
could modify the regex to make it more correct, for instance, ``r'^ *def '``
(this is still not completely right; do you see why?).

But there is a more serious issue. Say you had a string template to generate
some Python code.

.. code:: python

   >>> code_tricky = '''\
   ... FUNCTION_SKELETON = """
   ... def {name}({args}):
   ...     {body}
   ... """
   ... '''

The regular expression would detect this as a function.

.. code:: python

   >>> line_numbers_regex(code_tricky)
   2

In general, it's impossible for a regular expression to distinguish between a
block of code that is in a string and a block of code that is syntactically
actually code.

Tokenize
~~~~~~~~

Now let's consider the tokenize module. Let's look at what it produces for the
above code:

   >>> def line_numbers_tokenize(inputcode):
   ...     for token in tokenize.tokenize(io.BytesIO(inputcode.encode('utf-8')).readline):
   ...         if token.type == tokenize.NAME and token.string == 'def':
   ...             print(token.start[0])
   ...
   >>> line_numbers_tokenize(code)
   1
   4
   >>> line_numbers_tokenize(code_tricky)

We see that it isn't fooled by the code that is in a string, because strings
are tokenized as separate entities.

As noted above, tokenize can handle incomplete or invalid Python. Our regex solution is
also capable of this. This can be a boon (code that is being input into a text
editor is generally incomplete if the user hasn't finished typing it yet), or
a bane (incorrect Python code, such as ``def`` used as a variable, could trick
the above function). It really depends on what your use-case is and what
trade-offs you are willing to accept.

It should also be note that the above function is not fully correct, as it
does not properly handle ``ERRORTOKEN``\ s or exceptions. We will see later how
to fix it.

AST
~~~

The ``ast`` module can also be used to avoid the pitfalls of detecting false
positives. In fact, the ``ast`` module will have NO false positives. The price
that is paid for this is that the input code to the ``ast`` module must be
completely valid Python code. Incomplete code will cause ``ast.parse`` to
raise a ``SyntaxError``.

.. code:: python

   >>> def line_number_ast(inputcode):
   ...     p = ast.parse(inputcode)
   ...     for node in ast.walk(p):
   ...         if isinstance(node, ast.FunctionDef):
   ...             print(node.lineno)
   >>> line_number_ast(code)
   1
   4
   >>> line_number_ast(code_tricky)
   >>> line_number_ast("""\
   ... def test():
   ... """)
   Traceback (most recent call last):
     ...
     File "<unknown>", line 1
       def test():
                 ^
   SyntaxError: unexpected EOF while parsing

Another thing to note about the ``ast`` module is that certain semantically
irrelevant constructs such as redundant parentheses and extraneous whitespace
are lost in the AST representation. This can be an advantage if you don't care
about them, or a disadvantage if you do. ``tokenize`` does not remove
redundant parentheses. It does remove whitespace, but it can easily be
reconstructed from the column offsets.


The following table outlines the differences regular expression matching,
``tokenize``, and ``ast``. No one is the correct solution. It depends on what
trade-offs you want to make between false positives, false negatives,
maintainability, and the ability or inability to work with invalid or
incomplete code. The table is not organized as "pros and cons" because
something may be a pro (like, ability to work with incomplete code) or a con
(like, accepts invalid Python).

.. list-table::
   :header-rows: 1

   * - Regular expressions
     - ``tokenize``
     - ``ast``
   * - Can work with incomplete or invalid Python
     - Can work with incomplete or invalid Python
     - Requires syntactically valid Python (with a few minor exceptions)
   * - Regular expressions can be difficult to write correctly and maintain
     - Token types are easy to detect. Larger patterns must be amalgamated
       from the tokens.
     - AST nodes represent high-level syntactic constructs.


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
