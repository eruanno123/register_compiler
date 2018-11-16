/*****************************************************************************/
/* Module: {{ module_root_name }}_intr
 */
module {{ module_root_name }}_intr #(
    string ACTIVATION_TYPE = "ENABLE"
)
(
    input               clk,
    input               resetn,
    input               intr_enable,
    input               intr_mask,
    input               intr_set,
    input               intr_clear,
    output logic        intr_status
);

/* Signals ----------------------------------------------------------------- */

wire  intr_activated;
wire  _unused; /* keep verilator lint calm */

/* State machine ----------------------------------------------------------- */

/* Select interrupt activation scheme */
generate
    case (ACTIVATION_TYPE)
        "ENABLE": begin
            assign intr_activated =  intr_enable;
            assign _unused        =  intr_mask;
        end
        "MASK": begin
            assign intr_activated = ~intr_mask;
            assign _unused        =  intr_enable;
        end
        default: begin
            assign intr_activated =  1'b1;
            assign _unused        = & {intr_enable, intr_mask};
        end
    endcase
endgenerate

/* Interrupt status register */
always_ff @(posedge clk or negedge resetn)
begin
    if (!resetn)
        intr_status <= 1'b0;
    else begin
        if (intr_set && intr_activated)
            intr_status <= 1'b1;
        else if (intr_clear)
            intr_status <= 1'b0;
    end
end

endmodule: {{ module_root_name }}_intr
