from toffee import *
from .bundle import *
from utils.cmd_code import *
from utils.common import *
import queue
import logging


class SimpleBusMasterAgent(Agent):
    def __init__(self, bundle: SimpleBusBundle):
        super().__init__(bundle.step)
        self.bundle:SimpleBusBundle = bundle

    async def send_req(self, addr, size, cmd, user=0, wmask=0, wdata=0):
        await AllValid(self.bundle.req.ready, delay=0)
        self.bundle.req.assign({
            "valid": 1,   "addr": addr,   "size": size,  "cmd": cmd,
            "user": user, "wmask": wmask, "wdata": wdata
        })
        await self.bundle.step()
        self.bundle.req.valid.value = 0

    async def get_resp(self, size: int = 0):
        """
        获取 burst 响应（共 size+1 拍）
        """
        num_beats = size + 1
        results = []

        self.bundle.rsp.ready.value = 1

        logging.debug(f"[AGENT] get_resp() called with size={size}")
        while len(results) < num_beats:
            await self.bundle.step()  # 等效于等待一个周期

            if self.bundle.rsp.valid.value:
                resp = self.bundle.rsp.as_dict()
                logging.debug(f"[AGENT] Got response beat: {resp}")
                results.append(resp)

        self.bundle.rsp.ready.value = 0
        logging.debug(f"[AGENT] Completed burst response of {num_beats} beats.")
        return results

    @driver_method()
    async def read(self, addr, size, user=0):
        logging.debug(f"[AGENT] read() called with addr={hex(addr)}, size={size}, user={user}")
        await self.send_req(addr, size, CMD_READ, user)
        return {"user": user}

    @driver_method()
    async def write(self, addr, data_list, size = 0, user=0, wmask=0xFF):
        """
        执行一个 burst write 操作。
        参数：
            addr: 起始地址（64-bit 对齐）
            data_list: burst 数据，每个元素是一个 64-bit 数据
            user: 用户 ID
        """
        size = len(data_list) - 1  # size 表示有 size+1 个 beat

        for i, data in enumerate(data_list):
            # 选择正确的 cmd 类型
            if len(data_list) == 1:
                cmd = CMD_WRITE
            elif i == len(data_list) - 1:
                cmd = CMD_WRITELST
            else:
                cmd = CMD_WRITEBST

            logging.debug(f"[AGENT] write beat {i}/{size}: addr=0x{addr + 8*i:x}, data=0x{data:x}, user=0x{user:x}, cmd=0x{cmd:x}")

            self.bundle.req.valid.value = 1
            self.bundle.req.addr.value = addr + 8 * i
            self.bundle.req.wdata.value = data
            self.bundle.req.cmd.value = cmd
            self.bundle.req.size.value = size
            self.bundle.req.user.value = user
            self.bundle.req.wmask.value = wmask

            await AllValid(self.bundle.req.ready)
            await self.bundle.step()  # 等一拍进行握手
            # self.bundle.req.valid.value = 0  # 拉低 valid，防止 back-to-back 出错
            # await self.bundle.step()  # 多等一拍确保 handshake 完成

        logging.debug(f"[AGENT] write burst of {size + 1} beats completed")
        return {"user": user}
    
    @driver_method()
    async def write_one_word(self, addr, data, user=0, cmd=CMD_WRITE, size=0, wmask=0xFF):
        """
        发出一个单拍写请求。

        参数：
            addr: 写入地址（对齐）
            data: 写入数据（int）
            user: 用户ID
            cmd: 写命令（支持 CMD_WRITE / CMD_WRITEBST / CMD_WRITELST）
            size: 写 burst size，单写一般设为0
            wmask: 写掩码，默认写全字节
        """
        self.bundle.req.valid.value = 1
        self.bundle.req.addr.value = addr
        self.bundle.req.wdata.value = data
        self.bundle.req.cmd.value = cmd
        self.bundle.req.size.value = size
        self.bundle.req.user.value = user
        self.bundle.req.wmask.value = wmask

        await AllValid(self.bundle.req.ready)
        await self.bundle.step()

        self.bundle.req.valid.value = 0

    # @driver_method()
    async def write_burst(self, addr, data_list, user=0):
        """
        执行 burst 写操作，最后一个 beat 使用 CMD_WRITELST。

        参数：
            addr: 起始地址（64-bit 对齐）
            data_list: burst 数据列表
            user: 用户 ID
        """
        size = len(data_list) - 1

        for i, data in enumerate(data_list):
            # 判断当前是否为最后一个 beat
            if i == size:
                cmd = CMD_WRITELST
            else:
                cmd = CMD_WRITEBST

            await self.write_one_word(
                addr=addr + 8 * i,
                data=data,
                user=user,
                cmd=cmd,
                size=size,
                wmask=0xFF  # 按需调整
            )

    @monitor_method()
    async def get_read_response(self):
        """单周期监测：当valid和ready同时有效时捕获数据"""
        # 检查握手信号
        if self.bundle.rsp.valid.value and self.bundle.rsp.ready.value:
            # 捕获数据
            rdata = int(self.bundle.rsp.rdata.value)
            user = int(self.bundle.rsp.user.value)
            
            # 调试日志
            logging.debug(f"Captured read beat: rdata={hex(rdata)}, user={user}")
            
            # 返回监测到的单拍数据
            return {"rdata": rdata, "user": user}
        
        # 未满足条件时返回None（框架自动忽略）
        return None

        


class SimpleBusSlaveAgent(Agent):
    def __init__(self, bundle: SimpleBusBundle):
        super().__init__(bundle.step)
        self.bundle: SimpleBusBundle = bundle

    @driver_method()
    async def read_resp(self, size, rdata: list, user=0):
        assert len(rdata) == 1 << size
        await AllValid(self.bundle.rsp.ready, delay=0)
        self.bundle.rsp.valid.value = 1
        for i in range(1 << size):
            self.bundle.rsp.cmd.value = CMD_READLST if (i == ((1 << size) - 1)) else CMD_READ
            self.bundle.rsp.rdata.value = rdata[i]
            await self.bundle.step()
        self.bundle.rsp.valid.value = 0

    @driver_method()
    async def write_resp(self, user=0):
        await AllValid(self.bundle.rsp.ready, delay=0)
        self.bundle.rsp.assign({"valid": 1, "cmd": CMD_WRITERSP, "user": user})
        await self.bundle.step()
        self.bundle.rsp.valid.value = 0

    @driver_method()
    async def get_req(self):
        self.bundle.req.ready.value = 1
        await AllValid(self.bundle.req.valid)
        req = self.bundle.req.as_dict()
        self.bundle.req.ready.value = 0
        return req
