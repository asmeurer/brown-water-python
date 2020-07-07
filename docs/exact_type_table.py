#!/usr/bin/env python
import sys
import tokenize
from pathlib import Path

# TODO: Make these footnotes appear right below the table. See
# https://github.com/executablebooks/MyST-Parser/issues/179

FOOTER = """

[^f1]: Due to a [bug](https://bugs.python.org/issue24622), the `exact_type`
       for `RARROW` and `ELLIPSIS` tokens is `OP` in Python versions prior to
       3.7. See [above](rarrow).

[^f2]: New in Python 3.8.

"""

def code(s):
    return '`' + s + '`'

token_types = {num: string for string, num in tokenize.EXACT_TOKEN_TYPES.items()}

def main():
    if sys.version_info[1] < 8:
        sys.exit("This script should be run with Python 3.8 or newer.")

    print("Generating exact_type_table.txt")

    name_column = ['Exact token type']
    string_column = ['String value']
    for token_type in sorted(token_types):
        token_name = tokenize.tok_name[token_type]
        token_string = token_types[token_type]
        if token_type in [tokenize.RARROW, tokenize.ELLIPSIS]:
            note = " [^f1]"
        elif token_type == tokenize.COLONEQUAL:
            note = " [^f2]"
        else:
            note = ''

        name_column.append(code(token_name) + note)
        string_column.append(code(token_string))

    name_column_width = len(max(name_column, key=len)) + 2
    string_column_width = len(max(string_column, key=len)) + 2

    assert len(name_column) == len(string_column)

    with open('exact_type_table.txt', 'w') as f:
        for i, (typ, string) in enumerate(zip(name_column, string_column)):
            f.write('|')
            f.write(typ.center(name_column_width))
            f.write('|')
            f.write(string.center(string_column_width))
            f.write('|')
            f.write('\n')
            if i == 0:
                f.write('|')
                f.write('-'*name_column_width)
                f.write('|')
                f.write('-'*string_column_width)
                f.write('|')
                f.write('\n')

        f.write(FOOTER)

    # touch tokens.md so it forces a rebuild
    Path('tokens.md').touch()

if __name__ == '__main__':
    main()
