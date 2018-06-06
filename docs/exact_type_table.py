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

RARROW_NOTE = " The ``exact_type`` for ``RARROW`` is ``OP`` in Python versions prior to 3.7. See :ref:`RARROW` below."

ELLIPSIS_NOTE = " The ``exact_type`` for ``ELLIPSIS`` is ``OP`` in Python versions prior to 3.7. See :ref:`ELLIPSIS` below."

def escape(s):
    return '\\' + '\\'.join(s)

token_types = {num: string for string, num in tokenize.EXACT_TOKEN_TYPES}

# Not included below Python 3.7 for some reason
token_types[tokenize.ELLIPSIS] = '...'
token_types[tokenize.RARROW] = '->'

def main():
    with open('exact_type_table.txt', 'w') as f:
        f.write(HEADER)
        for token_type, token_string in sorted(token_types):
            if token_type == tokenize.RARROW:
                note = RARROW_NOTE
            elif token_type == tokenize.ELLIPSIS:
                note = ELLIPSIS_NOTE
            else:
                note = ''

            f.write(TABLE_ENTRY.format(
                token_name=tokenize.tok_name[token_type],
                token_string=escape(token_string),
                note=note,
                ))

if __name__ == '__main__':
    main()
