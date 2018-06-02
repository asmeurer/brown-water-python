.. _alternatives:

``tokenize`` vs. alternatives
-----------------------------

There are generally three methods one might use when trying to find or modify
syntatic constructs in Python source code:

- Naive matching with regular expression
- Using a lexical tokenizer (i.e., the ``tokenize`` module)
- Using an abstract syntax tree (AST) (i.e, the ``ast`` module)

Let us look at each of these three options to see the strengths and weaknesses
of each. Suppose you wanted to write a tool that takes a piece of Python code and
prints the line number of every function definition, that is, every occurrence
of the ``def`` keyword. Such a tool could be used by a text editor to aid in
jumping to function definitions, for instance.

Regular expressions
~~~~~~~~~~~~~~~~~~~

Using naive regular expression parsing, you might start with something like

.. doctest::

   >>> import re
   >>> FUNCTION = re.compile(r'def ')

Then using regular expression matching, find all lines that match and print
their line numbers.

.. doctest::

   >>> def line_numbers_regex(inputcode):
   ...     for lineno, line in enumerate(inputcode.splitlines(), 1):
   ...         if FUNCTION.search(line):
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
   5

You might notice some issues with this approach. First off, the regular
expression is not correct. It will also match lines like ``indef + 1``. You
could modify the regex to make it more correct, for instance, ``r'^ *def '``
(this is still not completely right; do you see why?).

But there is a more serious issue. Say you had a string template to generate
some Python code.

.. doctest::

   >>> code_tricky = '''\
   ... FUNCTION_SKELETON = """
   ... def {name}({args}):
   ...     {body}
   ... """
   ... '''

The regular expression would detect this as a function.

.. doctest::

   >>> line_numbers_regex(code_tricky)
   2

In general, it's very difficult, if not impossible, for a regular expression
to distinguish between a text that is inside a string and text that isn't.

This may or may not actually bother you, depending on your application.
Function definitions may not appear inside of strings very often, but other
code constructs appear in strings (and comments) quite often.

To quickly digress to a secondary example, the ``tokenize`` module can be used
to check if a piece of (incomplete) Python code has any mismatched parentheses
or braces. In this case, you definitely don't want to do a naive matching of
parentheses in the source as a whole, as a single "mismatched" parenthesis in
a string could confuse the entire engine, even if the source as Python is
itself valid. We will see this example in more detail later.

Tokenize
~~~~~~~~

Now let's consider the tokenize module. It's quite easy to search for the
``def`` keyword. We just look for ``NAME`` tokens where the token string is
``'def'``. Let's write a function that does this and look at what it produces
for the above code examples:

.. doctest::

   >>> import tokenize
   >>> import io
   >>> def line_numbers_tokenize(inputcode):
   ...     for token in tokenize.tokenize(io.BytesIO(inputcode.encode('utf-8')).readline):
   ...         if token.type == tokenize.NAME and token.string == 'def':
   ...             print(token.start[0])
   ...
   >>> line_numbers_tokenize(code)
   1
   5
   >>> line_numbers_tokenize(code_tricky) # No lines are printed

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
raise a ``SyntaxError``.\ [#]_

.. doctest::

   >>> import ast
   >>> def line_number_ast(inputcode):
   ...     p = ast.parse(inputcode)
   ...     for node in ast.walk(p):
   ...         if isinstance(node, ast.FunctionDef):
   ...             print(node.lineno)
   >>> line_number_ast(code)
   1
   5
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

If you want to learn more about the AST module, look at `Green Tree Snakes
<https://greentreesnakes.readthedocs.io/en/latest/>`_, which is a companion to
this guide for the Python ``ast`` module.

Summary
~~~~~~~

The following table outlines the differences between using regular expression
matching, ``tokenize``, and ``ast`` to find or modify constructs in Python
source code. No one method is the correct solution. It depends on what
trade-offs you want to make between false positives, false negatives,
maintainability, and the ability or inability to work with invalid or
incomplete code. The table is not organized as "pros and cons" because some
things may be pros (like, the ability to work with incomplete code) or cons
(like, accepting invalid Python), depending on what you are trying to do.

.. list-table::
   :header-rows: 1

   * - Regular expressions
     - ``tokenize``
     - ``ast``
   * - Can work with incomplete or invalid Python.
     - Can work with incomplete or invalid Python, though you may need to
       watch for ``ERRORTOKEN`` and exceptions.
     - Requires syntactically valid Python (with a few minor exceptions).
   * - Regular expressions can be difficult to write correctly and maintain.
     - Token types are easy to detect. Larger patterns must be amalgamated
       from the tokens.
     - AST has high-level abstractions such as ``ast.walk`` and
       ``NodeTransformer`` that make visiting and transforming nodes easy,
       even in complicated ways.
   * - Regular expressions work directly on the source code, so it is trivial
       to do lossless transformations with them.
     - Lossless transformations are possible with ``tokenize``, as all the
       whitespace can be inferred from the column offsets. However, it can
       often be tricky to do in practice (the ``untokenize`` function is not
       lossless).
     - Lossless transformations are impossible with ``ast``, as it completely
       drops whitespace, redundant parentheses, and comments (among other
       things).
   * - Impossible to detect edge cases in all circumstances, such as code that
       actually is inside of a string.
     - Edge cases can be avoided. Differentiates between actual code and code
       inside a string. Can still be fooled by invalid Python (though this can
       often be considered a `garbage in, garbage out
       <https://en.wikipedia.org/wiki/Garbage_in,_garbage_out>`_ scenario).
     - Edge cases can be avoided without effort, as only valid Python can even
       be parsed, and each node class represents that syntactic construct
       exactly.

As you can see, all three can be valid depending on what you are trying to do.
With that being said, I hope I can convince you at least that for most
use-cases where one might want to use naive string matching on Python code
using regular expressions, writing an equivalent method using the ``tokenize``
module will be more correct on edge cases, more maintainable, and easier to
extend.

As a final note, David Halter's `parso
<https://parso.readthedocs.io/en/latest/>`_ library contains an alternative
implementation of the standard library ``tokenize`` and ``ast`` modules for
Python. Parso has many advantages over the standard library, such as
round-trippable AST, the tokenize function has fewer "gotchas", the ability to
detect multiple syntax errors in a single block of code, the ability to parse
Python code for a different version of Python than the one that is running,
and more. If you don't mind an external dependency and want to save yourself
potential headaches, it is worth considering using ``parso`` instead of the
standard library ``tokenize`` or ``ast``.


.. [#] Actually there are a handful of syntax errors that cannot be detected
       by the AST due to their context sensitive nature, such as ``break``
       outside of a loop. These are found only after compiling the AST.
