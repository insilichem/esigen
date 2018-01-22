# {{name}}

{% if preview == 'web' %}
{{ viewer3d }}
{% elif preview in ('static', 'static_server') %}
![{{name}}]({{image}})
{% endif %}

__Requested operations__

`{{ route }}`

__Relevant magnitudes__

| Datum                                            | Value                     |
|:-------------------------------------------------|--------------------------:|
{% if missing or charge != missing %}
| Charge                                           | {{charge|center(25)}} |
{% endif %}
{% if missing or mult != missing %}
| Multiplicity                                     | {{mult|center(25)}} |
{% endif %}
{% if missing or stoichiometry != missing %}
| Stoichiometry                                    | {{stoichiometry|center(25)}} |
{% endif %}
{% if missing or nbasis != missing %}
| Number of Basis Functions                        | {{nbasis|center(25)}} |
{% endif %}
{% if missing or electronic_energy != missing %}
| Electronic Energy (eV)                           | {{electronic_energy|center(25)}} |
{% endif %}
{% if missing or zeropointenergies != missing %}
| Sum of electronic and zero-point Energies (eV)   | {{zeropointenergies|center(25)}} |
{% endif %}
{% if missing or thermalenergies != missing %}
| Sum of electronic and thermal Energies (eV)      | {{thermalenergies|center(25)}} |
{% endif %}
{% if missing or enthalpy != missing %}
| Sum of electronic and thermal Enthalpies (eV)    | {{enthalpy|center(25)}} |
{% endif %}
{% if missing or freeenergy != missing %}
| Sum of electronic and thermal Free Energies (eV) | {{freeenergy|center(25)}} |
{% endif %}
{% if missing or imaginaryfreqs != missing %}
| Number of Imaginary Frequencies                  | {{imaginaryfreqs|center(25)}} |
{% endif %}
{% if missing or mean_of_electrons != missing %}
| Mean of alpha and beta Electrons                 | {{mean_of_electrons|center(25)}} |
{% endif %}

__Molecular Geometry in Cartesian Coordinates__

```xyz
{{cartesians}}
```

***