/*****************************************************************************/
/* Module: {{ module_name }}
 */
module {{ module_name }} #(
    int                     FIELD_WIDTH = 32,
    bit [FIELD_WIDTH-1:0]   RESET_MASK  = 0,
    bit [FIELD_WIDTH-1:0]   RESET_VALUE = 0
)(
    input                       clk,
    input                       resetn,
    input                       write,
    input  [FIELD_WIDTH-1:0]    din,
    output [FIELD_WIDTH-1:0]    dq
);

/* Signals ----------------------------------------------------------------- */

logic   [FIELD_WIDTH-1:0]       field_data;

/* Modules ----------------------------------------------------------------- */

/* State machine ----------------------------------------------------------- */

generate
    genvar bitpos;

    for (bitpos = 0; bitpos < FIELD_WIDTH; bitpos = bitpos + 1) begin
        always_ff @(posedge clk or negedge resetn)
        begin
            if (!resetn && RESET_MASK[bitpos])
                field_data[bitpos] <= RESET_VALUE[bitpos];
            else if (write)
                field_data[bitpos] <= din[bitpos];
        end
    end
endgenerate

/* Interface assignment ---------------------------------------------------- */

assign dq = field_data;

endmodule: {{ module_name }}


