{{ module_name }}_field #(.FIELD_WIDTH({{ node.field_width }}), .RESET_MASK({{ node.field_reset_mask }}){% if node.field_reset_value != None %}, .RESET_VALUE({{ node.field_reset_value }}){% endif %})
field_{{ node.parent_reg_name }}__{{ node.field_name }} (
    .write (reg_{{ node.parent_reg_name }}__select),
    .din   (reg_{{ node.parent_reg_name }}__data_in{{ node.field_range }}),
    .dq    (reg_{{ node.parent_reg_name }}__data_out{{ node.field_range }}),
    .*
);