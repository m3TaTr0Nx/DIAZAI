`timescale 1ns/1ps
// Fixed radix-3 DIT schedule for N=729=3^6.
// Emits one butterfly address triple and the twiddle exponents per cycle.
// Exactly 6 * (729/3) = 1458 butterflies are emitted.
module dmr_ntt729_schedule(
    input  logic clk,
    input  logic rst_n,
    input  logic start,
    output logic busy,
    output logic valid,
    output logic done,
    output logic [2:0] stage,
    output logic [9:0] addr_a,
    output logic [9:0] addr_b,
    output logic [9:0] addr_c,
    output logic [9:0] twiddle_exp_b,
    output logic [9:0] twiddle_exp_c
);
    integer span, m, groups, j, g;
    integer base, step, exp1;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            busy <= 1'b0; valid <= 1'b0; done <= 1'b0;
            stage <= 3'd0; j <= 0; g <= 0;
            addr_a <= '0; addr_b <= '0; addr_c <= '0;
            twiddle_exp_b <= '0; twiddle_exp_c <= '0;
        end else begin
            done <= 1'b0;
            valid <= 1'b0;
            if (start && !busy) begin
                busy <= 1'b1;
                stage <= 3'd0;
                j <= 0;
                g <= 0;
            end else if (busy) begin
                span = 1;
                for (integer s = 0; s < stage; s = s + 1) span = span * 3;
                m = span * 3;
                groups = 729 / m;
                base = g * m;
                step = 729 / m;
                exp1 = (j * step) % 729;

                addr_a <= base + j;
                addr_b <= base + j + span;
                addr_c <= base + j + 2*span;
                twiddle_exp_b <= exp1;
                twiddle_exp_c <= (2*exp1) % 729;
                valid <= 1'b1;

                if (j == span-1) begin
                    j <= 0;
                    if (g == groups-1) begin
                        g <= 0;
                        if (stage == 5) begin
                            busy <= 1'b0;
                            done <= 1'b1;
                        end else begin
                            stage <= stage + 1'b1;
                        end
                    end else begin
                        g <= g + 1;
                    end
                end else begin
                    j <= j + 1;
                end
            end
        end
    end
endmodule
