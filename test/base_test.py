import toffee_test
from Cache import DUTCache
from env.ntcache_env import *
from env.simpleram import *

import random

@toffee_test.fixture
async def start_func(toffee_request: toffee_test.ToffeeRequest):
    setup_logging(DEBUG)
    dut = toffee_request.create_dut(DUTCache, "clock")
    env = NtCacheEnv(dut)

    async def start_code():
        dut.reset.AsImmWrite()
        dut.reset.value = 1
        dut.reset.AsRiseWrite()
        start_clock(dut)

        await ClockCycles(dut, 100)
        dut.reset.value = 0
        dut.io_flush.value = 0

        # 初始化内存数据
        init_data = {}
        for addr in range(0x00000000, 0x00001000, 8):
            init_data[addr] = random.getrandbits(64)

        ram_main = SimpleBusRam(env.mem_agent)
        ram_mmio = SimpleBusRam(env.mmio_agent)
        refmodel = CacheRefModel(init_data=init_data)
        env.attach(refmodel)

        # 同时初始化
        ram_main.init_memory(init_data)
        #refmodel.gold_mem.init_memory(init_data)
        await ClockCycles(dut, 5)

        async with Executor(exit="none") as exec:
            exec(env.usertop.req_handler(), sche_group="req_handler")
            exec(env.usertop.rsp_handler(), sche_group="rsp_handler")
            exec(ram_main.work(), sche_group="mem")
            exec(ram_mmio.work(), sche_group="mmio")
        return env

    return start_code
