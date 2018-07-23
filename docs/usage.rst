Quick usage
===========

.. _webusage:

Online server
-------------

.. note::

      This is only a demo server, so performance won’t be stellar… All files
      will be deleted within 1h and we won’t collect any data from you. Refer
      to the :ref:`install` docs if you want to setup your own (local)
      server.

1. Visit `esi.insilichem.com`_ and upload your Computational Chemistry
   outputs there. Any of the examples in `cclib data`_ should work.

2. Choose one of the :ref:`builtin-templates` or create your own (read on templating :ref:`template-syntax`).

3. Profit! You can now inspect the report and use the interactive viewer
   to rotate, move and `make measurements`_ in your molecule(s).

4. If you want to download the results, you have several options in the
   footer:

   a. Download all the processed data in a ZIP file which will include
      all the files listed below.
   b. Download only the rendered images in the browser.
   c. `Markdown <https://en.wikipedia.org/wiki/Markdown>`_ report (plain-text)
   d. `XYZ <https://en.wikipedia.org/wiki/XYZ_file_format>`_ coordinates
   e. `CML <https://en.wikipedia.org/wiki/Chemical_Markup_Language>`_ coordinates (Chemical Markup Language, XML-like)
   f. Raw `JSON <https://en.wikipedia.org/wiki/JSON>`_ (Programmatic representation of all the parsed data in
      your logfiles)
   g. `Chemical JSON <http://wiki.openchemistry.org/Chemical_JSON>`_ (Simplified summary of the JSON dump, with more
      meaningful names)

5. You can also export to online services that generate citable DOI
   identifiers for your data.

   a. `Figshare <https://figshare.com/>`_
   b. `Github Gist <https://gist.github.com/>`_ (must be converted to repository and then sync’ed with
      Zenodo integration)
   c. `Zenodo <https://zenodo.org/>`_


.. _cliusage:

Command-line (batch processing)
-------------------------------

1. Install ESIgen in your computer (read :ref:`install`).
2. Run ``esigen filename.log``. That’s it! You can even provide several
   files at once with ``esigen file1.log file2.log`` or
   ``esigen my_files_*.log``.
3. If you want to one of the :ref:`builtin-templates` or use your own (read on templating :ref:`template-syntax`),
   specify it with ``esigen -t mytemplate.md filename.log``. Ideal for
   quick reports on your daily routine. The template ``checks.md`` has been
   designed for this specific purpose.

The ESIgen suite also includes several other executables:

- ``esigenweb``. Creates a local webserver like the one in `esi.insilichem.com`_, but running only in your computer.
- ``esixyz``. Extracts XYZ coordinates from a computational chemistry logfile. Can be used with optimization jobs to request a particular step. Use ``esixyz -h`` for more help.

Futhermore, since ESIgen uses ``cclib`` under the hood, all its executables are available as well. Namely, ``ccget`` and ``ccwrite``. Again use ``-h`` for more help.

.. _esi.insilichem.com: http://esi.insilichem.com
.. _cclib data: https://github.com/cclib/cclib/tree/master/data
.. _make measurements: #
.. _local installation docs: install.md
.. _Install: install.md
.. _another builtin template: templates.md#builtin-templates