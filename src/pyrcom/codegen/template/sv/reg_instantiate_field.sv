/*** Field: {{ field_name }} ***/
{{ module_root_name }}_field #(.FIELD_WIDTH({{ field_width }}), .RESET_MASK({{ field_reset_mask }}), .RESET_VALUE({{ field_reset_value }}))
field_{{ reg_name }}__{{ field_name }} (
    .write (reg_{{ reg_name }}__select),
    .din   (reg_{{ reg_name }}__data_in[{{ field_range }}]),
    .dq    (reg_{{ reg_name }}__data_out[{{ field_range }}]),
    .*
);