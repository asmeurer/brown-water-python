#!/usr/bin/env python

import tokenize

HEADER = """
.. list-table::
   :header-rows: 1

   * - Exact token type
     - String value
"""

TABLE_ENTRY = """
   * - {token_name}
     - {token_string}
"""

def escape(s):
    return '\\' + '\\'.join(s)

def main():
    with open('exact_type_table.txt', 'w') as f:
        f.write(HEADER)
        for token_string, token_type in sorted(tokenize.EXACT_TOKEN_TYPES.items(), key=lambda i: i[1]):
            f.write(TABLE_ENTRY.format(
                token_name=tokenize.tok_name[token_type],
                token_string=escape(token_string)))

if __name__ == '__main__':
    main()
