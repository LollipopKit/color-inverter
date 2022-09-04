## Color Inverter

### 📌 Support
- `#000000`
- `#000`
- `rgb(0,0,0)`
- `rgba(0,0,0,0)`
- `aliceblue....` CSS Named Colors


### 🔖 Usage
```sh
# 查看帮助
➜ py main.py --help          
usage: main.py [-h] [-w] [-v] [-d] [-o] [-c] [-m] input

css color inverter

positional arguments:
  input           input path

options:
  -h, --help      show this help message and exit
  -w, --write     write result to output file
  -v, --verbose   verbose mode
  -d, --dir       input path is a dir
  -o, --override  override input file
  -c, --combine   combine origin/inverted css into one file which support auto light/dark mode
  -m, --minify    minify css
```

### 📝 License
`LGPL LollipopKit 2022`