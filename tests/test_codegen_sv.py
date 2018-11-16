

import pytest
from pyrcom.codegen import systemverilog as sv


def test_rangeSpecifier():
    range = sv.RangeSpecifier()
    assert range.start_idx == 0 and range.end_idx == 0

    range = sv.RangeSpecifier(31, 0)
    assert range.start_idx == 31 and range.end_idx == 0

    # string conversion test
    assert str(sv.RangeSpecifier(15, 0)) == "15:0"
    assert str(sv.RangeSpecifier(14, 9)) == "14:9"
    assert str(sv.RangeSpecifier(-1, 0)) == "-1:0"
    assert str(sv.RangeSpecifier(7, 7)) == "7"
    assert str(sv.RangeSpecifier(0, 0)) == "0"


def test_signalDeclaration():
    for kind in ["logic", "reg", "wire"]:
        spec1 = sv.SignalDeclaration("test", kind, sv.RangeSpecifier(31, 0))
        spec2 = sv.SignalDeclaration("test", kind, None)
        assert spec1.kind == kind and spec1.name == "test" and str(
            spec1.range) == "31:0"
        assert spec2.kind == kind and spec2.name == "test" and spec2.range == None

        assert str(spec1) == ("%s [31:0] test;" % kind)
        assert str(spec2) == ("%s test;" % kind)

    with pytest.raises(sv.SVGeneratorError, match="Unknown declaration type '(.*)'. Expected values: '(.*)'"):
        sv.SignalDeclaration("test", "no_such_kind", None)
