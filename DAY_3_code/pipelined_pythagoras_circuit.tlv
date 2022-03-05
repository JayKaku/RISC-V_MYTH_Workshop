\m4_TLV_version 1d: tl-x.org
\SV

   // =========================================
   // Welcome!  Try the tutorials via the menu.
   // =========================================

   // Default Makerchip TL-Verilog Code Template
   
   // Macro providing required top-level module definition, random
   // stimulus support, and Verilator config.

   `include "sqrt32.v";
   m4_makerchip_module   // (Expanded in Nav-TLV pane.)
\TLV

   //$aa_sq[7:0] = $rand1[4:0];
   //$bb_sq[7:0] = $rand2[4:0];
   
   // here we'll be retaining (>>1$total_dist or $RETAIN) the value of 
   // total_distance till the next valid cycle
   // iff valid ? new_cc + total_dist
   
   |calc
      @1
         $reset = *resert;
      ?$valid
         @1
            $aa_sq[31:0] = $aa[3:0] * $aa;
            $bb_sq[31:0] = $bb[3:0] * $bb;
         @2
            $cc_sq[31:0] = $aa_sq + $bb_sq;
         @3
            $cc[31:0] = sqrt($cc_sq);
      @4
         $total_dist[64:0] =
               $reset ? '0 :
               $valid ? >>1$total_dist + $cc :
                        $RETAIN;
         
   // Assert these to end simulation (before Makerchip cycle limit).
   *passed = *cyc_cnt > 40;
   *failed = 1'b0;
\SV
   endmodule
