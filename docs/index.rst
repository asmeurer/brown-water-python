=====================================================================
 Brown Water Python: Better Docs for the Python ``tokenize`` Module.
=====================================================================

The ``tokenize`` module in the Python standard library is very powerful, but
its `documentation <https://docs.python.org/3/library/tokenize.html>`_ is
somewhat limited. In the spirit of the `Green Tree Snakes
<https://greentreesnakes.readthedocs.io/>`_ project, which provides similar
extended documentation for the ``ast`` module, I am providing here some
extended documentation for effectively working with the ``tokenize`` module.

.. note::

   This document is currently a work in progress. I plan to add more, but any
   feedback on what I already have or what you'd like to see is welcome. Feel
   free to `open an issue
   <https://github.com/asmeurer/brown-water-python/issues>`_ or pull request
   about anything (questions, comments on what you'd like to see, corrections,
   etc.).

Python Versions Supported
=========================


The contents of this guide apply to Python 3.5 and up. Several minor changes
were made to the ``tokenize`` module in Python 3.7, and they have been noted
where appropriate.

The ``tokenize`` module tokenizes code according to the version of Python that
it is being run under. For example, some new syntax features in 3.6 affect
tokenization (particularly, `f-strings
<https://docs.python.org/3.6/whatsnew/3.6.html#pep-498-formatted-string-literals>`_
and `underscores in numeric literals
<https://docs.python.org/3.6/whatsnew/3.6.html#pep-515-underscores-in-numeric-literals>`_).
For example, ``123_456`` will tokenize as a single token in Python 3.6+,
``NUMBER`` (``123_456``), but in Python 3.5, it tokenizes as two tokens,
``NUMBER`` (``123``) and ``NAME`` (``_456``) (this will also be invalid syntax
in any context). See `the example <tokens.html#number>`_ in the ``NUMBER``
reference.

Most of what is written here will also apply to earlier Python 3 versions, with
obvious exceptions (like tokens that were added for new syntax).

I don't have any interest in supporting Python 2 in this guide. `Its lifetime
<https://devguide.python.org/#status-of-python-branches>`_ is quickly coming
to an end, so you should strongly consider being Python 3-only for most new
code that is written.

With that being said, I will point out one important difference in Python 2:
the ``tokenize()`` function in Python 2 *prints* the tokens instead of
returning them. Instead, you should use the ``generate_tokens()`` function,
which works like ``tokenize()`` in Python 3 (see the `docs
<https://docs.python.org/2.7/library/tokenize.html>`_).

.. doctest::

   >>> # Python 2.7 tokenize example
   >>> import tokenize
   >>> import io
   >>> for tok in tokenize.generate_tokens(io.BytesIO('1 + 2').readline):
   ...     print tok # doctest: +SKIP
   ...
   (2, '1', (1, 0), (1, 1), '1 + 2')
   (51, '+', (1, 2), (1, 3), '1 + 2')
   (2, '2', (1, 4), (1, 5), '1 + 2')
   (0, '', (2, 0), (2, 0), '')

Also, the result of
this function is a regular tuple, not a ``namedtuple``, so you will not be
able to use attributes to access the members. Instead use something like ``for
toknum, tokval, start, end, line in tokenize.generate_tokens(...):`` (this
pattern is recommended in Python 3 as well, see the `Usage <usage.html>`_ section).

Table of Contents
=================

.. toctree::
   :maxdepth: 3

   intro
   alternatives
   usage
   tokens


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
