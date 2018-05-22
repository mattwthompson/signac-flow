{% block resources %}
{# Number of tasks is the same for any script type #}
{% if parallel %}
{% set num_tasks = operations|map(attribute='directives.np')|sum %}
{% else %}
{% set num_tasks = operations|map(attribute='directives.np')|max %}
{% endif %}
{% endblock %}
{% block header %}
{% endblock %}

{% block project_header %}
set -e
set -u

cd {{ project.config.project_dir }}
{% endblock %}

{% block body %}
{% set suffix_cmd = suffix_cmd|default('') + (' &' if parallel else '') %}
{% for operation in operations %}
# Operation '{{ operation.name }}' for job '{{ operation.job._id }}':
{{ prefix_cmd }}{{ operation.cmd }}{{ suffix_cmd }}
{% endfor %}
{% if parallel %}
wait
{% endif %}
{% endblock %}
{% block footer %}
{% endblock %}
