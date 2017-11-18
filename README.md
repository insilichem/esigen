# Insilichem ESI: Supporting information generator

Automatically generate supporting information documents for your Chemistry publications.

# Usage

Visit http://esi.insilichem.com and submit your Gaussian outputs there. This is only a demo server, so performance won't be stellar... All files will be deleted within 24h and we won't collect any data from you.

# Local installation

If you need to process a lot of files or are worried about your privacy, we recommend using it locally.

1. Download and unzip [this repository](https://github.com/insilichem/supporting)
2. Download [Miniconda](https://conda.io/miniconda.html)
3. Create a new conda environment and activate it
4. Enter the repo directory and run `python runserver.py`

For Linux, this roughly translates to:

```
wget https://github.com/insilichem/supporting/archive/master.zip && unzip master.zip
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda*.sh
conda env create -f supporting-master/environment.yml # or environment-pymol.yml if you need CLI image rendering (not web)
source activate supporting
cd supporting-master
python runserver.py
```

You can also install it as a Python CLI program with `python setup.py install`, which will provide an executable called `qmview` with the same purpose. Run `qmview -h` to print usage guidelines.


# Acknowledgments

Inspired by [Chauncey Garrett's collection of scripts](https://github.com/chauncey-garrett/gaussian-tools), this project was conceived as a Python-only CLI attempt at solving the same problem. Then I ([@jaimergp](https://github.com/jaimergp/)) started adding more features (like markdown reports or image rendering), and finally turned it into a online service.

Insilichem ESI is possible thanks to great open-source projects:

- [CCLib](https://github.com/cclib/cclib). Gaussian output file parsing.
- [NGL](https://github.com/arose/ngl). Interactive 3D preview in the browser.
- [Flask](https://github.com/pallets/flask). Web backend.
- [PyMol](https://sourceforge.net/projects/pymol/). Unattended 3D image rendering.
- [HTML5 UP](https://html5up.net/). Base web design.
- [Dropzone](https://github.com/enyo/dropzone). Drag & drop uploads.