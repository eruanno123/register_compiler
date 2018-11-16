/*****************************************************************************/
/* Module: {{ module_root_name }}
 */
module {{ module_root_name }} (
    input               clk,
    input               resetn,

    /* SW interface (APB) */
    {{ sw_ports }}

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

{{ module_root_name }}_interface iface   (.*);
{{ module_root_name }}_backend   backend (.*);

/* State machine ----------------------------------------------------------- */


/* Interface assignment ---------------------------------------------------- */


endmodule: {{ module_root_name }}
