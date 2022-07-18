import argparse
import re
import sys

debug = False
color_regexp = r'(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}|rgb\(\d+, *\d+, *\d+\)|rgba\(\d+, *\d+, *\d+, *[0-9\.]+\))'
named_color_list = []
named_color_convert_regexp = r'([A-Za-z]+)\s+(#[0-9a-fA-F]{6})'
named_color_raw_str = '''
AliceBlue 	#F0F8FF
AntiqueWhite 	#FAEBD7
Aqua 	#00FFFF
Aquamarine 	#7FFFD4
Azure 	#F0FFFF
Beige 	#F5F5DC
Bisque 	#FFE4C4
Black 	#000000
BlanchedAlmond 	#FFEBCD
Blue 	#0000FF
BlueViolet 	#8A2BE2
Brown 	#A52A2A
BurlyWood 	#DEB887
CadetBlue 	#5F9EA0
Chartreuse 	#7FFF00
Chocolate 	#D2691E
Coral 	#FF7F50
CornflowerBlue 	#6495ED
Cornsilk 	#FFF8DC
Crimson 	#DC143C
Cyan 	#00FFFF
DarkBlue 	#00008B
DarkCyan 	#008B8B
DarkGoldenRod 	#B8860B
DarkGray 	#A9A9A9
DarkGreen 	#006400
DarkKhaki 	#BDB76B
DarkMagenta 	#8B008B
DarkOliveGreen 	#556B2F
DarkOrange 	#FF8C00
DarkOrchid 	#9932CC
DarkRed 	#8B0000
DarkSalmon 	#E9967A
DarkSeaGreen 	#8FBC8F
DarkSlateBlue 	#483D8B
DarkSlateGray 	#2F4F4F
DarkTurquoise 	#00CED1
DarkViolet 	#9400D3
DeepPink 	#FF1493
DeepSkyBlue 	#00BFFF
DimGray 	#696969
DodgerBlue 	#1E90FF
FireBrick 	#B22222
FloralWhite 	#FFFAF0
ForestGreen 	#228B22
Fuchsia 	#FF00FF
Gainsboro 	#DCDCDC
GhostWhite 	#F8F8FF
Gold 	#FFD700
GoldenRod 	#DAA520
Gray 	#808080
Green 	#008000
GreenYellow 	#ADFF2F
HoneyDew 	#F0FFF0
HotPink 	#FF69B4
IndianRed  	#CD5C5C
Indigo  	#4B0082
Ivory 	#FFFFF0
Khaki 	#F0E68C
Lavender 	#E6E6FA
LavenderBlush 	#FFF0F5
LawnGreen 	#7CFC00
LemonChiffon 	#FFFACD
LightBlue 	#ADD8E6
LightCoral 	#F08080
LightCyan 	#E0FFFF
LightGoldenRodYellow 	#FAFAD2
LightGray 	#D3D3D3
LightGreen 	#90EE90
LightPink 	#FFB6C1
LightSalmon 	#FFA07A
LightSeaGreen 	#20B2AA
LightSkyBlue 	#87CEFA
LightSlateGray 	#778899
LightSteelBlue 	#B0C4DE
LightYellow 	#FFFFE0
Lime 	#00FF00
LimeGreen 	#32CD32
Linen 	#FAF0E6
Magenta 	#FF00FF
Maroon 	#800000
MediumAquaMarine 	#66CDAA
MediumBlue 	#0000CD
MediumOrchid 	#BA55D3
MediumPurple 	#9370DB
MediumSeaGreen 	#3CB371
MediumSlateBlue 	#7B68EE
MediumSpringGreen 	#00FA9A
MediumTurquoise 	#48D1CC
MediumVioletRed 	#C71585
MidnightBlue 	#191970
MintCream 	#F5FFFA
MistyRose 	#FFE4E1
Moccasin 	#FFE4B5
NavajoWhite 	#FFDEAD
Navy 	#000080
OldLace 	#FDF5E6
Olive 	#808000
OliveDrab 	#6B8E23
Orange 	#FFA500
OrangeRed 	#FF4500
Orchid 	#DA70D6
PaleGoldenRod 	#EEE8AA
PaleGreen 	#98FB98
PaleTurquoise 	#AFEEEE
PaleVioletRed 	#DB7093
PapayaWhip 	#FFEFD5
PeachPuff 	#FFDAB9
Peru 	#CD853F
Pink 	#FFC0CB
Plum 	#DDA0DD
PowderBlue 	#B0E0E6
Purple 	#800080
Red 	#FF0000
RosyBrown 	#BC8F8F
RoyalBlue 	#4169E1
SaddleBrown 	#8B4513
Salmon 	#FA8072
SandyBrown 	#F4A460
SeaGreen 	#2E8B57
SeaShell 	#FFF5EE
Sienna 	#A0522D
Silver 	#C0C0C0
SkyBlue 	#87CEEB
SlateBlue 	#6A5ACD
SlateGray 	#708090
Snow 	#FFFAFA
SpringGreen 	#00FF7F
SteelBlue 	#4682B4
Tan 	#D2B48C
Teal 	#008080
Thistle 	#D8BFD8
Tomato 	#FF6347
Turquoise 	#40E0D0
Violet 	#EE82EE
Wheat 	#F5DEB3
White 	#FFFFFF
WhiteSmoke 	#F5F5F5
Yellow 	#FFFF00
YellowGreen 	#9ACD32
'''

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
                return str(1 - f)
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
    for find in re.findall(named_color_convert_regexp, named_color_raw_str):
        if not find:
            continue
        named_color_list.append([find[0].lower(), find[1]])


def pri(pre: str, msg):
    if not debug:
        return
    print(f'[{pre} {msg}')


if __name__ == '__main__':
    convert_namaed_color_list()

    parser = argparse.ArgumentParser(description='css color inverter')
    parser.add_argument('input', type=str, help='input file path')
    parser.add_argument('-w', '--write', action='store_true', help='write result to output file')
    parser.add_argument('-d', '--debug', action='store_true', help='debug')
    args = parser.parse_args()

    debug = args.debug
    if args.input is None:
        print('No input file specified')
        sys.exit(1)
    filename = args.input
    filename_splited = filename.split('.')
    file_pre = filename_splited[0]
    file_suf = filename_splited[1]
    with open(filename, 'r') as f:
        css_raw = f.read()
    css_raw = do_invert(css_raw)
    if args.write:
        with open(f'{file_pre}.inverted.{file_suf}', 'w') as f:
            f.write(css_raw)
    else:
        print(css_raw)
