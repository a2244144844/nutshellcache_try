import random
import logging
from env.simplebus_agents import *
from utils import *

class CacheLineState:
    """辅助类，用于表示单个缓存行的状态。"""
    def __init__(self):
        self.valid = False
        self.dirty = False
        self.tag = None
        self.data_block = None # 存储64字节的数据块 (例如，一个包含8个64位整数的列表)

    def __str__(self):
        return f"V:{int(self.valid)} D:{int(self.dirty)} Tag:{self.tag if self.tag is not None else 'N/A'}"


class CDTable:
    def __init__(self, num_sets = 128, num_ways = 4, block_size_bytes = 64, address_bits=32):
        self.num_sets = 128
        self.num_ways = 4
        self.block_size_bytes = 64
        self.address_bits = address_bits

        self.byte_offset_bits = (self.block_size_bytes - 1).bit_length()
        self.set_index_bits = (self.num_sets - 1).bit_length()
        self.tag_shift = self.set_index_bits + self.byte_offset_bits
        self.set_index_mask = self.num_sets - 1
        self.block_addr_mask = ~ (self.block_size_bytes - 1)

        self.table = [[CacheLineState() for _ in range(self.num_ways)] for _ in range(self.num_sets)]

    def _decode_address(self, addr):
        block_addr = addr & self.block_addr_mask
        set_index = (addr >> self.byte_offset_bits) & self.set_index_mask
        tag = addr >> self.tag_shift
        byte_offset_in_block = addr & (self.block_size_bytes - 1)
        return tag, set_index, block_addr, byte_offset_in_block

    def find_line_with_all_details(self, addr):
        tag, set_index, block_addr, byte_offset_in_block = self._decode_address(addr)
        for way_idx, line_state in enumerate(self.table[set_index]):
            if line_state.valid and line_state.tag == tag:
                return True, way_idx, set_index, tag, block_addr, byte_offset_in_block
        return False, None, set_index, tag, block_addr, byte_offset_in_block

    def get_victim_way(self, set_index):
        invalid_ways = [idx for idx, line in enumerate(self.table[set_index]) if not line.valid]
        if invalid_ways:
            return random.choice(invalid_ways)
        return random.randrange(self.num_ways)

    def read_from_cache_line(self, addr):
        is_hit, way_idx, set_index, _, _, byte_offset_in_block = self.find_line_with_all_details(addr)
        if is_hit and way_idx is not None:
            line = self.table[set_index][way_idx]
            if line.data_block:
                word_index_in_block = byte_offset_in_block // 8
                return line.data_block[word_index_in_block]
        return None

    def write_to_cache_line(self, addr, data64_for_word, byte_mask_8bit):
        is_hit, way_idx, set_index, _, _, byte_offset_in_block = self.find_line_with_all_details(addr)
        if is_hit and way_idx is not None:
            line = self.table[set_index][way_idx]
            if line.data_block is None:
                line.data_block = [0] * (self.block_size_bytes // 8)

            word_index_in_block = byte_offset_in_block // 8
            current_word_data = line.data_block[word_index_in_block]

            modified_word = 0
            for i in range(8):
                if (byte_mask_8bit >> i) & 0b1:
                    byte_to_write = (data64_for_word >> (i * 8)) & 0xFF
                else:
                    byte_to_write = (current_word_data >> (i * 8)) & 0xFF
                modified_word |= (byte_to_write << (i * 8))

            line.data_block[word_index_in_block] = modified_word
            line.dirty = True
            return True
        return False

    def allocate_line(self, addr, data_block_from_mem):
        tag, set_index, block_addr, _ = self._decode_address(addr)
        victim_way_idx = self.get_victim_way(set_index)

        old_line_state = self.table[set_index][victim_way_idx]
        evicted_dirty_line_info = None
        if old_line_state.valid and old_line_state.dirty:
            evicted_block_addr = (old_line_state.tag << self.tag_shift) | (set_index << self.byte_offset_bits)
            evicted_dirty_line_info = {
                "addr": evicted_block_addr,
                "tag": old_line_state.tag,
                "data_block": old_line_state.data_block
            }

        new_line = self.table[set_index][victim_way_idx]
        new_line.valid = True
        new_line.dirty = False
        new_line.tag = tag
        new_line.data_block = list(data_block_from_mem)

        return set_index, victim_way_idx, evicted_dirty_line_info

    def invalidate_line_by_block_addr(self, block_addr):
        tag, set_index, _, _ = self._decode_address(block_addr)
        for way_idx, line_state in enumerate(self.table[set_index]):
            if line_state.valid and line_state.tag == tag:
                was_dirty = line_state.dirty
                line_state.valid = False
                line_state.dirty = False
                line_state.data_block = None
                return True, was_dirty
        return False, False

    def get_line_state_by_block_addr(self, block_addr):
        tag, set_index, _, _ = self._decode_address(block_addr)
        for way_idx, line_state in enumerate(self.table[set_index]):
            if line_state.valid and line_state.tag == tag:
                return line_state
        return None

    def reset(self):
        self.table = [[CacheLineState() for _ in range(self.num_ways)] for _ in range(self.num_sets)]

    def __str__(self):
        output = []
        for set_idx, ways in enumerate(self.table):
            line_strs = []
            for way_idx, line in enumerate(ways):
                if line.valid:
                    line_strs.append(f"W{way_idx}: {str(line)}")
            if line_strs:
                output.append(f"Set {set_idx:03d}: " + " | ".join(line_strs))
        return "\n".join(output)

