.. _install:

Installation
============

If you need to process a lot of files or are worried about your privacy,
we recommend to install ESIgen locally. It also makes for a good
day-to-day tool if you have to check a lot of output files routinely!

Recommended steps
-----------------

Download the `latest release`_ and execute the installer. The binaries
``esigen`` and ``esigenweb`` will be available under
``$INSTALL_PATH/bin``. In Windows, a shortcut will also be available in
Start menu.

If the installer is not available for your platform, use one of the
methods below.

With conda
----------

Conda is package manager for Python that greatly simplifies the
installation of Python libraries.

1. Download `Miniconda 3`_ for your platform. 2a. Install ``esigen`` in
   a Python 3.6 environment (default for Miniconda 3). 2b. Install
   ``esigen`` in a Python 2.7 environment if you don’t have PyMol
   already (Linux and MacOS, only).
2. Run ``esigenweb`` to launch the web server, or ``esigen`` for the CLI
   tool.

For Linux & Mac, this roughly translates to:

::

    ## Install Conda
    wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda*.sh

    ## Install esigen
    conda install -c insilichem esigen

    ## Or, if you also need PyMol
    # conda create -n esigen -c omnia -c egilliesix -c insilichem python=2.7 esigen
    # conda activate esigen

    ## Run!
    esigen -h  # CLI
    esigenweb  # WEB

For Windows, it’s almost the same. Just install Miniconda with the
`*.exe`_, and use the Anaconda Prompt (in Start Menu) to install
Numpy. Then, use ``pip`` for ``esigen``. The commands are:

::

    conda install numpy esigen
    esigen -h  # CLI
    esigenweb  # WEB

With pip
--------

If you don’t want to install Conda, or the package is not available in
your platform, you will need to provide the additional dependencies
yourself. Assuming you already have Python installed, run:

::

    pip install numpy
    pip install esigen
    # or, for latest dev version
    pip install https://github.com/insilichem/esigen/archive/master.zip

.. _latest release: https://github.com/insilichem/esigen/releases
.. _Miniconda 3: https://conda.io/miniconda.html
.. _*.exe: https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe
