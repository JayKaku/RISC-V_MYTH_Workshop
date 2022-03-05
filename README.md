# RISC-V based Microprocessor

This repository contains all the information needed to build your RISC-V pipelined core, which has support of base interger RV32I instruction format using TL-Verilog on [makerchip](https://makerchip.com/) platform.

# Table of Contents

- [Introduction to RISC-V ISA](#introduction-to-risc-v-isa)
- [Overview of GNU compiler toolchain](#overview-of-gnu-compiler-toolchain)
- [Digital Logic with TL-Verilog and Makerchip](#digital-logic-with-tl-verilog-and-makerchip)
  - [Combinational logic](#combinational-logic)
  - [Sequential logic](#sequential-logic)
  - [Pipelined logic](#pipelined-logic)
  - [Validity](#validity)
- [Basic RISC-V CPU micro-architecture](#basic-risc-v-cpu-micro-architecture)
  - [Fetch](#fetch)
  - [Decode](#decode)
  - [Register File Read and Write](#register-file-read-and-write)
  - [Execute](#execute)
  - [Control Logic](#control-logic)
- [Pipelined RISC-V CPU](#pipelined-risc-v-cpu)
  - [Pipelinig the CPU](#pipelining-the-cpu)
  - [Load and store instructions and memory](#load-and-store-instructions-and-memory)
  - [Completing the RISC-V CPU](#completing-the-risc-v-cpu)
- [Acknowledgements](#acknowledgements)

# Introduction to RISC-V ISA

A RISC-V ISA is defined as a base integer ISA, which must be present in any implementation, plus optional extensions to the base ISA. Each base integer instruction set is characterized by

1. Width of the integer registers (XLEN)
2. Corresponding size of the address space
3. Number of integer registers (32 in RISC-V)

More details on RISC-V ISA can be obtained [here](https://github.com/riscv/riscv-isa-manual/releases/download/draft-20200727-8088ba4/riscv-spec.pdf).

Another greate resource by [John Winans](https://github.com/johnwinans) can be found [here](https://github.com/johnwinans/rvalp/releases?page=1)

# Overview of GNU compiler toolchain

The GNU Toolchain is a set of programming tools in Linux systems that programmers can use to make and compile their code to produce a program or library. So, how the machine code which is understandable by processer is explained below.

- Preprocessor - Process source code before compilation. Macro definition, file inclusion or any other directive if present then are preprocessed.
- Compiler - Takes the input provided by preprocessor and converts to assembly code.
- Assembler - Takes the input provided by compiler and converts to relocatable machine code.
- Linker - Takes the input provided by Assembler and converts to Absolute machine code.

Under the risc-v toolchain,

- To generate the object files

  `riscv64-unknown-elf-gcc -Ofast -mabi=lp64 -march=rv64i -c <C filename>`

- To use the risc-v gcc compiler use the below command:

  `riscv64-unknown-elf-gcc -Ofast -mabi=lp64 -march=rv64i -o <object filename> <C filename>`

  More generic command with different options:

  `riscv64-unknown-elf-gcc <compiler option -O1 ; Ofast> <ABI specifier -lp64; -lp32; -ilp32> <architecture specifier -RV64 ; RV32> -o <object filename> <C filename>`

  More details on compiler options can be obtained [here](https://www.sifive.com/blog/all-aboard-part-1-compiler-args)

- To view assembly code use the below command,

  `riscv64-unknown-elf-objdump -d <object filename>`

- To use SPIKE simualtor to run risc-v obj file use the below command,

  `spike pk <object filename>`

  To use SPIKE as debugger

  `spike -d pk <object Filename>` with degub command as `until pc 0 <pc of your choice>`

  To install complete risc-v toolchain locally on linux machine,

  1. [RISC-V GNU Toolchain](http://hdlexpress.com/RisKy1/How2/toolchain/toolchain.html)
  2. [RISC-V ISA SImulator - Spike](https://github.com/kunalg123/riscv_workshop_collaterals)

  Alternate resources

  1. [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain)
  2. [RISC-V ISA SImulator - Spike](https://github.com/riscv-software-src/riscv-isa-sim)
  3. [RISC-V ISA SImulator - Proxy Kernel for Spike](https://github.com/riscv-software-src/riscv-pk)

  Note: Step 1 of alternate method requires making custom toolchain for `-mabi=lp64 -march=rv64i` which could be looked up [here](https://github.com/riscv-collab/riscv-gnu-toolchain)

  [Understanding RISC-V software stack for software and hardware developer](https://riscv.org/wp-content/uploads/2015/02/riscv-software-stack-tutorial-hpca2015.pdf)

  Once done with installation add the PATH to .bashrc file for future use.

# Introduction to ABI

An Application Binary Interface is a set of rules enforced by the Operating System on a specific architecture. So, Linker converts relocatable machine code to absolute machine code via ABI interface specific to the architecture of machine.

So, it is system call interface used by the application program to access the registers specific to architecture. Overhere the architecture is RISC-V, so to access 32 registers of RISC-V below is the table which shows the calling convention (ABI name) given to registers for the application programmer to use.
[(Image source)](https://riscv.org/wp-content/uploads/2015/01/riscv-calling.pdf)

![calling_convention](Images/riscv-abi.png)

# Digital Logic with TL-Verilog and Makerchip

[Makerchip](https://makerchip.com/) is a free online environment for developing high-quality integrated circuits. You can code, compile, simulate, and debug Verilog designs, all from your browser. Your code, block diagrams, and waveforms are tightly integrated.

All the examples shown below are done on Makerchip IDE using TL-verilog. Also there are other tutorials present on IDE which can be found [here](https://makerchip.com/sandbox/) under Tutorials section.

## [Combinational logic](DAY_3_code/combinational_logic_calc.tlv)

Starting with basic example in combinational logic is an inverter. To write the logic of inverter using TL-verilog is `$out = ! $in;`. There is no need to declare `$out` and `$in` unlike Verilog. There is also no need to assign `$in`. Random stimulus is provided, and a warning is produced.

Below is snapshot of Combinational Calculator.

![Combinational-Calculator](Images/DAY_3_imgs/Combinaitonal_calc.png)

## [Sequential logic](DAY_3_code/sequential_logic.tlv)

Starting with basic example in sequential logic is Fibonacci Series with reset. To write the logic of Series using TL-Verilog is `$num[31:0] = $reset ? 1 : (>>1$num + >>2$num)`. This operator `>>?` is ahead of operator which will provide the value of that signal 1 cycle before and 2 cycle before respectively.

Below is snapshot of Sequential Calculator which remembers the last result, and uses it for the next calculation.

![Sequential-Calculator](Images/DAY_3_imgs/sequential_clac.png)

## [Pipelined logic](DAY_3_code/pipelined_calc_with_single_value_mem.tlv)

Timing abstract powerful feature of TL-Verilog which converts a code into pipeline stages easily. Whole code under `|pipe` scope with stages defined as `@?`

Below is snapshot of 2-cycle calculator which clears the output alternatively and output of given inputs are observed at the next cycle. Code for [Pipelined-Pythagoras](DAY_3_code/pipelined_pythagoras_circuit.tlv)

![Pipelined-Pythagoras](Images/DAY_3_imgs/pipelined_pythagoras_circuit.png)

![Cycle-Calculator](Images/DAY_3_imgs/pipelined_calc_with_single_value_mem.png)

## [Validity](DAY_3_code/pipelined_calc_with_validity.tlv)

Validity is TL-verilog means signal indicates validity of transaction and described as "when" scope else it will work as don't care. Denoted as `?$valid`. Validity provides easier debug, cleaner design, better error checking, automated clock gating.

Below is snapshot of 2-cycle calculator with validity.

![Cycle-Calculator-Validity](Images/DAY_3_imgs/pipelined_calc_with_validity.png)

# Basic RISC-V CPU micro-architecture

Designing the basic processor of 3 stages fetch, decode and execute based on RISC-V ISA.

![RV32i-Micro_Architecture](Images/RISCV_Block_Diagram.png)

## Fetch

- Program Counter (PC): Holds the address of next Instruction
- Instruction Memory (IM): Holds the set of instructions to be executed

During Fetch Stage, processor fetches the instruction from the IM pointed by address given by PC.

Below is snapshot from Makerchip IDE after performing the Fetch Stage.

![Fetch](Images/DAY_4-5/Load.png)

## Decode

6 types of Instructions:

- R-type - Register
- I-type - Immediate
- S-type - Store
- B-type - Branch (Conditional Jump)
- U-type - Upper Immediate
- J-type - Jump (Unconditional Jump)

Instruction Format includes Opcode, immediate value, source address, destination address. During Decode Stage, processor decodes the instruction based on instruction format and type of instruction.

Below is snapshot from Makerchip IDE after performing the Decode Stage.

![Decode](Images/DAY_4-5/Decode.png)

## Register File Read and Write

Here the Register file is 2 read, 1 write means 2 read and 1 write operation can happen simultanously.

Inputs:

- Read_Enable - Enable signal to perform read operation
- Read_Address1 - Address1 from where data has to be read
- Read_Address2 - Address2 from where data has to be read
- Write_Enable - Enable signal to perform write operation
- Write_Address - Address where data has to be written
- Write_Data - Data to be written at Write_Address

Outputs:

- Read_Data1 - Data from Read_Address1
- Read_Data2 - Data from Read_Address2

Below is snapshot from Makerchip IDE after performing the Register File Read followed by Register File Write.

![Register-File-Read](Images/DAY_4-5/Register_file_read.png)

![Register-File-Write](Images/DAY_4-5/Register_file_write.png)

## Execute

During the Execute Stage, both the operands perform the operation based on Opcode.

Below is snapshot from Makerchip IDE after performing the Execute Stage.

![Execute](Images/DAY_4-5/ALU.png)

## Control Logic

During Decode Stage, branch target address is calculated and fed into PC mux. Before Execute Stage, once the operands are ready branch condition is checked.

Below is snapshot from Makerchip IDE after including the control logic for branch instructions.

![Control-logic](Images/DAY_4-5/Control_Logic.png)

# Pipelined RISC-V CPU

Converting non-piepleined CPU to pipelined CPU using timing abstract feature of TL-Verilog. This allows easy retiming wihtout any risk of funcational bugs. More details reagrding Timing Abstract in TL-Verilog can be found in IEEE Paper ["Timing-Abstract Circuit Design in Transaction-Level Verilog" by Steven Hoover.](https://ieeexplore.ieee.org/document/8119264)

## Pipelining the CPU

Pipelining the CPU with branches still having 3 cycle delay rest all instructions are pipelined. Pipelining the CPU in TL-Verilog can be done in following manner:

```
|<pipe-name>
    @<pipe stage>
       Instructions present in this stage

    @<pipe_stage>
       Instructions present in this stage

```

Below is snapshot of pipelined CPU with a test case of assembly program which does summation from 1 to 9 then stores to r10 of register file. In snapshot `r10 = 45`. Test case:

```
*passed = |cpu/xreg[10]>>5$value == (1+2+3+4+5+6+7+8+9);

```

![Pipelining_CPU](Images/DAY_4-5/riscv_pipelined_diagram.png)
![Pipelining_CPU](Images/DAY_4-5/Pipelining_CPU.png)

## Load and store instructions and memory

Similar to branch, load will also have 3 cycle delay. So, added a Data Memory 1 write/read memory.

Inputs:

- Read_Enable - Enable signal to perform read operation
- Write_Enable - Enable signal to perform write operation
- Address - Address specified whether to read/write from
- Write_Data - Data to be written on Address (Store Instruction)

Output:

- Read_Data - Data to be read from Address (Load Instruction)

Added test case to check fucntionality of load/store. Stored the summation of 1 to 9 on address 4 of Data Memory and loaded that value from Data Memory to r17.

```
*passed = |cpu/xreg[17]>>5$value == (1+2+3+4+5+6+7+8+9);
```

Below is snapshot from Makerchip IDE after including load/store instructions.

![Load_Store](Images/DAY_4-5/Load.png)

## [Completing the RISC-V CPU](DAY_4-5_code/cpu.tlv)

Added Jumps and completed Instruction Decode and ALU for all instruction present in RV32I base integer instruction set.

Below is final Snapshot of Complete Pipelined RISC-V CPU.

![Final](Images/DAY_4-5/cpu_final.png)
![Final](Images/DAY_4-5/cpu_1.png)
![Final](Images/DAY_4-5/cpu_2.png)
![Final](Images/DAY_4-5/cpu_3.png)

# Acknowledgements

- [Kunal Ghosh](https://github.com/kunalg123), Co-founder, VSD Corp. Pvt. Ltd.
- [Steve Hoover](https://github.com/stevehoover), Founder, Redwood EDA
- [Shivani Shah](https://github.com/shivanishah269)
- [Akil M](https://github.com/akilm/MYTH-RV32I-core-akilm)
