/***
 *** REGISTER FILE DEFINITION
 ***/

{% for rg in register_instances %}
/*** Register: {{ rg.name }} ({{ rg.address_offset }}) ***/
{{ rg.register_inst_code }}

{% endfor %}

/***
 *** INTERRUPT DEFINITION
 ***/

{% for intr in interrupt_instances %}
{{ intr.interrupt_inst_code }}

{% endfor %}