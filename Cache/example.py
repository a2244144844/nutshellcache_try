try:
    from UT_Cache import *
except:
    try:
        from Cache import *
    except:
        from __init__ import *


if __name__ == "__main__":
    dut = DUTCache()
    # dut.init_clock("clk")

    dut.Step(1)

    dut.Finish()
