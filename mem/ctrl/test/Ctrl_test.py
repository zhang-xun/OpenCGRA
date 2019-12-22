"""
==========================================================================
Ctrl_test.py
==========================================================================
Test cases for control memory.

Author : Cheng Tan
  Date : Dec 21, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ....fu.single.Alu            import Alu
from ..CtrlMem                    import CtrlMem
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, DataType, ConfigType, nregs, src0_msgs, src1_msgs,
                 ctrl_raddr, ctrl_waddr, ctrl_msgs, sink_msgs ):

    AddrType = mk_bits( clog2( nregs ) )

    s.src_data0 = TestSrcRTL( DataType,   src0_msgs  )
    s.src_data1 = TestSrcRTL( DataType,   src1_msgs  )
    s.src_raddr = TestSrcRTL( AddrType,   ctrl_raddr )
    s.src_waddr = TestSrcRTL( AddrType,   ctrl_waddr )
    s.src_wdata = TestSrcRTL( ConfigType, ctrl_msgs  )
    s.sink_out  = TestSinkCL( DataType,   sink_msgs  )

    s.alu       = Alu( DataType, ConfigType )
    s.ctrl_mem  = CtrlMem( ConfigType, nregs )

    print( "recv_opt: ", s.alu.recv_opt, "; send_rdata: ", s.ctrl_mem.send_rdata )
    connect( s.alu.recv_opt,   s.ctrl_mem.send_rdata[0] )

    connect( s.src_raddr.send, s.ctrl_mem.recv_raddr[0] )
    connect( s.src_waddr.send, s.ctrl_mem.recv_waddr[0] )
    connect( s.src_wdata.send, s.ctrl_mem.recv_wdata[0] )

    connect( s.src_data0.send, s.alu.recv_in0           )
    connect( s.src_data1.send, s.alu.recv_in1           )
    connect( s.alu.send_out0,  s.sink_out.recv          )

  def done( s ):
    return s.src_data0.done() and s.src_data1.done() and\
           s.sink_out.done()

  def line_trace( s ):
    return s.alu.line_trace() + " || " +s.ctrl_mem.line_trace()

def run_sim( test_harness, max_cycles=100 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

def test_Ctrl():
  DataType  = mk_data( 16, 1 )
  CtrlType  = mk_ctrl()
  nregs     = 8
  AddrType  = mk_bits( clog2( nregs ) )
  src_data0 = [DataType(0,0),DataType(1,1),DataType(5,1),DataType(7,1),DataType(6,1)]
  src_data1 = [DataType(0,0),DataType(6,1),DataType(1,1),DataType(2,1),DataType(3,1)]
  src_raddr = [AddrType( 0 ),AddrType( 0 ),AddrType( 1 ),AddrType( 2 ),AddrType( 3 )]
  src_waddr = [AddrType( 0 ),AddrType( 1 ),AddrType( 2 ),AddrType( 3 )]
  src_wdata = [CtrlType(OPT_ADD),CtrlType(OPT_SUB),CtrlType(OPT_SUB),CtrlType(OPT_ADD)]
  sink_out  = [DataType(0,0),DataType(7,1),DataType(4,1),DataType(5,1),DataType(9,1)]
  th = TestHarness( DataType, CtrlType, nregs, src_data0, src_data1,
                    src_raddr, src_waddr, src_wdata, sink_out )
  run_sim( th )
