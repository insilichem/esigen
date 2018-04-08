ESIgen: Supporting information generator
========================================

|Build Status| |Install with conda| |DOI|

Automatically generate supporting information documents for your
Chemistry publications online.

.. figure:: docs/img/esigen.gif
   :alt: Example


Documentation and support
=========================

Latest documentation is always available at `esigen.readthedocs.io`_.

If you have problems using ESIgen, feel free to `create an issue`_!
Also, make sure to visit our main webpage at `insilichem.com`_.

Citation
========

|DOI|

ESIgen is scientific software, funded by public research grants: Spanish
MINECO (project CTQ2017-87889-P), Generalitat de Catalunya (project
2014SGR989), J.R.G.P.: Generalitat de Catalunya (grant 2017FI_B2_00168),
P.G.O.: Spanish MINECO (grant FPI BES-2015-074190). If you make use of
ESIgen in scientific publications, please cite `our article in JCIM`_.
It will help measure the impact of our research and future funding!

::

    @article{doi:10.1021/acs.jcim.7b00714,
        author = {Rodríguez-Guerra Pedregal, Jaime and Gómez-Orellana, Pablo and Maréchal, Jean-Didier Pierre},
        title = {ESIgen: Electronic Supporting Information Generator for Computational Chemistry Publications},
        journal = {Journal of Chemical Information and Modeling},
        year = {2018},
        doi = {10.1021/acs.jcim.7b00714},
            note ={PMID: 29506387},
        URL = {
                https://doi.org/10.1021/acs.jcim.7b00714
        },
        eprint = {
                https://doi.org/10.1021/acs.jcim.7b00714
        }
    }

Acknowledgments
===============

Inspired by `Chauncey Garrett’s collection of scripts`_, this project
was conceived as a Python-only CLI attempt at solving the same problem.
Then more features were added (like markdown reports or image
rendering), and finally was turned into a online service.

ESIgen is possible thanks to great open-source projects:

-  Backend: `CCLib`_, `Jinja`_.
-  Web UI: `NGL`_, `Flask`_, `requests`_, `HTML5 UP`_, `Dropzone`_,
   `clipboard.js`_, `FileSaver.js`_, `JSZip`_, `CloudFormatter`_.
-  CLI: `PyMol`_.
-  Installer: `Conda Constructor`_.

.. _Conda Constructor: https://github.com/conda/constructor
.. _esigen.readthedocs.io: https://esigen.readthedocs.io
.. _create an issue: https://github.com/insilichem/esigen/issues
.. _insilichem.com: http://www.insilichem.com
.. _our article in JCIM: https://pubs.acs.org/doi/10.1021/acs.jcim.7b00714
.. _Chauncey Garrett’s collection of scripts: https://github.com/chauncey-garrett/gaussian-tools
.. _CCLib: https://github.com/cclib/cclib
.. _Jinja: http://jinja.pocoo.org/
.. _NGL: https://github.com/arose/ngl
.. _Flask: https://github.com/pallets/flask
.. _requests: http://docs.python-requests.org
.. _HTML5 UP: https://html5up.net/
.. _Dropzone: https://github.com/enyo/dropzone
.. _clipboard.js: https://clipboardjs.com/
.. _FileSaver.js: https://github.com/eligrey/FileSaver.js/
.. _JSZip: https://stuk.github.io/jszip/
.. _CloudFormatter: http://www.cloudformatter.com/CSS2Pdf
.. _PyMol: https://sourceforge.net/projects/pymol/

.. |Build Status| image:: https://travis-ci.org/insilichem/esigen.svg?branch=master
   :target: https://travis-ci.org/insilichem/esigen
.. |Install with conda| image:: https://anaconda.org/insilichem/esigen/badges/downloads.svg
   :target: https://anaconda.org/InsiliChem/esigen
.. |DOI| image:: https://img.shields.io/badge/doi-10.1021%2Facs.jcim.7b00714-blue.svg
   :target: https://pubs.acs.org/doi/10.1021/acs.jcim.7b00714