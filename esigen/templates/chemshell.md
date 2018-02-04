# {{name}}

- Converged after {{ nsteps }} cycles: {{ optdone }}

- {{ 'QM/MM Energy'.ljust(37) }}: {{ scfenergies[-1] }} a.u.
{% if energycontributions != missing %}
{% for contribution, energy in energycontributions[-1].items() %}
    + {{ contribution.ljust(33) }}: {{ energy }}
{% endfor %}
{% endif %}

{% if mmenergies != missing %}
{% set total=mmenergies[-1].pop('total') %}
- {{'MM Energies'.ljust(37)}}: {{ total }}
{% for contribution, energy in mmenergies[-1].items() %}
    + {{ contribution.ljust(33) }}: {{ energy }}
{% endfor %}
{% endif %}