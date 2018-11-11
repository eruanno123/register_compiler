[![Build Status](https://travis-ci.org/eruanno123/register_compiler.svg?branch=master)](https://travis-ci.org/eruanno123/register_compiler)

Register Compiler
=================

This project is my attempt to create open source, automated code generation tool based on standarized [SystemRDL specification](http://www.accellera.org/downloads/standards/systemrdl).

Planned features for now:

- generate SystemVerilog register backend
- generate register access interface (APB, AXI4-Lite, Avalon-MM, ...)
- generate UVM-SystemC register model for design verification purposes.

The project depends on systemrdl-compiler project.

Similar projects
----------------

- [systemrdl-compiler](https://pypi.org/project/systemrdl-compiler/) - engine used by Register Compiler.

- [ORDT](https://github.com/Juniper/open-register-design-tool/wiki/Running-Ordt) from Juniper - Java based register design tool
