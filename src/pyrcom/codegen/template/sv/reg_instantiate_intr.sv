/*** Interrupt: {{ intr_name }} ***/
{{ module_root_name }}_intr #(.ACTIVATION_TYPE ("ENABLE"))
intr_{{ intr_name }}
(
    .intr_enable    (intr_{{ intr_name }}_enable),
    .intr_mask      (1'b0),
    .intr_set       (intr_{{ intr_name }}_set),
    .intr_clear     (intr_{{ intr_name }}_clear),
    .intr_status    (intr_{{ intr_name }}_status),
    .*
);