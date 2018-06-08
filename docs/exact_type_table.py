#!/usr/bin/env python

import tokenize

HEADER = """
.. list-table::
   :header-rows: 1

   * - Exact token type
     - String value
"""

TABLE_ENTRY = """
   * - {token_name}{note}
     - {token_string}
"""

FOOTER = """

.. rubric:: Footnotes

.. [#f1] Due to a `bug <https://bugs.python.org/issue24622>`_, the ``exact_type`` for ``RARROW`` and ``ELLIPSIS`` is ``OP`` in Python versions prior to 3.7. See `below <#rarrow>`_.

"""

def escape(s):
    return '\\' + '\\'.join(s)

token_types = {num: string for string, num in tokenize.EXACT_TOKEN_TYPES.items()}

# Not included below Python 3.7 for some reason
token_types[tokenize.ELLIPSIS] = '...'
token_types[tokenize.RARROW] = '->'

def main():
    print("Generating exact_type_table.txt")
    with open('exact_type_table.txt', 'w') as f:
        f.write(HEADER)
        for token_type in sorted(token_types):
            token_string = token_types[token_type]
            if token_type in [tokenize.RARROW, tokenize.ELLIPSIS]:
                note = " [#f1]_"
            else:
                note = ''

            f.write(TABLE_ENTRY.format(
                token_name=tokenize.tok_name[token_type],
                token_string=escape(token_string),
                note=note,
                ))
        f.write(FOOTER)

if __name__ == '__main__':
    main()
