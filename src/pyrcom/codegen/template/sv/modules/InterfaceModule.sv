/*****************************************************************************/
/* Module: {{ module_name }}
 */
module {{ module_name }} (
    /* verilator lint_off UNUSED */
    input               clk,
    input               resetn,
    /* verilator lint_on UNUSED */

    /* SW interface ({{ interface_name }}) */
    {{ interface_ports | indent(4) }}

    /* Backend interface */
    output              sw_select,
    output [31:0]       sw_address,
    output              sw_enable,
    output              sw_write,
    output [31:0]       sw_wdata,
    input [31:0]        sw_rdata,
    input               sw_ready,
    input               sw_error,
    input               sw_interrupt
);

{{ interface_code }}

endmodule: {{ module_name }}


