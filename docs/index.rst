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


``tokenize`` vs. ``ast``
------------------------

There are generally three methods one might use when trying to find or modify
syntatic constructs in Python source code:

- Naive matching with regular expression
- Using a lexical tokenizer (i.e., the ``tokenize`` module)
- Using an abstract syntax tree (AST) (i.e, the ``ast`` module)

Suppose you wanted to write a tool that takes a piece of Python code and
prints the line number of every function definition, that is, every occurrence
of the ``def`` keyword. Such a tool could be used by a text editor to aid in
jumping to function definitions.

Using naive regular expression parsing, you might start with something like

.. code:: python

   >>> import re
   >>> FUNCTION = re.compile('def ')

then use the ``finditer`` method to find all instances and print their line
numbers.


.. code:: python

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
