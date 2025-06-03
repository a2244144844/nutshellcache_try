"""
    Boring packages
    Author: yzcc
"""

class ReqMsg:
    def __init__(self, addr, cmd, data=0, mask=0, user=0x123, size=7, data_list=None):
        self.user = user
        self.size = size
        self.addr = addr
        self.cmd = cmd
        self.mask = mask
        self.data = data
        self.data_list = data_list  # 新增字段，用于 burst write
    
    def display(self, displayer=print):
        displayer(f"[REQ MSG] user {self.user:x}, size {self.size}, addr 0x{self.addr:x} "
                  f"cmd 0x{self.cmd:x}, mask {self.mask:b}, data {self.data:x}")

    def set_from_dict(self, d):
        self.user = d['user']
        self.size = d['size']
        self.addr = d['addr']
        self.cmd = d['cmd']
        self.mask = d['mask']
        self.data = d['data']
        self.data_list = d.get('data_list', None)  # 安全地获取 data_list，默认 None

    def as_dict(self):
        req = {
            "valid": True,
            "bits_addr": self.addr,
            "bits_size": self.size,
            "bits_cmd": self.cmd,
            "bits_wmask": self.mask,
            "bits_wdata": self.data,
            "bits_user": self.user
        }
        return req

    def __str__(self):
        """为 logging 提供标准字符串输出，复用 display() 的逻辑"""
        from io import StringIO
        with StringIO() as buf:
            self.display(displayer=lambda s: buf.write(s + '\n'))
            return buf.getvalue().strip()

    def loggable(self):
        """专为 logging 优化的输出格式"""
        return (
            f"ReqMsg(user=0x{self.user:04x}, cmd=0x{self.cmd:x}, "
            f"addr=0x{self.addr:08x}, size={self.size}, "
            f"mask=0b{self.mask:08b}, data=0x{self.data:016x}, "
            f"data_list={[hex(d) for d in self.data_list] if self.data_list else None})"
        )

class RespMsg:
    def __init__(self, cmd, rdata, user):
        self.cmd = cmd
        self.rdata = rdata
        self.user = user

    def display(self):
        print(f"[RESP MSG] cmd 0x{self.cmd}, rdata 0x{self.rdata:x}")

    def set_from_dict(self, d):
        self.rdata = d['rdata']
        self.cmd = d['cmd']
        self.user = d['user']

    def as_dict(self):
        resp = {}
        resp["valid"] = True
        resp["bits_rdata"] = self.rdata
        resp["bits_cmd"] = self.cmd
        resp["bits_user"] = self.user

    def __str__(self):
        """标准字符串转换，自动被logging调用"""
        return self.loggable()

    def loggable(self):
        """专为logging优化的格式化输出"""
        cmd_str = {
            0: "READ_RESP",
            1: "WRITE_ACK",
            2: "ERROR"
        }.get(self.cmd, f"UNKNOWN_CMD({self.cmd})")

        return f"RespMsg(cmd={cmd_str}, rdata=0x{self.rdata:x}, user=0x{self.user:x})"

def replicate_bits(binary_num, replication, num_bits):
    result = 0
    for i in range(num_bits):
        bit = (binary_num >> i) & 1
        for j in range(replication):
            result = result | (bit << (i * replication + j))
    return result
