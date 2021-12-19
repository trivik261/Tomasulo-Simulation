#Tomasulo Algorithm - Python3

3 Reservation Stations for Add (Add, Fadd, Sub, FSub)
2 Reservation Stations for Mul (Mul, Fmul)
2 Reservation Station for LogicShift (Cmp, Xor, Nand, LSL, LSR)
3 for Load and Store Buffer Each

16 registers (R0 to R15)

Time to execute:
ADD/SUB -> 14 cc
MUL -> 34 cc
FADD/FSUB -> 12 cc
FMUL -> 36 cc
Logic -> 1 cc (NAND, XOR, CMP)
Shift -> 4 cc (LSL, LSR)
STR -> 2 cc
LDR -> 2 cc

Run python3 TomasuloAlgorithm.py

enter 1 or 2 as input (choosing the test cases instr file)
