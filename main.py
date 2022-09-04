import argparse
import os
import re
import sys
import const

debug = False
color_regexp = r'(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\(\d+, *\d+, *\d+\)|rgba\(\d+, *\d+, *\d+, *[0-9\.]+\))'
named_color_list = []

char_invert_set = [
    ['0', 'f'], ['1', 'e'], ['2', 'd'], ['3', 'c'], ['4', 'b'], ['5', 'a'], ['6', '9'], ['7', '8'],
]


def invert_one_char(char: str) -> str:
    '''
    param: char: str (only contains one '0'-'9' or 'a'-'f')
    return: str
    '''
    char = char.lower()
    if len(char) == 1:
        for s in char_invert_set:
            if char == s[0]:
                return s[1]
            if char == s[1]:
                return s[0]
    raise ValueError(f'Invalid char: {char} with length {len(char)}')


def invert_one(s: str) -> str:
    '''
    param: s: str (only contains '0'-'9' and '.', such as '123' '0.5')
    return: str
    '''
    try:
        i = int(s)
        return str(255 - i)
    except ValueError:
        if '.' in s:
            try:
                f = float(s)
                if f > 1 or f < 0:
                    raise ValueError(f'Invalid float: {f} not in [0, 1]')
                # return f, because f is alpha (in rgb'a')
                return str(f)
            except ValueError:
                raise ValueError(f'Invalid float: {s}')
        raise ValueError(f'Invalid intstr: {s}')


class Color:
    raw: str = None
    # type 0: #000000, 1: #000, 2: rgb(0,0,0), 3: rgba(0,0,0,0)
    type: int = None

    def __init__(self, raw: str) -> None:
        self.raw = raw
        if raw.startswith('rgba('):
            self.type = 3
        if raw.startswith('rgb('):
            self.type = 2
        if raw.startswith('#'):
            self.type = 1 if len(raw) == 7 else 0

    def invert(self) -> 'Color':
        if self.type == 0:
            return Color('#' + ''.join([invert_one_char(c) for c in self.raw[1:]]))
        if self.type == 1:
            return Color('#' + ''.join([invert_one_char(c) for c in self.raw[1:]]))
        if self.type == 2:
            return Color('rgb(' + ','.join([invert_one(c) for c in self.raw[4:-1].split(',')]) + ')')
        if self.type == 3:
            return Color('rgba(' + ','.join([invert_one(c) for c in self.raw[5:-1].split(',')]) + ')')
        return Color('#000000')


def find_invert(css_raw: str):
    replace_list = []
    for color in re.findall(color_regexp, css_raw):
        replace_list.append([color, Color(color).invert().raw])
    for named_color_tuple in named_color_list:
        for locator in re.findall(': ?'+named_color_tuple[0], css_raw):
            replace_list.append([locator, ': ' + Color(named_color_tuple[1]).invert().raw])
    return replace_list


def do_invert(css_raw: str) -> str:
    replace_list = find_invert(css_raw)
    pri('do_convert', replace_list)
    for s in replace_list:
        css_raw = css_raw.replace(s[0], s[1])
    return css_raw


def convert_namaed_color_list():
    for find in re.findall(const.named_color_convert_regexp, const.named_color_raw_str):
        if not find:
            continue
        named_color_list.append([find[0].lower(), find[1]])


def combine(css_light, css_dark) -> str:
    return const.css_mix_template.replace(const.css_dark_locator, css_dark).replace(const.css_light_locator, css_light)


def minify(css_raw: str) -> str:
    css_raw = css_raw.replace(' ', '').replace('\n', '').replace('\t', '')
    return css_raw


def pri(pre: str, msg):
    if not debug:
        return
    print(f'[{pre}] {msg}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='css color inverter')
    parser.add_argument('input', type=str, help='input path')
    parser.add_argument('-w', '--write', default=True, action='store_true', help='write result to output file')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='verbose mode')
    parser.add_argument('-d', '--dir', default=False, action='store_true', help='input path is a dir')
    parser.add_argument('-o', '--override', default=False, action='store_true', help='override input file')
    parser.add_argument('-c', '--combine', default=False, action='store_true', help='combine origin/inverted css into one file which support auto light/dark mode')
    parser.add_argument('-m', '--minify', default=False, action='store_true', help='minify css')
    args = parser.parse_args()

    debug = args.verbose
    if args.input is None:
        print('No input file specified')
        sys.exit(1)

    # Must do it first
    convert_namaed_color_list()

    file_paths = []
    if args.dir:
        if not os.path.isdir(args.input):
            print(f'Invalid dir: {args.input}')
            sys.exit(1)
        for root, dirs, files in os.walk(args.input):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    else:
        file_paths.append(args.input)

    pri('file_paths', file_paths)

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            css_raw = f.read()

        # Doing invert
        if args.combine:
            css_raw = combine(css_raw, do_invert(css_raw))
        else:
            css_raw = do_invert(css_raw)

        if args.minify:
            css_raw = minify(css_raw)

        if args.write:
            # Set output file name
            filename_splited = file_path.split('.')
            file_pre = filename_splited[0]
            file_suf = filename_splited[1]
            filename_new = ''
            if args.override:
                # Use origin name
                filename_new = file_path
            else:
                # Add suffix
                name_addon = ''
                if args.combine:
                    name_addon += '_mix'
                else:
                    name_addon += '_inv'
                if args.minify:
                    name_addon += '_min'
                filename_new = f'{file_pre}{name_addon}.{file_suf}'
            with open(filename_new, 'w') as f:
                f.write(css_raw)
            print(f'Successfully wrote to [{filename_new}].')
        else:
            print(css_raw)
