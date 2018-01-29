# {{name}}

{% if preview == 'web' %}
{{ viewer3d }}
{% elif preview in ('static', 'static_server') %}
![{{name}}]({{image}})
{% endif %}

__Requested operations__

`{{ route }}`

__Relevant magnitudes__

{% set label_value = (('Charge' , charge),
                      ('Multiplicity', mult),
                      ('Stoichiometry', stoichiometry),
                      ('Number of Basis Functions', nbasis),
                      ('Electronic Energy (Eh)', electronic_energy),
                      ('Sum of electronic and zero-point Energies (Eh)', zeropointenergy),
                      ('Sum of electronic and thermal Energies (Eh)', thermalenergy),
                      ('Sum of electronic and enthalpy Energies (Eh)', enthalpy),
                      ('Sum of electronic and thermal Free Energies (Eh)', freeenergy),
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

__Excited states__

{% for state in etsecs[:5] %}
{% set symmetry = etsyms[loop.index-1] %}
{% set energy = convertor(etenergies[loop.index-1], "cm-1", "eV") %}
{% set strength = etoscs[loop.index-1] %}

**Excited state #{{ loop.index }}**: {{ symmetry }}

E={{energy}}eV, f={{ strength }}

{% for transition in state %}
- {{ transition[0][0] + 1 }}->{{ transition[1][0] + 1 }} = {{ '{: 5.2%}'.format(transition[2]**2) }}

{% endfor %}
{% endfor %}

***