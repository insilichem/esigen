.. _templating:

Templating in ESIgen
====================

.. _builtin-templates:

Builtin templates
-----------------

Some `templates are included with
ESIgen <https://github.com/insilichem/esigen/tree/master/esigen/templates/reports>`__
for your convenience:

-  ``default.md``. Uses an interactive 3D viewer in the web interface
   and static images on the command line. A table of magnitudes is
   provided, together with the coordinates and, if available, first 10
   frequencies.
-  ``TD.md``. Same as default, but listing the excitation energies of TD
   calculations.
-  ``simple.md``. Dummy example to help illustrate easy templating.
-  ``chemshell.md``. Shows experimental support for some ChemShell QM/MM
   jobs.
-  ``checks.md``. Day-to-day analysis tasks for Gaussian jobs.

However, you might want to modify them or create your own from scratch.
Keep reading for further details.

.. _template-syntax:

Syntax
------

ESIgen templates are written using
`**Markdown** <https://daringfireball.net/projects/markdown/syntax>`__
(a subset of HTML designed to be highly readable) syntax on top of the
wonderful `**Jinja2** <http://jinja.pocoo.org/>`__ engine, which allows
easy keyword replacing. For example:

::

    # {{ name }}

    - Stoichiometry: {{ stoichiometry }}
    - Electronic Energy (eV): {{ electronic_energy }}

, which results in something like this:

--------------

heme_fe2singlet_fe3doublet
..........................

-  Stoichiometry: C34H30FeN4O4(1-,2)
-  Electronic Energy (eV): -1957.86428957

--------------

As you see, you just write normal Markdown (syntax is described
`here <https://github.com/tchapi/markdown-cheatsheet>`__) and then
insert the desired variables between double curly braces, like this
``{{ energy }}``. Jinja2 also supports ``for`` loops, ``if``
conditionals and so on, but you won’t probably need it. However, one of
the advanced features might be helpful:
`filters <http://jinja.pocoo.org/docs/2.10/templates/#filters>`__, which
allow you to post-process some values (ie, centering with respect to a
fixed width with ``{{ value|center(20) }}``).

.. _data-fields:

Data Fields
-----------

All fields provided by `cclib <http://cclib.github.io/index.html>`_
parsers are available. Simply refer to the official documentation on
`Parsed Data <http://cclib.github.io/data.html>`__ and `Parsed Data
Notes <http://cclib.github.io/data_notes.html>`__ to check the full list
and the compatibility matrix across different programs.

Additionally, ESIgen provides some more fields and methods you can use
during the templating:

-  Features

   -  ``{{ name }}``: Extracted from the filename, without the
      extension.
   -  ``{{ filename }}``: Filename, with extension.
   -  ``{{ filepath }}``: Full path to the file.
   -  ``{{ stoichiometry }}``. Self-explanatory.
   -  ``{{ imaginary_freqs }}``: Number of negative frequencies.
   -  ``{{ mean_of_electrons }}``: Mean of ``alphaelectrons`` and
      ``betaelectrons``.
   -  ``{{ metadata['route'] }}``: First of Gaussian route sections. For
      other programs, check ``metadata``.
   -  ``{{ nsteps }}``: Number of optimization steps. Extracted from
      ``scfenergies`` size.
   - ``{{ solvent }}``. Solvent chosen, if applicable. (Gaussian only).
   -  ModRedundant scans (Gaussian only, might change anytime; see
      ``checks.md`` for an example):

      -  ``{{ modredvars }}``: List of variables being scanned (R83,
         A21, D125…).
      -  ``{{ modreddefs }}``: Atomic definition of those variables (2
         atoms for R, 3 for A, 4 for D)
      -  ``{{ modredvalues }}``: (m, n) array for variable values
         (distance in A, angle in degrees), where m is the number of
         cycles and n the number of variables.
      -  ``{{ modredenergies }}``: (j, k, l) array of -dE/dx values,
         where j is the number of cycles, k the number of iteration at
         each cycle and l the number of variables being scanned.

-  Magnitudes (Gaussian only)

   -  ``{{ electronic_energy }}``. Last of ``scfenergies``, Eh.
   -  ``{{ thermalenergy }}``: Sum of electronic and thermal energies,
      Eh.
   -  ``{{ zeropointenergy }}``: Sum of electronic and zero-point
      energies, Eh.

-  Structural info

   -  ``{{ viewer3d }}``: Insert interactive 3D depiction of the
      structure. Only available in web UI.
   -  ``{{ image }}``: Static depiction of the structure. Requires PyMol
      (not available on public demo!)
   -  ``{{ cartesians }}``: Molecule structure exported in XYZ format.

-  Functions

   -  ``{{ convertor(value, from_unit, to_unit) }}`` can be used to
      change units in most cases. Check
      `here <https://github.com/cclib/cclib/blob/master/src/cclib/parser/utils.py#L62>`__
      for supported constants. If not, you can always use normal math
      inside the curly braces (``{{ (10+value)**2 }}``).

-  Experimental support for QM/MM jobs in ChemShell (might change
   anytime; see ``chemshell.md`` template for an example)

   -  ``{{ scfenergies  }}``: Lists “QM/MM energy” entries.
   -  ``{{ mmenergies }}``: List of dicts which detail MM energy
      decomposition for each cycle.
   -  ``{{ energycontributions }}``: List of dicts which detail QM/MM
      energy decomposition for each cycle.
   -  ``{{ optdone }}``: ``True`` if optimization converged (only
      available with Turbomole backend).

.. note::

    Depending on the software used to create the output file, some fields
    might not be available. When in doubt, you can check the JSON dump of
    the files by appending ``/json`` to the report URL (a link is also
    available in the bottom of the page). This will list all the attributes
    available for each file. (JSON dumps are best viewed in Firefox 57+).

Missing Values
--------------

An additional flag ``missing`` is passed to the template to control what
to report when the requested field is missing in the file. By default,
in the WebUI, maximum length is restricted to 10 chars.

In the ``default.md`` template, ``missing`` is checked in every row to
control if the row should be written or not. If ``missing`` is set to
the empty string ``''`` (default value) and the value is not present in
the file, the row won’t be written; if missing is set to any other
string (for example, ``N/A``) and the value is not present, the row will
be written but the value will be reported as ``N/A``.

For example, if ``stoichiometry`` is not available in the file:

**Case A**: ``missing = ''``

::

    # TDNI_GGCMPW

    __Requested operations__

    `p td=(nstates=30) MPW1PW91 scrf=(solvent=water) geom=connectivity def2tzvp`

    __Relevant magnitudes__

    | Datum                                            | Value                     |
    |:-------------------------------------------------|--------------------------:|
    | Charge                                           |             -2            |
    | Multiplicity                                     |             1             |
    | Stoichiometry                                    |      C7H9N3NiO4S(2-)      |
    | Number of Basis Functions                        |            570            |
    | Electronic Energy (eV)                           |    -2644.5302088499993    |
    | Mean of alpha and beta Electrons                 |             75            |

**Case B**: ``missing = 'N/A'``, default

::

    # TDNI_GGCMPW

    __Requested operations__

    `p td=(nstates=30) MPW1PW91 scrf=(solvent=water) geom=connectivity def2tzvp`

    __Relevant magnitudes__

    | Datum                                            | Value                     |
    |:-------------------------------------------------|--------------------------:|
    | Charge                                           |             -2            |
    | Multiplicity                                     |             1             |
    | Stoichiometry                                    |      C7H9N3NiO4S(2-)      |
    | Number of Basis Functions                        |            570            |
    | Electronic Energy (Eh)                           |    -2644.5302088499993    |
    | Sum of electronic and zero-point Energies (Eh)   |            N/A            |
    | Sum of electronic and thermal Energies (Eh)      |            N/A            |
    | Sum of electronic and thermal Enthalpies (Eh)    |            N/A            |
    | Sum of electronic and thermal Free Energies (Eh) |            N/A            |
    | Number of Imaginary Frequencies                  |            N/A            |
    | Mean of alpha and beta Electrons                 |             75            |
