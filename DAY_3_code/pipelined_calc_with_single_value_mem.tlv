\m4_TLV_version 1d: tl-x.org
\SV

   // =========================================
   // Welcome!  Try the tutorials via the menu.
   // =========================================

   // Default Makerchip TL-Verilog Code Template
   
   // Macro providing required top-level module definition, random
   // stimulus support, and Verilator config.
   m4_makerchip_module   // (Expanded in Nav-TLV pane.)
\TLV
   
   // we need to make sure the logic is valid druing the reset
   // therefore we use valid_or_reset
   
   // we need not necessarily make the loop for mux instead in physically 
   // we could just block the clock (avoiding the clock) input to the flip-flop 
   // using clock gating to make flip-flop retain its value
   
   |calc
      @0
         $reset = *reset;
      @1
         $valid = $reset ? 0 : (1 + >>1$valid);
         $valid_or_reset = $valid || $reset;
         $val1[31:0] = >>2$out[31:0];
         $val2[31:0] = $rand2[3:0];
         // 3 bit op
         $op[2:0] = $rand3[2:0];

      ?$valid_or_reset
         @1
            $sum[31:0] = $val1[31:0] + $val2[31:0];
            $diff[31:0] = $val1[31:0] - $val2[31:0];
            $prod[31:0] = $val1[31:0] * $val2[31:0];
            $quot[31:0] = $val1[31:0] / $val2[31:0];
         @2
            $out[31:0] = $valid_or_reset ? 32'b0:
                                 (($op == 3'b000) ? $sum :
                                   ($op == 3'b001) ? $diff :
                                     ($op == 3'b010) ? $prod :
                                       ($op == 3'b011) ? $quot:
                                          ($op == 3'b100) ? >>2$mem:
                                             >>2$out);
            $mem[31:0] = $valid_or_reset ? 32'b0:
                           (($op == 3'b100) ? $val1: >>2$mem);

            
   // Assert these to end simulation (before Makerchip cycle limit).
   *passed = *cyc_cnt > 40;
   *failed = 1'b0;
\SV
   endmodule
