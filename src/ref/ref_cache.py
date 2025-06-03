"""
    A simple reference cache model
    Author: zzy
"""
from env.simplebus_agents import *
from utils import *
import logging
import random
from .CDTable import *


class CacheRefModel(Model):
    def __init__(self, init_data=None, num_sets=128, num_ways=4, block_size_bytes=64, address_bits=32):
        super().__init__()
        self.gold_mem = SimpleMem()
        self.cd_table = CDTable(num_sets, num_ways, block_size_bytes, address_bits)

        # 初始化内存内容
        if init_data is not None:
            self.gold_mem.init_memory(init_data)
        # if init_data is not None:
        #     log_message = "CacheRefModel initialized with init_data:"
        #     for key, value in init_data.items():
        #         log_message += f"\n  {hex(key)}: {hex(value)}"
        #     logging.debug(log_message)
        # else:
        #     logging.debug("CacheRefModel initialized without init_data.")

        # 用于暂存预期的CPU响应，以便monitor_hook可以访问
        self._expected_read_rsp_queue = []
        self._expecting_cpu_response = False

        # 用于记录预期的写回，以便与memory_agent的monitor比较
        self._pending_expected_write_backs = {}  # addr -> data_block

    def reset(self):
        self.gold_mem.reset()
        self.cd_table.reset()
        self._expected_read_rsp_queue.clear()
        self._expecting_cpu_response = False
        self._pending_expected_write_backs.clear()
        self.mem = None

    def _read_single_word(self, addr: int, user: int):
        """处理单个地址的读取请求"""
        # 地址解码
        tag, set_idx, block_addr, byte_offset_in_block = self.cd_table._decode_address(addr)

        # 在 cache 中查找
        is_hit, way_idx, _, _, _, _ = self.cd_table.find_line_with_all_details(addr)
        logging.debug(f"is_hit: {is_hit}, way_idx: {way_idx}")

        if is_hit:
            # ✅ Cache hit：直接从 cache 中读取 word
            read_data = self.cd_table.read_from_cache_line(addr)
            logging.debug(f"read_data: {hex(read_data)}")
        else:
            # ❌ Cache miss：
            # 1️⃣ 选择 victim 行
            # 2️⃣ 如果 dirty，需要写回
            # 3️⃣ 从主存读取 block 并写入新行
            victim_set_idx, victim_way_idx, evicted_info = self.cd_table.allocate_line(addr, [0] * 8)
            logging.debug(f"victim_set_idx: {victim_set_idx}, victim_way_idx: {victim_way_idx}, evicted_info: {evicted_info}")

            if evicted_info is not None:
                # 写回 dirty 行（此处暂不处理 mem 比对，只记录）
                self._pending_expected_write_backs[evicted_info['addr']] = evicted_info['data_block']
                self.gold_mem.write_block(
                    evicted_info['addr'],
                    evicted_info['data_block'],
                    self.cd_table.block_size_bytes)

            # 从 gold_mem 加载 block
            block_addr = addr & ~(self.cd_table.block_size_bytes - 1)
            data_block = self.gold_mem.read_block(
                block_addr, self.cd_table.block_size_bytes)
            logging.debug(f"block_addr: {block_addr}, cd_table.block_size_bytes: {self.cd_table.block_size_bytes}")
            logging.debug(f"data_block: {data_block}")

            # 写入新 cache 行（会更新 tag/valid）
            self.cd_table.table[victim_set_idx][victim_way_idx].data_block = data_block
            self.cd_table.table[victim_set_idx][victim_way_idx].tag = tag
            self.cd_table.table[victim_set_idx][victim_way_idx].valid = True
            self.cd_table.table[victim_set_idx][victim_way_idx].dirty = False

            # 命中后再次读取
            read_data = self.cd_table.read_from_cache_line(addr)
            logging.debug(f"read_data: {hex(read_data)}")

        # 将预期响应加入队列
        self._expected_read_rsp_queue.append({
            "rdata": read_data,
            "user": user
        })
        self._expecting_cpu_response = True
        logging.debug(f"添加预期响应到队列: rdata={hex(read_data)}, user={user}")

    @driver_hook(agent_name="in_agent", driver_name="read")
    def read(self, addr, size, user=0):
        """
        处理burst读取请求
        addr: 起始地址（按8字节对齐）
        size: 0 表示只读1个word，1表示读2个word（AXI风格）
        user: 唯一标识符，匹配 response
        """
        for i in range(size + 1):  # size=0 表示读一个 word
            burst_addr = addr + i * 8
            self._read_single_word(burst_addr, user)

    @monitor_hook(agent_name="in_agent", monitor_name="get_read_response")
    def check_read_response(self, rsp):
        logging.debug("check_read_response 被调用")

        if rsp is None:
            logging.debug("响应为空，跳过检查")
            return

        if not self._expected_read_rsp_queue:
            logging.warning("收到响应但队列中没有期望！")
            return

        expected = self._expected_read_rsp_queue.pop(0)

        logging.debug(f"开始比较响应 - 预期数据: {hex(expected['rdata'])}, 实际数据: {hex(rsp['rdata'])}")
        logging.debug(f"开始比较用户ID - 预期: {expected['user']}, 实际: {rsp['user']}")

        assert rsp["rdata"] == expected["rdata"], \
            f"[READ RESP DATA MISMATCH] Expected: {hex(expected['rdata'])}, Got: {hex(rsp['rdata'])}"

        assert rsp["user"] == expected["user"], \
            f"[READ RESP USER MISMATCH] Expected: {expected['user']}, Got: {rsp['user']}"

        if not self._expected_read_rsp_queue:
            self._expecting_cpu_response = False


    def _write_single_beat(self, addr: int, data_word: int, byte_mask: int, user: int):
        """
        处理单个写操作（可能是突发传输中的一个节拍）的参考模型。
        实现写回、写分配策略。
        addr: 64位对齐的写入地址。
        data_word: 要写入的64位数据字。
        byte_mask: 8位掩码，每一位对应data_word中的一个字节。
                   1表示写入该字节，0表示保持原值。（例如，0xFF表示写入整个字）
        user: 用户ID（用于日志记录，不直接用于状态更改）。
        """
        tag, set_idx, block_addr, byte_offset_in_block = self.cd_table._decode_address(addr)
        logging.debug(f"参考模型写节拍: addr=0x{addr:08x}, data=0x{data_word:016x}, mask=0b{byte_mask:08b}, user=0x{user:x}")

        is_hit, way_idx, _, _, _, _ = self.cd_table.find_line_with_all_details(addr)

        if is_hit:
            # 缓存命中
            logging.debug(f"参考模型写: 地址0x{addr:08x}缓存命中")
            # 将数据写入现有缓存行
            # cd_table.write_to_cache_line将更新data_block并设置dirty=True
            write_success = self.cd_table.write_to_cache_line(addr, data_word, byte_mask)
            if not write_success:
                # 如果find_line_with_all_details报告命中，这种情况不应该发生
                logging.error(f"参考模型写: 严重错误 - 在报告命中的情况下写入缓存行失败，地址0x{addr:08x}")
        else:
            # 缓存未命中（写分配策略）
            logging.debug(f"参考模型写: 地址0x{addr:08x}缓存未命中。执行写分配。")

            # 1. 从主内存(gold_mem)获取包含目标地址的数据块
            # 这个数据块将被加载到缓存中
            logging.debug(f"参考模型写: 从gold_mem获取地址0x{block_addr:08x}的数据块。")
            block_data_from_memory = self.gold_mem.read_block(block_addr, self.cd_table.block_size_bytes)

            # 2. 在缓存中为这个新数据块分配一行
            # 这可能会驱逐现有行。如果被驱逐的行是脏的，其数据必须写回
            # allocate_line将block_data_from_memory放入选定的行，设置其标签和有效位，
            # 并初始标记为非脏(dirty=False)
            _allocated_set_idx, _allocated_way_idx, evicted_info = self.cd_table.allocate_line(addr, block_data_from_memory)
            logging.debug(f"参考模型写: 为地址0x{addr:08x}在组{_allocated_set_idx}、路{_allocated_way_idx}分配了行。")

            if evicted_info:
                # 选择了一个有效的脏行作为牺牲者。将其内容写回gold_mem
                logging.debug(f"参考模型写: 驱逐了脏牺牲行(标签: {evicted_info['tag']}, 地址: 0x{evicted_info['addr']:08x})。写回gold_mem。")
                self.gold_mem.write_block(
                    evicted_info['addr'],               # 牺牲者的块对齐地址
                    evicted_info['data_block'],         # 牺牲者的数据块
                    self.cd_table.block_size_bytes
                )

            # 3. 现在数据块（包含来自内存的原始数据）已在缓存中，
            # 对新加载和分配的行执行请求的写操作
            # cd_table.write_to_cache_line将找到该行（现在是命中），
            # 使用data_word和byte_mask修改块中的相关字，
            # 并将该行标记为脏(dirty=True)
            logging.debug(f"参考模型写: 将请求的数据写入新分配的行，地址0x{addr:08x}。")
            write_success = self.cd_table.write_to_cache_line(addr, data_word, byte_mask)
            if not write_success:
                # 这表明有问题，因为该行应该已经可用并命中
                logging.error(f"参考模型写: 严重错误 - 写入新分配的缓存行失败，地址0x{addr:08x}")

    @driver_hook(agent_name="in_agent", driver_name="write")
    def write(self, addr: int, data_list: list, user: int = 0, wmask: int = 0xFF):
        """
        Driver hook for write operations initiated by the in_agent.
        Handles single word writes and burst writes.

        addr: Starting address of the write.
        data_list: A list of 64-bit integer data words to be written.
                   For a single word write, this list will contain one element.
        user: User ID for the transaction.
        wmask: 8-bit byte mask for the write operation (e.g., 0xFF for all bytes of a word).
               This mask is applied to each data word in data_list.
        """
        num_beats = len(data_list)
        logging.debug(f"RefModel Write Hook: addr=0x{addr:08x}, num_beats={num_beats}, user=0x{user:x}, wmask=0b{wmask:08b}")

        if num_beats == 0:
            logging.warning("RefModel Write Hook: Received write request with empty data_list.")
            return

        for i in range(num_beats):
            current_addr = addr + (i * 8)  # Assuming 8 bytes per data word (64-bit words)
            data_for_this_beat = data_list[i]
            # The wmask from the agent.write call is typically for the entire word.
            # Our _write_single_beat expects this 8-bit byte_mask directly.
            self._write_single_beat(current_addr, data_for_this_beat, wmask, user)


class SimpleMem:
    def __init__(self, lbound=0x00000000, rbound=0xffffffff, default_value=0):
        self.mem = {}
        self.lbound = lbound
        self.rbound = rbound
        self.default_value = default_value

        
    def init_memory(self, init_data: dict):
        """
        用于初始化内存。
        参数：
            init_data (dict): 形如 {addr0: data0, addr1: data1, ...}
        """
        for addr, data in init_data.items():
            self.mem[addr] = data

    def reset(self):
        self.mem.clear()

    def _check_bounds(self, addr):
        if not (self.lbound <= addr <= self.rbound):
            raise ValueError(
                f"[Memory-SIM]: Address 0x{addr:08x} is out of bounds.")

    def read_block(self, block_addr, block_size_bytes):
        """读取整个数据块 (例如 64 字节)"""
        self._check_bounds(block_addr)
        if block_addr % block_size_bytes != 0:
            raise ValueError(
                f"Block address 0x{block_addr:08x} is not aligned to block size {block_size_bytes}.")

        data_block = []
        # 假设我们按64位字(8字节)存储，一个64B的块包含8个64位字
        num_words_in_block = block_size_bytes // 8
        for i in range(num_words_in_block):
            word_addr = block_addr + i * 8
            data_block.append(self.mem.get(word_addr, self.default_value))
        return data_block  # 返回一个包含多个64位字的列表

    def write_block(self, block_addr, data_block_words, block_size_bytes):
        """写入整个数据块"""
        self._check_bounds(block_addr)
        if block_addr % block_size_bytes != 0:
            raise ValueError(
                f"Block address 0x{block_addr:08x} is not aligned to block size {block_size_bytes}.")

        num_words_in_block = block_size_bytes // 8
        if len(data_block_words) != num_words_in_block:
            raise ValueError(
                f"Data block size mismatch. Expected {num_words_in_block} words, got {len(data_block_words)}.")

        for i in range(num_words_in_block):
            word_addr = block_addr + i * 8
            self.mem[word_addr] = data_block_words[i]

    # 为CPU请求的字节/字/半字级别读写保留原来的word64方法，
    # 但SimpleMem主要与Cache交互的是块级别
    def read_word64(self, word_addr):
        if word_addr % 8 != 0:
            raise ValueError(
                f"Address 0x{word_addr:08x} is not 64-bit aligned for word read.")
        self._check_bounds(word_addr)
        return self.mem.get(word_addr, self.default_value)

    def write_word64(self, word_addr, data64, byte_mask_8bit=0xFF):
        if word_addr % 8 != 0:
            raise ValueError(
                f"Address 0x{word_addr:08x} is not 64-bit aligned for word write.")
        self._check_bounds(word_addr)
        current_mem_data = self.mem.get(word_addr, self.default_value)
        final_data = 0
        for i in range(8):
            if (byte_mask_8bit >> i) & 0b1:
                byte_to_write = (data64 >> (i * 8)) & 0xFF
            else:
                byte_to_write = (current_mem_data >> (i * 8)) & 0xFF
            final_data |= (byte_to_write << (i * 8))
        self.mem[word_addr] = final_data
