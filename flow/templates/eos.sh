{% extends "torque.sh" %}
{% block tasks %}
{% set nn = nn|default((num_tasks/24)|round(method='ceil')|int, true) %}
#PBS -l nodes={{ nn }}
{% endblock %}
{% block header %}
{{ super() -}}
{% set account = 'account'|get_config_value(ns=environment) %}
{% if account %}
#PBS -A {{ account }}
{% endif %}
{% endblock %}
