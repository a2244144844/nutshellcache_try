"""
    Just Drive The Dut
    Author: yzcc
"""
import logging
from base_test import *
import asyncio

logging.basicConfig(level=logging.DEBUG)
logging.debug("Test debug message")

@toffee_test.testcase
async def test_smoke(start_func):
    env: NtCacheEnv = await start_func()

    await env.usertop.block_write(data_list = [0x8], addr = 0x100, user = random.randint(0, 65535), size = 0)   
    # await env.usertop.block_read(0x108, user = random.randint(0, 65535))

    #logging.debug("block_read finished")
    #await env.usertop.block_write(0x1, 0x1, 0x1)
    # for i in range(0x100, 0x1000 , 8):  # 循环从地址 0x1 到 0x100 (包含两端)
    #     await env.usertop.block_read(addr=i, user=random.randint(0, 65535))
    #await env.usertop.non_block_read(0x2)
    #res = await env.usertop.recv()
    #logging.debug("recv finished")
    #return res

