# Using ESIgen programmatically

ESIgen is only a wrapper around the excellent `cclib` project, which handles the tedious job of parsing computational chemistry logfiles. It then provides all the parsed fields to a `Jinja2` templating engine via the main class, `esigen.core.ESIgenReport`. This class also hooks to several molecular viewers implemented in `esigen.render` (PyMol, NGLView, ChemView). The API is straight-forward:

    from esigen import ESIgenReport
    reporter = ESIgenReport(logfile_path)
    all_fields = reporter.data_as_dict()
    subyacent_ccdata = reporter.data
    # Fill template with parsed data ()
    print(reporter.report(template='default.md'))
    # If inside Jupyter Notebook, get an interactive preview
    reporter.view_with_nglview()

Check the docstrings for `ESIgenReport` and `ESIgenReport.report()` for more information on available options.

## How to extend ESIgen

__TLDR__: Check the source for the `esigen.io` module.

Extending ESIgen to add support for more fields should not be necessary. Instead, contributing to `cclib` is preferred and, that way, other users will benefit from the new additions. That said, we do add some fields in ESIgen for the sake of easy templating. This is controlled in the `esigen.io.ccDataExtended` class, which is a subclass of the original `cclib.parser.data.ccData_optdone_bool` class, responsible of holding the data fields (as listed [here](http://cclib.github.io/data.html)). Our subclass creates a few property methods (functions that can be called as attributes, without the `()` syntax) that serve as aliases to compute some properties on the fly based on the existing (static) fields. If you want to add more, subclass `esigen.io.ccDataExtended`, add the properties and overwrite the `_properties` class attribute to reflect the new additions:

    from esigen.io import ccDataExtended
    class ccDataExtendedExtra(ccDataExtended):
        _properties = ccDataExtended._properties[:] + ['my_new_property']

        @property
        def my_new_property(self):
            return 'Custom value computed out of static fields'

This is needed because `esigen.io.ccDataExtended` defines a new method `as_dict`, that acts as the original `ccData.getattributes`, but also collecting the values from all the elements defined in `_properties`.

Temporarily, we have also added some more static attributes and subclassed the original `GaussianParser` (based on `cclib.parser.Gaussian`) to fill them in by adding more rules in `esigen.io.GaussianParser.extract`. Eventually, these new fields will be available in `cclib`, but in the meantime you can use these.

All the code in this module (`esigen.io`) can serve as an example on how to extend ESIgen to fill your own needs. You only have to change the default parameters during the creation of your ESIgenReport objects:

    from esigen import ESIgenReport
    # default
    report = ESIgenReport(logfile_path)
    # custom parser, default datatype
    report = ESIgenReport(logfile_path, parser=your_parsing_function)
    # default parser, custom datatype (maybe you want to define more properties)
    report = ESIgenReport(logfile_path, datatype=ccDataCustomSubclass)