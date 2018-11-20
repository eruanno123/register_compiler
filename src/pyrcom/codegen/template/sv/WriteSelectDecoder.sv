always_comb
begin
    {% for d in address_map %}
    {{ "%-27s = 1'b0;" | format(d[1]) }}{% endfor %}
    sw_decode_select_valid      = 1'b0;

    if (sw_state == SW_STATE_WRITE_ACCESS) begin
        sw_decode_select_valid  = 1'b1;
        case (sw_decode_address)
            {% for d in address_map %}
            {{ d[0] | verilog_literal("x") }}: {{ "%-27s = 1'b1;" | format(d[1]) }}{% endfor %}
            default: /* TODO: decode error */
                    sw_decode_select_valid  = 1'b0;
        endcase
    end // sw_state == SW_STATE_WRITE_ACCESS
end