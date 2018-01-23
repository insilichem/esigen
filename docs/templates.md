# Templating in ESIgen

## Syntax

ESIgen templates are written using [**Markdown**](https://daringfireball.net/projects/markdown/syntax) (a subset of HTML designed to be highly readable) syntax on top of the wonderful [**Jinja2**](http://jinja.pocoo.org/) engine, which allows easy keyword replacing. For example:

```
# {{ name }}

- Stoichiometry: {{ stoichiometry }}
- Electronic Energy (eV): {{ electronic_energy }}
```
, which results in something like this:

***

# dvb_gopt

- Stoichiometry: N/A
- Electronic Energy (eV): -5.16295044221

***

As you see, you just write normal Markdown (syntax is described [here](https://github.com/tchapi/markdown-cheatsheet)) and then insert the desired variables between double curly braces, like this `{{ energy }}`. Jinja2 also supports `for` loops, `if` conditionals and so on, but you won't probably need it. However, one of the advanced features might be helpful: [filters](http://jinja.pocoo.org/docs/2.10/templates/#filters), which allow you to post-process some values (ie, centering with respect to a fixed width with `{{ value|center(20) }}`).

Some [templates are included with ESIgen](https://github.com/insilichem/esigen/tree/master/esigen/templates/reports) for your convenience:

- `default.md`. Uses an interactive 3D viewer in the web interface and static images on the command line. A table of magnitudes is provided, together with the coordinates and, if available, first 10 frequencies.
- `TD.md`. Same as default, but listing the excitation energies of TD calculations.
- `simple.md`. Dummy example to help illustrate easy templating.

## Data Fields

All fields provided by `[cclib](http://cclib.github.io/index.html)` parsers are available. Simply refer to the official documentation on [Parsed Data](http://cclib.github.io/data.html) and [Parsed Data Notes](http://cclib.github.io/data_notes.html) to check the full list and the compatibility matrix across different programs.

Additionally, ESIgen provides some more fields and methods you can use during the templating:

- Features
    - `{{ name }}`: Extracted from the filename, without the extension.
    - `{{ stoichiometry }}`.
    - `{{ nbasis }}`: Number of basis functions.
    - `{{ imaginary_freqs }}`: Number of negative frequencies.
    - `{{ mean_of_electrons }}`: Mean of alpha and beta electrons.
- Magnitudes
    - `{{ electronic_energy }}`.
    - `{{ enthalpy }}`: Sum of electronic and thermal enthalpies, eV
    - `{{ freeenergy }}`: Sum of electronic and free energies, eV.
    - `{{ thermalenergies }}`: Sum of electronic and thermal energies, eV.
    - `{{ zeropointenergies }}`: Sum of electronic and zero-point energies, eV.
- Structural info
    - `{{ viewer3d }}`: Insert interactive 3D depiction of the structure. Only available in web UI.
    - `{{ image }}`: Static depiction of the structure. Requires PyMol (not available on public demo!)
    - `{{ cartesians }}`: Molecule structure exported in XYZ format.
- Functions
    - `{{ convertor(value, from_unit, to_unit) }}` can be used to change units in most cases. If not, you can always use normal math inside the curly braces (`{{ (10+value)**2 }}`).

## Missing Values

An additional flag `missing` is passed to the template to control what to report when the requested field is missing in the file. By default, in the WebUI, maximum length is restricted to 10 chars.

In the `default.md` template, `missing` is checked in every row to control if the row should be written or not. If `missing` is set to the empty string `''` (default value) and the value is not present in the file, the row won't be written; if missing is set to any other string (for example, `N/A`) and the value is not present, the row will be written but the value will be reported as `N/A`.

For example, if `stoichiometry` is not available in the file:

__Case A__ (`missing = ''`, default)

    # dvb_gopt

    - Electronic Energy (eV): -5.16295044221

__Case B__: (`missing = 'N/A'`)

    # dvb_gopt

    - Stoichiometry: N/A
    - Electronic Energy (eV): -5.16295044221