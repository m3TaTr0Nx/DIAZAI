`timescale 1ns/1ps
// Exact 3-point NTT butterfly over F_58321.
// Reference-synthesis implementation: uses % for modular reduction.
// The comparator intentionally keeps this simple; a Barrett/Montgomery version
// should be benchmarked as a separate microarchitecture, not silently substituted.
module dmr_butterfly3_58321 #(
    parameter int P = 58321,
    parameter int W = 16,
    parameter int OMEGA3 = 30624,
    parameter int OMEGA3_SQ = 27696
)(
    input  logic [W-1:0] a,
    input  logic [W-1:0] b,
    input  logic [W-1:0] c,
    output logic [W-1:0] y0,
    output logic [W-1:0] y1,
    output logic [W-1:0] y2
);
    function automatic logic [W-1:0] mod_add3(
        input logic [W-1:0] x,
        input logic [W-1:0] y,
        input logic [W-1:0] z
    );
        logic [W+1:0] s;
        begin
            s = x + y + z;
            mod_add3 = s % P;
        end
    endfunction

    function automatic logic [W-1:0] mod_mul(
        input logic [W-1:0] x,
        input integer k
    );
        logic [2*W-1:0] ptmp;
        begin
            ptmp = x * k;
            mod_mul = ptmp % P;
        end
    endfunction

    logic [W-1:0] wb, w2b, wc, w2c;
    always_comb begin
        wb  = mod_mul(b, OMEGA3);
        w2b = mod_mul(b, OMEGA3_SQ);
        wc  = mod_mul(c, OMEGA3);
        w2c = mod_mul(c, OMEGA3_SQ);
        y0  = mod_add3(a, b, c);
        y1  = mod_add3(a, wb,  w2c);
        y2  = mod_add3(a, w2b, wc);
    end
endmodule
