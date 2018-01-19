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
{% if show_NAs or charge != 'N/A' %}
| Charge                                           | {{charge|center(25)}} |
{% endif %}
{% if show_NAs or mult != 'N/A' %}
| Multiplicity                                     | {{mult|center(25)}} |
{% endif %}
{% if show_NAs or stoichiometry != 'N/A' %}
| Stoichiometry                                    | {{stoichiometry|center(25)}} |
{% endif %}
{% if show_NAs or nbasis != 'N/A' %}
| Number of Basis Functions                        | {{nbasis|center(25)}} |
{% endif %}
{% if show_NAs or electronic_energy != 'N/A' %}
| Electronic Energy (eV)                           | {{electronic_energy|center(25)}} |
{% endif %}
{% if show_NAs or zeropointenergies != 'N/A' %}
| Sum of electronic and zero-point Energies (eV)   | {{zeropointenergies|center(25)}} |
{% endif %}
{% if show_NAs or thermalenergies != 'N/A' %}
| Sum of electronic and thermal Energies (eV)      | {{thermalenergies|center(25)}} |
{% endif %}
{% if show_NAs or enthalpy != 'N/A' %}
| Sum of electronic and thermal Enthalpies (eV)    | {{enthalpy|center(25)}} |
{% endif %}
{% if show_NAs or freeenergy != 'N/A' %}
| Sum of electronic and thermal Free Energies (eV) | {{freeenergy|center(25)}} |
{% endif %}
{% if show_NAs or imaginaryfreqs != 'N/A' %}
| Number of Imaginary Frequencies                  | {{imaginaryfreqs|center(25)}} |
{% endif %}
{% if show_NAs or mean_of_electrons != 'N/A' %}
| Mean of alpha and beta Electrons                 | {{mean_of_electrons|center(25)}} |
{% endif %}

__Molecular Geometry in Cartesian Coordinates__

```xyz
{{cartesians}}
```

***