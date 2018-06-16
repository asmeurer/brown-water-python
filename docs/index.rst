=====================================================================
 Brown Water Python: Better Docs for the Python ``tokenize`` Module.
=====================================================================

The ``tokenize`` module in the Python standard library is very powerful, but
its `documentation <https://docs.python.org/3/library/tokenize.html>`_ is
somewhat limited. In the spirit of Thomas Kluyver's `Green Tree Snakes
<https://greentreesnakes.readthedocs.io/>`_ project, which provides similar
extended documentation for the ``ast`` module, I am providing here some
extended documentation for effectively working with the ``tokenize`` module.

Python Versions Supported
=========================

The contents of this guide apply to Python 3.5 and up. Several minor changes
were made to the ``tokenize`` module in Python 3.7, and they have been noted
where appropriate.

The ``tokenize`` module tokenizes code according to the version of Python that
it is being run under. For example, some new syntax features in 3.6 affect
tokenization (in particular, `f-strings
<https://docs.python.org/3.6/whatsnew/3.6.html#pep-498-formatted-string-literals>`_
and `underscores in numeric literals
<https://docs.python.org/3.6/whatsnew/3.6.html#pep-515-underscores-in-numeric-literals>`_).
Take ``123_456``. This will tokenize as a single token in Python 3.6+,
``NUMBER`` (``123_456``), but in Python 3.5, it tokenizes as two tokens,
``NUMBER`` (``123``) and ``NAME`` (``_456``) (see the reference for the
|NUMBER|_ token type for more info).

.. _NUMBER: tokens.html#number

.. |NUMBER| replace:: ``NUMBER``

Most of what is written here will also apply to earlier Python 3 versions,
with obvious exceptions (like tokens that were added for new syntax), though
none of it has been tested.

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

Another difference is that the result of this function is a regular tuple, not
a ``namedtuple``, so you will not be able to use attributes to access the
members. Instead use something like "``for toknum, tokval, start, end, line in
tokenize.generate_tokens(...):``" (this pattern can be used in Python 3 as
well, see the `Usage <usage.html#calling-syntax>`_ section).

Table of Contents
=================

.. toctree::
   :maxdepth: 3

   intro
   alternatives
   usage
   tokens
   helper-functions
   examples

.. raw:: html

   <div class="footer" style="text-align: left;">Water Python image by Matt
   from Melbourne, Australia <a
   href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>, via <a
   href="https://commons.wikimedia.org/wiki/File:Water_Python_(Liasis_mackloti)_(8692394648).jpg">Wikimedia
   Commons</a></div><p>
