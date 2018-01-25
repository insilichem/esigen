# {{name}}

{% if preview == 'web' %}
{{ viewer3d }}
{% elif preview %}
![{{name}}]({{image}})
{% endif %}

__Requested operations__

`{{ route }}`

__Relevant magnitudes__

{% set label_value = (('Charge' , charge),
                      ('Multiplicity', mult),
                      ('Stoichiometry', stoichiometry),
                      ('Number of Basis Functions', nbasis),
                      ('Electronic Energy (eV)', electronic_energy),
                      ('Sum of electronic and zero-point Energies (eV)', zeropointenergies),
                      ('Sum of electronic and thermal Energies (eV)', thermalenergies),
                      ('Sum of electronic and thermal Free Energies (eV)', freeenergy),
                      ('Number of Imaginary Frequencies', imaginary_freqs),
                      ('Mean of alpha and beta Electrons', mean_of_electrons),
                     )
%}

| Datum                                            | Value                     |
|:-------------------------------------------------|--------------------------:|
{% for label, value in label_value %}
{% if missing or value != missing %}
| {{label.ljust(48)}} | {{value|center(25)}} |
{% endif %}
{% endfor %}

__Molecular Geometry in Cartesian Coordinates__

```xyz
{{cartesians}}
```
{% if vibfreqs != missing %}

__Frequencies__

```
{% for freq in vibfreqs[:10] %}
{{'{:>3d}'.format(loop.index)}}. {{ '{: 12.4f}'.format(freq) }} cm-1 (Symmetry: {{vibsyms[loop.index-1]}}) {% if freq < 0 %} * {% endif %}

{% endfor %}
```
{% endif %}
***