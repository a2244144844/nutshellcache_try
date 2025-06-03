module Cache_top;

  logic  clock;
  logic  reset;
  logic  io_in_req_ready;
  logic  io_in_req_valid;
  logic [31:0] io_in_req_bits_addr;
  logic [2:0] io_in_req_bits_size;
  logic [3:0] io_in_req_bits_cmd;
  logic [7:0] io_in_req_bits_wmask;
  logic [63:0] io_in_req_bits_wdata;
  logic [15:0] io_in_req_bits_user;
  logic  io_in_resp_ready;
  logic  io_in_resp_valid;
  logic [3:0] io_in_resp_bits_cmd;
  logic [63:0] io_in_resp_bits_rdata;
  logic [15:0] io_in_resp_bits_user;
  logic [1:0] io_flush;
  logic  io_out_mem_req_ready;
  logic  io_out_mem_req_valid;
  logic [31:0] io_out_mem_req_bits_addr;
  logic [2:0] io_out_mem_req_bits_size;
  logic [3:0] io_out_mem_req_bits_cmd;
  logic [7:0] io_out_mem_req_bits_wmask;
  logic [63:0] io_out_mem_req_bits_wdata;
  logic  io_out_mem_resp_ready;
  logic  io_out_mem_resp_valid;
  logic [3:0] io_out_mem_resp_bits_cmd;
  logic [63:0] io_out_mem_resp_bits_rdata;
  logic  io_out_coh_req_ready;
  logic  io_out_coh_req_valid;
  logic [31:0] io_out_coh_req_bits_addr;
  logic [2:0] io_out_coh_req_bits_size;
  logic [3:0] io_out_coh_req_bits_cmd;
  logic [7:0] io_out_coh_req_bits_wmask;
  logic [63:0] io_out_coh_req_bits_wdata;
  logic  io_out_coh_resp_ready;
  logic  io_out_coh_resp_valid;
  logic [3:0] io_out_coh_resp_bits_cmd;
  logic [63:0] io_out_coh_resp_bits_rdata;
  logic  io_mmio_req_ready;
  logic  io_mmio_req_valid;
  logic [31:0] io_mmio_req_bits_addr;
  logic [2:0] io_mmio_req_bits_size;
  logic [3:0] io_mmio_req_bits_cmd;
  logic [7:0] io_mmio_req_bits_wmask;
  logic [63:0] io_mmio_req_bits_wdata;
  logic  io_mmio_resp_ready;
  logic  io_mmio_resp_valid;
  logic [3:0] io_mmio_resp_bits_cmd;
  logic [63:0] io_mmio_resp_bits_rdata;
  logic  io_empty;
  logic  victim_way_mask_valid;
  logic [3:0] victim_way_mask;


 Cache Cache(
    .clock(clock),
    .reset(reset),
    .io_in_req_ready(io_in_req_ready),
    .io_in_req_valid(io_in_req_valid),
    .io_in_req_bits_addr(io_in_req_bits_addr),
    .io_in_req_bits_size(io_in_req_bits_size),
    .io_in_req_bits_cmd(io_in_req_bits_cmd),
    .io_in_req_bits_wmask(io_in_req_bits_wmask),
    .io_in_req_bits_wdata(io_in_req_bits_wdata),
    .io_in_req_bits_user(io_in_req_bits_user),
    .io_in_resp_ready(io_in_resp_ready),
    .io_in_resp_valid(io_in_resp_valid),
    .io_in_resp_bits_cmd(io_in_resp_bits_cmd),
    .io_in_resp_bits_rdata(io_in_resp_bits_rdata),
    .io_in_resp_bits_user(io_in_resp_bits_user),
    .io_flush(io_flush),
    .io_out_mem_req_ready(io_out_mem_req_ready),
    .io_out_mem_req_valid(io_out_mem_req_valid),
    .io_out_mem_req_bits_addr(io_out_mem_req_bits_addr),
    .io_out_mem_req_bits_size(io_out_mem_req_bits_size),
    .io_out_mem_req_bits_cmd(io_out_mem_req_bits_cmd),
    .io_out_mem_req_bits_wmask(io_out_mem_req_bits_wmask),
    .io_out_mem_req_bits_wdata(io_out_mem_req_bits_wdata),
    .io_out_mem_resp_ready(io_out_mem_resp_ready),
    .io_out_mem_resp_valid(io_out_mem_resp_valid),
    .io_out_mem_resp_bits_cmd(io_out_mem_resp_bits_cmd),
    .io_out_mem_resp_bits_rdata(io_out_mem_resp_bits_rdata),
    .io_out_coh_req_ready(io_out_coh_req_ready),
    .io_out_coh_req_valid(io_out_coh_req_valid),
    .io_out_coh_req_bits_addr(io_out_coh_req_bits_addr),
    .io_out_coh_req_bits_size(io_out_coh_req_bits_size),
    .io_out_coh_req_bits_cmd(io_out_coh_req_bits_cmd),
    .io_out_coh_req_bits_wmask(io_out_coh_req_bits_wmask),
    .io_out_coh_req_bits_wdata(io_out_coh_req_bits_wdata),
    .io_out_coh_resp_ready(io_out_coh_resp_ready),
    .io_out_coh_resp_valid(io_out_coh_resp_valid),
    .io_out_coh_resp_bits_cmd(io_out_coh_resp_bits_cmd),
    .io_out_coh_resp_bits_rdata(io_out_coh_resp_bits_rdata),
    .io_mmio_req_ready(io_mmio_req_ready),
    .io_mmio_req_valid(io_mmio_req_valid),
    .io_mmio_req_bits_addr(io_mmio_req_bits_addr),
    .io_mmio_req_bits_size(io_mmio_req_bits_size),
    .io_mmio_req_bits_cmd(io_mmio_req_bits_cmd),
    .io_mmio_req_bits_wmask(io_mmio_req_bits_wmask),
    .io_mmio_req_bits_wdata(io_mmio_req_bits_wdata),
    .io_mmio_resp_ready(io_mmio_resp_ready),
    .io_mmio_resp_valid(io_mmio_resp_valid),
    .io_mmio_resp_bits_cmd(io_mmio_resp_bits_cmd),
    .io_mmio_resp_bits_rdata(io_mmio_resp_bits_rdata),
    .io_empty(io_empty),
    .victim_way_mask_valid(victim_way_mask_valid),
    .victim_way_mask(victim_way_mask)
 );


  export "DPI-C" function get_clockxxPfBDHPSlkEh;
  export "DPI-C" function set_clockxxPfBDHPSlkEh;
  export "DPI-C" function get_resetxxPfBDHPSlkEh;
  export "DPI-C" function set_resetxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_validxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_req_bits_userxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_req_bits_userxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function set_io_in_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_in_resp_bits_userxxPfBDHPSlkEh;
  export "DPI-C" function get_io_flushxxPfBDHPSlkEh;
  export "DPI-C" function set_io_flushxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_mem_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_mem_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_mem_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_mem_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_mem_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_validxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function set_io_out_coh_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_out_coh_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function set_io_mmio_req_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_bits_addrxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_bits_sizexxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_bits_wmaskxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_req_bits_wdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_resp_readyxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function set_io_mmio_resp_validxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function set_io_mmio_resp_bits_cmdxxPfBDHPSlkEh;
  export "DPI-C" function get_io_mmio_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function set_io_mmio_resp_bits_rdataxxPfBDHPSlkEh;
  export "DPI-C" function get_io_emptyxxPfBDHPSlkEh;
  export "DPI-C" function get_victim_way_mask_validxxPfBDHPSlkEh;
  export "DPI-C" function get_victim_way_maskxxPfBDHPSlkEh;


  function void get_clockxxPfBDHPSlkEh;
    output logic  value;
    value=clock;
  endfunction

  function void set_clockxxPfBDHPSlkEh;
    input logic  value;
    clock=value;
  endfunction

  function void get_resetxxPfBDHPSlkEh;
    output logic  value;
    value=reset;
  endfunction

  function void set_resetxxPfBDHPSlkEh;
    input logic  value;
    reset=value;
  endfunction

  function void get_io_in_req_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_in_req_ready;
  endfunction

  function void get_io_in_req_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_in_req_valid;
  endfunction

  function void set_io_in_req_validxxPfBDHPSlkEh;
    input logic  value;
    io_in_req_valid=value;
  endfunction

  function void get_io_in_req_bits_addrxxPfBDHPSlkEh;
    output logic [31:0] value;
    value=io_in_req_bits_addr;
  endfunction

  function void set_io_in_req_bits_addrxxPfBDHPSlkEh;
    input logic [31:0] value;
    io_in_req_bits_addr=value;
  endfunction

  function void get_io_in_req_bits_sizexxPfBDHPSlkEh;
    output logic [2:0] value;
    value=io_in_req_bits_size;
  endfunction

  function void set_io_in_req_bits_sizexxPfBDHPSlkEh;
    input logic [2:0] value;
    io_in_req_bits_size=value;
  endfunction

  function void get_io_in_req_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_in_req_bits_cmd;
  endfunction

  function void set_io_in_req_bits_cmdxxPfBDHPSlkEh;
    input logic [3:0] value;
    io_in_req_bits_cmd=value;
  endfunction

  function void get_io_in_req_bits_wmaskxxPfBDHPSlkEh;
    output logic [7:0] value;
    value=io_in_req_bits_wmask;
  endfunction

  function void set_io_in_req_bits_wmaskxxPfBDHPSlkEh;
    input logic [7:0] value;
    io_in_req_bits_wmask=value;
  endfunction

  function void get_io_in_req_bits_wdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_in_req_bits_wdata;
  endfunction

  function void set_io_in_req_bits_wdataxxPfBDHPSlkEh;
    input logic [63:0] value;
    io_in_req_bits_wdata=value;
  endfunction

  function void get_io_in_req_bits_userxxPfBDHPSlkEh;
    output logic [15:0] value;
    value=io_in_req_bits_user;
  endfunction

  function void set_io_in_req_bits_userxxPfBDHPSlkEh;
    input logic [15:0] value;
    io_in_req_bits_user=value;
  endfunction

  function void get_io_in_resp_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_in_resp_ready;
  endfunction

  function void set_io_in_resp_readyxxPfBDHPSlkEh;
    input logic  value;
    io_in_resp_ready=value;
  endfunction

  function void get_io_in_resp_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_in_resp_valid;
  endfunction

  function void get_io_in_resp_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_in_resp_bits_cmd;
  endfunction

  function void get_io_in_resp_bits_rdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_in_resp_bits_rdata;
  endfunction

  function void get_io_in_resp_bits_userxxPfBDHPSlkEh;
    output logic [15:0] value;
    value=io_in_resp_bits_user;
  endfunction

  function void get_io_flushxxPfBDHPSlkEh;
    output logic [1:0] value;
    value=io_flush;
  endfunction

  function void set_io_flushxxPfBDHPSlkEh;
    input logic [1:0] value;
    io_flush=value;
  endfunction

  function void get_io_out_mem_req_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_mem_req_ready;
  endfunction

  function void set_io_out_mem_req_readyxxPfBDHPSlkEh;
    input logic  value;
    io_out_mem_req_ready=value;
  endfunction

  function void get_io_out_mem_req_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_mem_req_valid;
  endfunction

  function void get_io_out_mem_req_bits_addrxxPfBDHPSlkEh;
    output logic [31:0] value;
    value=io_out_mem_req_bits_addr;
  endfunction

  function void get_io_out_mem_req_bits_sizexxPfBDHPSlkEh;
    output logic [2:0] value;
    value=io_out_mem_req_bits_size;
  endfunction

  function void get_io_out_mem_req_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_out_mem_req_bits_cmd;
  endfunction

  function void get_io_out_mem_req_bits_wmaskxxPfBDHPSlkEh;
    output logic [7:0] value;
    value=io_out_mem_req_bits_wmask;
  endfunction

  function void get_io_out_mem_req_bits_wdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_out_mem_req_bits_wdata;
  endfunction

  function void get_io_out_mem_resp_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_mem_resp_ready;
  endfunction

  function void get_io_out_mem_resp_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_mem_resp_valid;
  endfunction

  function void set_io_out_mem_resp_validxxPfBDHPSlkEh;
    input logic  value;
    io_out_mem_resp_valid=value;
  endfunction

  function void get_io_out_mem_resp_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_out_mem_resp_bits_cmd;
  endfunction

  function void set_io_out_mem_resp_bits_cmdxxPfBDHPSlkEh;
    input logic [3:0] value;
    io_out_mem_resp_bits_cmd=value;
  endfunction

  function void get_io_out_mem_resp_bits_rdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_out_mem_resp_bits_rdata;
  endfunction

  function void set_io_out_mem_resp_bits_rdataxxPfBDHPSlkEh;
    input logic [63:0] value;
    io_out_mem_resp_bits_rdata=value;
  endfunction

  function void get_io_out_coh_req_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_coh_req_ready;
  endfunction

  function void get_io_out_coh_req_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_coh_req_valid;
  endfunction

  function void set_io_out_coh_req_validxxPfBDHPSlkEh;
    input logic  value;
    io_out_coh_req_valid=value;
  endfunction

  function void get_io_out_coh_req_bits_addrxxPfBDHPSlkEh;
    output logic [31:0] value;
    value=io_out_coh_req_bits_addr;
  endfunction

  function void set_io_out_coh_req_bits_addrxxPfBDHPSlkEh;
    input logic [31:0] value;
    io_out_coh_req_bits_addr=value;
  endfunction

  function void get_io_out_coh_req_bits_sizexxPfBDHPSlkEh;
    output logic [2:0] value;
    value=io_out_coh_req_bits_size;
  endfunction

  function void set_io_out_coh_req_bits_sizexxPfBDHPSlkEh;
    input logic [2:0] value;
    io_out_coh_req_bits_size=value;
  endfunction

  function void get_io_out_coh_req_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_out_coh_req_bits_cmd;
  endfunction

  function void set_io_out_coh_req_bits_cmdxxPfBDHPSlkEh;
    input logic [3:0] value;
    io_out_coh_req_bits_cmd=value;
  endfunction

  function void get_io_out_coh_req_bits_wmaskxxPfBDHPSlkEh;
    output logic [7:0] value;
    value=io_out_coh_req_bits_wmask;
  endfunction

  function void set_io_out_coh_req_bits_wmaskxxPfBDHPSlkEh;
    input logic [7:0] value;
    io_out_coh_req_bits_wmask=value;
  endfunction

  function void get_io_out_coh_req_bits_wdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_out_coh_req_bits_wdata;
  endfunction

  function void set_io_out_coh_req_bits_wdataxxPfBDHPSlkEh;
    input logic [63:0] value;
    io_out_coh_req_bits_wdata=value;
  endfunction

  function void get_io_out_coh_resp_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_coh_resp_ready;
  endfunction

  function void set_io_out_coh_resp_readyxxPfBDHPSlkEh;
    input logic  value;
    io_out_coh_resp_ready=value;
  endfunction

  function void get_io_out_coh_resp_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_out_coh_resp_valid;
  endfunction

  function void get_io_out_coh_resp_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_out_coh_resp_bits_cmd;
  endfunction

  function void get_io_out_coh_resp_bits_rdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_out_coh_resp_bits_rdata;
  endfunction

  function void get_io_mmio_req_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_mmio_req_ready;
  endfunction

  function void set_io_mmio_req_readyxxPfBDHPSlkEh;
    input logic  value;
    io_mmio_req_ready=value;
  endfunction

  function void get_io_mmio_req_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_mmio_req_valid;
  endfunction

  function void get_io_mmio_req_bits_addrxxPfBDHPSlkEh;
    output logic [31:0] value;
    value=io_mmio_req_bits_addr;
  endfunction

  function void get_io_mmio_req_bits_sizexxPfBDHPSlkEh;
    output logic [2:0] value;
    value=io_mmio_req_bits_size;
  endfunction

  function void get_io_mmio_req_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_mmio_req_bits_cmd;
  endfunction

  function void get_io_mmio_req_bits_wmaskxxPfBDHPSlkEh;
    output logic [7:0] value;
    value=io_mmio_req_bits_wmask;
  endfunction

  function void get_io_mmio_req_bits_wdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_mmio_req_bits_wdata;
  endfunction

  function void get_io_mmio_resp_readyxxPfBDHPSlkEh;
    output logic  value;
    value=io_mmio_resp_ready;
  endfunction

  function void get_io_mmio_resp_validxxPfBDHPSlkEh;
    output logic  value;
    value=io_mmio_resp_valid;
  endfunction

  function void set_io_mmio_resp_validxxPfBDHPSlkEh;
    input logic  value;
    io_mmio_resp_valid=value;
  endfunction

  function void get_io_mmio_resp_bits_cmdxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=io_mmio_resp_bits_cmd;
  endfunction

  function void set_io_mmio_resp_bits_cmdxxPfBDHPSlkEh;
    input logic [3:0] value;
    io_mmio_resp_bits_cmd=value;
  endfunction

  function void get_io_mmio_resp_bits_rdataxxPfBDHPSlkEh;
    output logic [63:0] value;
    value=io_mmio_resp_bits_rdata;
  endfunction

  function void set_io_mmio_resp_bits_rdataxxPfBDHPSlkEh;
    input logic [63:0] value;
    io_mmio_resp_bits_rdata=value;
  endfunction

  function void get_io_emptyxxPfBDHPSlkEh;
    output logic  value;
    value=io_empty;
  endfunction

  function void get_victim_way_mask_validxxPfBDHPSlkEh;
    output logic  value;
    value=victim_way_mask_valid;
  endfunction

  function void get_victim_way_maskxxPfBDHPSlkEh;
    output logic [3:0] value;
    value=victim_way_mask;
  endfunction



  initial begin
    $dumpfile("Cache.fst");
    $dumpvars(0, Cache_top);
  end

  export "DPI-C" function finish_PfBDHPSlkEh;
  function void finish_PfBDHPSlkEh;
    $finish;
  endfunction


endmodule
