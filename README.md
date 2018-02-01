# ESIgen: Supporting information generator

Automatically generate supporting information documents for your Chemistry publications online.

![Example](docs/img/esigen.gif)

# Usage

## Online server

1. Visit http://esi.insilichem.com and upload your Computational Chemistry outputs there. Any of the examples in [cclib data](https://github.com/cclib/cclib/tree/master/data) should work.
2. Choose one of the [builtin templates](docs/templates.md#builtin-templates) or [create your own](docs/templates.md#syntax).
3. Profit! You can generate a PDF, print it with your browser, download a zip file with all the contents or even publish it to a [Gist](https://gist.github.com/anonymous/8a5890c9e18de78ba90e67c3109b074f). All export options are listed at the bottom of the file.

This is only a demo server, so performance won't be stellar... All files will be deleted within 1h and we won't collect any data from you. Refer to the [local installation docs](docs/install.md) if you want to setup your own (local) server.

## Command-line (batch processing)

1. [Install](docs/install.md) in your computer.
2. Run `esigen filename.log`. That's it! You can even provide several files at once with `esigen file1.log file2.log` or `esigen my_files_*.log`.
3. If you want to use [another builtin template](docs/templates.md#builtin-templates) or [create your own](docs/templates.md#syntax), specify it with `esigen -t mytemplate.md filename.log`. Ideal for quick reports on your daily routine.

# Documentation

- [Local installation](docs/install.md)
- [How to write your own ESIgen templates](docs/templates.md)
- [Use ESIgen Python API programmatically](docs/developer.md)

# Acknowledgments

Inspired by [Chauncey Garrett's collection of scripts](https://github.com/chauncey-garrett/gaussian-tools), this project was conceived as a Python-only CLI attempt at solving the same problem. Then more features were added (like markdown reports or image rendering), and finally was turned into a online service.

ESIgen is possible thanks to great open-source projects:

- Backend: [CCLib](https://github.com/cclib/cclib), [Jinja](http://jinja.pocoo.org/).
- Web UI: [NGL](https://github.com/arose/ngl), [Flask](https://github.com/pallets/flask), [requests](http://docs.python-requests.org), [HTML5 UP](https://html5up.net/), [Dropzone](https://github.com/enyo/dropzone), [clipboard.js](https://clipboardjs.com/), [FileSaver.js](https://github.com/eligrey/FileSaver.js/), [JSZip](https://stuk.github.io/jszip/), [CloudFormatter](http://www.cloudformatter.com/CSS2Pdf).
- CLI: [PyMol](https://sourceforge.net/projects/pymol/).
- Installer: [Conda Constructor](https://github.com/conda/constructor).