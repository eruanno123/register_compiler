/*****************************************************************************/
/* Module: {{ module_name }}
 */
module {{ module_name }} (
    input               clk,
    input               resetn,

    /* SW interface ({{ interface_name }}) */
    {{ interface_ports | indent(4) }}

    /* HW interface */
    {{ hw_ports }}
);

/* Signals ----------------------------------------------------------------- */

wire              sw_select;
wire [31:0]       sw_address;
wire              sw_enable;
wire              sw_write;
wire [31:0]       sw_wdata;
wire [31:0]       sw_rdata;
wire              sw_ready;
wire              sw_error;
wire              sw_interrupt;

/* Modules ----------------------------------------------------------------- */

{{ module_name }}_interface iface   (.*);
{{ module_name }}_backend   backend (.*);

/* State machine ----------------------------------------------------------- */


/* Interface assignment ---------------------------------------------------- */


endmodule: {{ module_name }}
