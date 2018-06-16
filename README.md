<a href="https://www.asmeurer.com/brown-water-python/"><img src="docs/_static/water-python.jpg" alt="logo" width="50%"></a>

Brown Water Python: Better Docs for the Python `tokenize` Module.
=================================================================

This is my attempt to write some more helpful documentation for the Python
standard library [`tokenize`](https://docs.python.org/3/library/tokenize.html)
module, in the style of [Green Tree
Snakes](https://greentreesnakes.readthedocs.io/).

Brown Water Python can be found at
https://www.asmeurer.com/brown-water-python/

**NOTE: This document is currently a work in progress. I plan to add more, but
any feedback on what I already have or what you'd like to see is welcome. Feel
free to [open an issue](https://github.com/asmeurer/brown-water-python/issues)
or pull request about anything (questions, comments on what you'd like to see,
corrections, etc.).**

## Building the HTML pages

To build the HTML pages, first install `sphinx` and `recommonmark`.

    pip install sphinx recommonmark

At the moment, you also need the git versions of Sphinx and alabaster (this
will not be required once they do releases).

    pip install git+https://github.com/sphinx-doc/sphinx@1.7
    pip install -U git+https://github.com/bitprophet/alabaster/

Then run

    cd doc
    make html

The resulting pages are in `_build/html`.

## Doctests

The examples in are all doctested. You can run the doctests with

    cd doc
    ./run_doctests

I have extended to doctests to add flags to skip doctests in Python 3.5, 3.6,
and 3.7, to help test differences in the three language versions. The flags
are `SKIP35`, `SKIP36`, and `SKIP37`, respectively. For example, to make a
doctest that doesn't run in Python 3.5, use

```py
>>> # This is only valid syntax in Python 3.6+
>>> 123_456  # doctest: +SKIP35
123456

```

To make a doctest that only runs in Python 3.5, use something like


```py
>>> # This is the behavior in Python 3.5
>>> 123_456 # doctest: +SKIP36, +SKIP37
Traceback (most recent call last):
  ...
    123_456
          ^
SyntaxError: invalid syntax

```

The `# doctest` comments are automatically hidden in the rendered output, so
it's generally a good idea to include an explanatory comment that the given
code only runs on certain Python versions, as in the above examples.

For code that tests exceptions, you'll need to include `...` in the traceback
to make it match.

For code that prints something and then has an exception, you'll have to skip
it entirely (`# doctest: +SKIP`), as the doctest module does not support this.

As a final note, the doctester won't work correctly unless you include a blank
line before the end \`\`\` (otherwise it will think it is part of the output).

## Contributing

Contributions are welcome. So are questions. My goal here is to help people to
understand the `tokenize` module, so if something is not clear, [please let me
know](https://github.com/asmeurer/brown-water-python/issues). If you see
something written here that is wrong, please make a pull request correcting
it. I'm not an expert at `tokenize`. I mainly know what is written here from
trial and error and from reading the source code.

The site is built with Sphinx using
[recommonmark](https://recommonmark.readthedocs.io/), meaning the files are
written in Markdown. If you need to add an reST structure that isn't supported
by Markdown, you can either use raw HTML to emulate it, or use the
[eval_rst](https://recommonmark.readthedocs.io/en/latest/auto_structify.html#embed-restructuredtext)
construct to embed reST in the Markdown.

## License

Everything in this repo is licensed under the MIT license. See the LICENSE
file.

The Water Python image is by Matt from Melbourne, Australia [CC BY
2.0](https://creativecommons.org/licenses/by/2.0), via [Wikimedia
Commons](https://commons.wikimedia.org/wiki/File:Water_Python_(Liasis_mackloti)_(8692394648).jpg).
