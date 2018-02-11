{{ '-' * len(name) }}
{{ name }}
{{ '-' * len(name) }}

Electronic energy: {{ electronic_energy }} Eh
{% if imaginary_freqs != missing %}
Number of imaginary frequencies: {{ imaginary_freqs }}
{% for freq in vibfreqs[vibfreqs < 0] %}
    {{ freq }}
{% endfor %}
{% endif %}


Convergence
-----------
Converged after {{ nsteps }} fully completed steps: {{ optdone }}
{% if nsteps < scftargets.shape[0] %}
! {{nsteps}} steps were completed, but {{ scftargets.shape[0] }} were attempted. Early termination?
{% endif %}
{% if optdone != True %}
SCF convergence in latest steps
{% for step, (target, values) in enumerate(zip(scftargets[-5:], scfvalues[-5:]), scftargets.shape[0] - 4) %}
- #{{ step }}: {{ ', '.join(map(str, (values[-1] < target))) }}
{% endfor %}
{% endif %}

{% if geovalues != missing %}
{% set geoconverged_query = (geovalues[slice(None), slice(0,2)] < geotargets[0:2]).all(axis=1) %}
{% set geoconverged_idx = np.argwhere(geoconverged_query).flatten() %}
{% set geoconverged_status = (geovalues[geoconverged_idx] < geotargets) %}

Geometric convergence found at steps:
{% for cycle, status in zip(geoconverged_idx, geoconverged_status) %}
- #{{ cycle + 1 }}: {{ ', '.join(map(str, status)) }}
{% endfor %}

{% if 0 %}
Coordinates for latest geometrically converged structure (#{{geoconverged_idx.max() + 1}})
{% for atom, xyz in zip(atoms, atomcoords[geoconverged_idx.max()]) %}
{{ '{:4} {: 15.6f} {: 15.6f} {: 15.6f}'.format(atom, *xyz) }}
{% endfor %}
{% endif %}
{% endif %}
***