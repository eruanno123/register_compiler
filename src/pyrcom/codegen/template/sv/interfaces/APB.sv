assign sw_select    = psel;
assign sw_address   = paddr;
assign sw_enable    = penable;
assign sw_write     = pwrite;
assign sw_wdata     = pwdata;

assign prdata       = sw_rdata;
assign pready       = sw_ready;
assign pslverr      = sw_error;
assign interrupt    = sw_interrupt;