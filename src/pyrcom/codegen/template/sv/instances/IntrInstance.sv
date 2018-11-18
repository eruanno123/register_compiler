{{ module_name }}_intr #(.ACTIVATION_TYPE ("ENABLE"))
intr_{{ node.intr_name }}
(
    .intr_enable    (intr_{{ node.intr_name }}_enable),
    .intr_set       (intr_{{ node.intr_name }}_set),
    .intr_clear     (intr_{{ node.intr_name }}_clear),
    .intr_status    (intr_{{ node.intr_name }}_status),
    .*
);