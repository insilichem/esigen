# {{name}}

{% if web %}
{{ viewer3d }}
{% elif preview %}
![{{name}}]({{image}})
{% endif %}

__Requested operations__

`{{ route }}`

__Relevant magnitudes__

| Datum                                            | Value                     |
|:-------------------------------------------------|--------------------------:|
{% if show_NAs or stoichiometry != 'N/A' %}
| Stoichiometry                                    | {{stoichiometry|center(25)}} |
{% endif %}
{% if show_NAs or basis_functions != 'N/A' %}
| Number of Basis Functions                        | {{basis_functions|center(25)}} |
{% endif %}
{% if show_NAs or electronic_energy != 'N/A' %}
| Electronic Energy (eV)                           | {{electronic_energy|center(25)}} |
{% endif %}
{% if show_NAs or zeropoint_energy != 'N/A' %}
| Sum of electronic and zero-point Energies (eV)   | {{zeropoint_energy|center(25)}} |
{% endif %}
{% if show_NAs or thermal_energy != 'N/A' %}
| Sum of electronic and thermal Energies (eV)      | {{thermal_energy|center(25)}} |
{% endif %}
{% if show_NAs or enthalpy != 'N/A' %}
| Sum of electronic and thermal Enthalpies (eV)    | {{enthalpy|center(25)}} |
{% endif %}
{% if show_NAs or free_energy != 'N/A' %}
| Sum of electronic and thermal Free Energies (eV) | {{free_energy|center(25)}} |
{% endif %}
{% if show_NAs or imaginary_frequencies != 'N/A' %}
| Number of Imaginary Frequencies                  | {{imaginary_frequencies|center(25)}} |
{% endif %}
{% if show_NAs or mean_of_electrons != 'N/A' %}
| Mean of alpha and beta Electrons                 | {{mean_of_electrons|center(25)}} |
{% endif %}

__Molecular Geometry in Cartesian Coordinates__

```xyz
{{cartesians}}
```

***