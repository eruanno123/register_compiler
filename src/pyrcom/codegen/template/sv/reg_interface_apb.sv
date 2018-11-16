/*****************************************************************************/
/* Module: {{ module_root_name }}_interface
 */
module {{ module_root_name }}_interface (
    /* verilator lint_off UNUSED */
    input               clk,
    input               resetn,
    /* verilator lint_on UNUSED */

    /* APB slave interface */
    input   [31:0]      paddr,
    input               pwrite,
    input               psel,
    input               penable,
    input   [31:0]      pwdata,
    output  [31:0]      prdata,
    output              pready,
    output              pslverr,
    output              interrupt,

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

    assign sw_select    = psel;
    assign sw_address   = paddr;
    assign sw_enable    = penable;
    assign sw_write     = pwrite;
    assign sw_wdata     = pwdata;

    assign prdata       = sw_rdata;
    assign pready       = sw_ready;
    assign pslverr      = sw_error;
    assign interrupt    = sw_interrupt;

endmodule: {{ module_root_name }}_interface
