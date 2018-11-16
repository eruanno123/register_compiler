/*****************************************************************************/
/* Module: {{ module_root_name }}_backend
 *
 * Register backend.
 * Connect SW ports to the desired register interface.
 * Connect HW ports to custom logic.
 */
module {{ module_root_name }}_backend (
    input               clk,
    input               resetn,

    /* HW ports */
    {% for port in hw_ports %}
    {{ "%-7s" | format(port.direction) }}{% if port.width != None %}{{ "%-13s" | format(port.width) }}{% else %}             {% endif %}{{ port.name }},
    {% endfor %}

    /* SW ports */
    input               sw_select,
    input  [31:0]       sw_address,
    input               sw_enable,
    input               sw_write,
    input  [31:0]       sw_wdata,
    output [31:0]       sw_rdata,
    output              sw_ready,
    output              sw_error,
    output              sw_interrupt
);

/* Parameters -------------------------------------------------------------- */

typedef enum bit [1:0] {
    SW_STATE_IDLE           = 2'd0,
    SW_STATE_READ_ACCESS    = 2'd1,
    SW_STATE_WRITE_ACCESS   = 2'd2
} sw_state_t;

/* Signals ----------------------------------------------------------------- */

sw_state_t          sw_state;

logic [1:0]         sw_decode_address;
logic               sw_decode_select_valid;
logic [31:0]        sw_decode_rdata_w;
logic [31:0]        sw_decode_rdata;
logic               sw_decode_rdata_valid;
logic               sw_decode_ready;
logic               sw_interrupt_request_w;
logic               sw_interrupt_request;

{{ backend_signal_definitions }}

/* Modules ----------------------------------------------------------------- */

{{ backend_instantiation }}

/* State machine ----------------------------------------------------------- */

/* TODO: use Hamming code to represent APB bus state */
always_ff @(posedge clk or negedge resetn)
begin
    if (!resetn) begin
        sw_state <= SW_STATE_IDLE;
    end else begin
        case (sw_state)
            SW_STATE_IDLE:
                /* TODO assert PENABLE = 1 in idle */
                if (sw_select) begin
                    if (sw_write)
                        sw_state <= SW_STATE_WRITE_ACCESS;
                    else
                        sw_state <= SW_STATE_READ_ACCESS;
                end

            SW_STATE_WRITE_ACCESS, SW_STATE_READ_ACCESS:
                /* TODO assert PSEL = 0 */
                if (sw_enable)
                    sw_state <= SW_STATE_IDLE;

            default: ;
               /* assert */
        endcase
    end
end

/* Decoder address */
always_ff @(posedge clk or negedge resetn)
begin
    if (!resetn)
        sw_decode_address <= 0;
    else if (sw_select)
        sw_decode_address <= sw_address[3:2];
end

/***
 *** Write select decoder
 ***/
always_comb
begin
    {{ write_select_init }}
    sw_decode_select_valid      = 1'b0;

    if (sw_state == SW_STATE_WRITE_ACCESS) begin
        sw_decode_select_valid  = 1'b1;
        case (sw_decode_address)
            {{ write_select_cases }}
            default: /* TODO: decode error */
                    sw_decode_select_valid  = 1'b0;
        endcase
    end // sw_state == SW_STATE_WRITE_ACCESS
end

/***
 *** Read data decoder
 ***/
always_comb
begin
    sw_decode_rdata_w           = 0;
    sw_decode_rdata_valid       = 1'b0;

    if (sw_state == SW_STATE_READ_ACCESS) begin
        sw_decode_rdata_valid   = 1'b1;
        case (sw_decode_address)
            {{ read_data_cases }}
            default: /* TODO: decode error */
                    sw_decode_rdata_valid = 1'b0;
        endcase
    end // sw_state == SW_STATE_READ_ACCESS
end
/* pipeline read data register with corresponding sw_ready */
always_ff @(posedge clk)
begin
    sw_decode_rdata <= sw_decode_rdata_w;
    sw_decode_ready <= sw_enable;
    /* TODO: sw_decode_error = ~sw_decode_rdata_valid | sw_decode_select_valid; */
end


{{ interrupt_woclr }}
{{ interrupt_port }}

/* Internal assignment ----------------------------------------------------- */

{{ internal_assignments }}

/* Interface assignment ---------------------------------------------------- */

assign sw_error         = 1'b0; /* TODO: handle decode/access error */
assign sw_ready         = sw_decode_ready;
assign sw_rdata         = sw_decode_rdata;
assign sw_interrupt     = sw_interrupt_request;

{{ interface_assignments }}

/* Linting ----------------------------------------------------------------- */

/* Undriven nets */
{{ linter_undriven }}

/* Unused nets */
wire _unused = & {
    {{ linter_unused }}
};

endmodule: {{ module_root_name }}_backend
