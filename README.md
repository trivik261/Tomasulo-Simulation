# Tomasulo Simulation

A cycle-by-cycle model of dynamic scheduling with reservation stations, register renaming, operand capture, and a single common data bus.

## Run
```bash
python simulate.py Instruction1.txt --output trace.json
python -m unittest discover -s tests -v
```
Python 3.10+; no packages or Verilog tools required for the standalone entry point. Initial registers contain their indices; unmapped memory reads return zero. Instructions support ADD, SUB, MUL, FADD, FMUL, bitwise operations, shifts, LDR, and STR. Programs use `OP destination source source`; memory addresses use `offset+Rbase` or `Rbase+offset`.

## Scheduling model
One instruction issues per cycle. Separate add/multiply/logic/memory functional units execute when operands are ready. Stations retain results until one result can broadcast per cycle. Dependencies consume captured values or producer tags, protecting RAW, WAR, and WAW cases. Memory operations serialize in program order. Python numeric arithmetic is used; this is an educational scheduling model, not a bit-accurate processor or IEEE-754 hardware model.

## Original implementation
`tomo.py` is preserved as the original coursework. It invokes Verilog backends (`rda`, `fpa`, `fpm`, `alu`, `wallace`) that are absent from this repository and is not the portable run path. `simulate.py` reconstructs the scheduling behavior without those missing external modules. Tests cover dependent arithmetic, independent execution, register hazards, store/load ordering, and malformed programs.
