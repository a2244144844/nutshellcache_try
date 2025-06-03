"""
    Wrap up some user functions for read/write here
    Author: yzcc
"""

import queue
import logging

from toffee import ClockCycles

from utils.cmd_code import *
from utils.common import *
from .simplebus_agents import SimpleBusMasterAgent

class UserTop:
    def __init__(self, agent:SimpleBusMasterAgent, dut):
        self.agent = agent
        self.dut = dut
        self.user_to_size = {}

        self.pending_read_sizes = {}
        self.req_que = queue.Queue()
        self.rsp_que = queue.Queue()

    async def req_handler(self):
        while True:
            if self.req_que.empty():
                await ClockCycles(self.dut, 1)
            else:
                logging.debug("self.req_que is not empty")
                req: ReqMsg = self.req_que.get()

                if req.cmd == CMD_READ:
                    logging.debug("req.cmd == CMD_READ")
                    await self.agent.read(req.addr, req.size, req.user)

                elif req.cmd == CMD_WRITE:
                    logging.debug("req.cmd == CMD_WRITE (single write)")
                    await self.agent.write(addr=req.addr, data_list=req.data_list, user=req.user)  # 包成 list 方便复用

                # elif req.cmd == CMD_WRITEBST:
                #     logging.debug("req.cmd == CMD_WRITEBST (burst write)")
                #     await self.agent.write(req.addr, req.data_list, req.user)

                # elif req.cmd == CMD_WRITELST:
                #     logging.debug("req.cmd == CMD_WRITELST (last beat of burst write)")
                #     # 如果你打算拆开每一拍的写，也可以在此处理"最后一拍"的 write
                #     await self.agent.write(req.addr, [req.data], req.user)

                else:
                    logging.warning(f"Unknown req.cmd {req.cmd}")

    async def rsp_handler(self):
        while True:
            # ⚠️ 默认先收一个响应，拿到 user_id
            first_resp = await self.agent.get_resp(size=0)
            if not first_resp:
                continue  # skip if somehow empty

            user = first_resp[0]["user"]
            logging.debug(f"[RSP_HANDLER] trying to get size for user={user}, all pending: {self.pending_read_sizes}")
            size = self.pending_read_sizes.get(user, 0)  # 默认为 0 拍

            # ✅ 如果 size > 0，再继续收剩余 beat
            remaining = size
            resp_list = first_resp

            if size > 0:
                resp_list += await self.agent.get_resp(size=remaining)

            logging.debug(f"[RSP_HANDLER] Received burst of {len(resp_list)} beats for user={user}")

            # ✅ 推入队列
            for res in resp_list:
                rsp = RespMsg(rdata=res["rdata"], user=res["user"], cmd=res.get("cmd", 0))
                self.rsp_que.put_nowait(rsp)

            # ✅ 清除 user 的记录
            self.pending_read_sizes.pop(user, None)

    async def non_block_read(self, addr, size = 0, user = 0):
        # size = 0
        result = ReqMsg(addr, CMD_READ, size = size, user = user) #所有的cmd都是CMD_READ
        logging.debug("Request details: %s", result.loggable())
        
        # ✅ 记录该 user 的 burst 长度
        self.pending_read_sizes[user] = size
        
        self.req_que.put_nowait(result)
        logging.debug("non_block_read finished")

    async def non_block_write(self, addr, data_list, user=0, size = 0):
        """
        向请求队列发送一个 write 请求（非阻塞，立即返回）。

        参数：
            addr: 写起始地址
            data_list: 一个 burst 数据列表
            user: user ID
        """
        result = ReqMsg(addr, CMD_WRITE, data_list=data_list, size=len(data_list) - 1, user=user)
        logging.debug("Write request details: %s", result.loggable())
        self.req_que.put_nowait(result)
        logging.debug("non_block_write finished")

    async def recv_burst(self, size):
        results = []
        for _ in range(size + 1):
            while self.rsp_que.empty():
                await ClockCycles(self.dut, 1)
            logging.debug("rsp_que is not empty")
            results.append(self.rsp_que.get())
        return results

    async def block_read(self, addr, size = 0, user = 0):
        await self.non_block_read(addr, size, user)
        
        num_beats = size + 1
        results = []
        logging.debug(f"num_beats: {num_beats}")
        
        while len(results) < num_beats:
            logging.debug(f"len(results): {len(results)}")
            while self.rsp_que.empty():
                # logging.debug("rsp_que is empty")
                await ClockCycles(self.dut, 1)
            res = self.rsp_que.get()
            results.append(res)

        logging.debug("recv finished")
        for i, r in enumerate(results):
            logging.debug(f"beat[{i}]: {r}")

        return results

    async def block_write(self, addr, data_list, user=0, size = 0):
        current_write_user_id = user
        await self.non_block_write(addr, data_list, user, size)
        # 如果写没有响应机制，则直接返回即可
        # 若需要 ACK（即 agent 需要 get_resp），可以在此添加等待逻辑
        logging.debug("block_write finished")
        found_ack = False
        # 临时存储非目标响应的消息
        messages_to_requeue = []

        while not found_ack:
            try:
                # 非阻塞方式获取响应消息
                response_msg: RespMsg = self.rsp_que.get_nowait()

                # 检查是否为目标写响应
                if response_msg.user == current_write_user_id and \
                   response_msg.cmd == CMD_WRITERSP:
                    logging.debug(f"[UserTop] block_write: 收到用户 0x{current_write_user_id:x} 的写响应")
                    found_ack = True
                else:
                    # 保存非目标响应以便后续重新入队
                    logging.debug(f"[UserTop] block_write: 用户 0x{current_write_user_id:x} 收到不匹配响应 (用户: 0x{response_msg.user:x}, 命令: 0x{response_msg.cmd:x})")
                    messages_to_requeue.append(response_msg)

            except queue.Empty:
                # 队列为空时等待一个时钟周期
                await ClockCycles(self.dut, 1)

        for msg_to_requeue in reversed(messages_to_requeue):
            self.rsp_que.put_nowait(msg_to_requeue)
        
        if not found_ack:
            logging.error(f"[UserTop] block_write: 未能收到用户 0x{current_write_user_id:x} 的 CMD_WRITERSP 响应")
            raise Exception(f"等待用户 0x{current_write_user_id:x} 的 CMD_WRITERSP 响应超时或出错")
        else:
            logging.debug(f"[UserTop] block_write: 用户 0x{current_write_user_id:x} 的写操作已完成并收到确认")
