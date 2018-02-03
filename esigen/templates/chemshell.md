# {{name}}

{% if preview == 'web' %}
{{ viewer3d }}
{% elif preview %}
![{{name}}]({{image}})
{% endif %}
- Converged: {{ optdone }}
- {{ 'QM/MM Energy'.ljust(37) }}: {{ scfenergies[-1] }} a.u.
{% if energycontributions is defined %}
{% for contribution, energy in energycontributions[-1].items() %}
  + {{ contribution.ljust(35) }}: {{ energy }}
{% endfor %}
{% endif %}
{% if mmenergies is defined %}
{% set total=mmenergies[-1].pop('total') %}
- {{'MM Energies'.ljust(37)}}: {{ total }}
{% for contribution, energy in mmenergies[-1].items() %}
  + {{ contribution.ljust(35) }}: {{ energy }}
{% endfor %}
{% endif %}