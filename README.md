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
or pull request about anything.**

## Building the HTML pages

To build the HTML pages, first install `sphinx` and `recommonmark`.

    pip install sphinx recommonmark

Then run

    cd doc
    make html

The resulting pages are in `_build/html`.

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

Everything in this repo is licensed under the MIT licence. See the LICENSE
file.
