"""
This script generates the xdc file for debugging

Note that all the wires to debug must be present in the synthesized design

Currently, the debug hub clock and the ila clock should be the same and should be free-running
Not sure if other setup works correctly.
"""

# ---- This part is the only part that needs to be changed ----
nets_clk = 'sh_root_clk'
nets_clk_mhz = '100'
nets_to_debug = [
        ("Confreg/reg_initPC", 64) ,
        ("Confreg/reg_resetReg", 64),
        ("Confreg/reg_st", 2),

        ]
depth = 16384
pipe_stages = 3
# ---- Generate the ports ----
current_port_id = 0
res = ''
for net_id in nets_to_debug:
    if current_port_id != 0:
        res = res + 'create_debug_port u_ila_0 probe\n'
    if net_id[1] == 1:
        net_list = '{' + net_id[0] + '}'
    else:
        net_list = ' '.join('{' + net_id[0] + f'[{idx}]' + '}' for idx in range(net_id[1]))
    res +=  f"""
set_property PROBE_TYPE DATA_AND_TRIGGER [get_debug_ports u_ila_0/probe{current_port_id}]
set_property port_width {net_id[1]} [get_debug_ports u_ila_0/probe{current_port_id}]
set_property MARK_DEBUG TRUE [ get_nets {net_id[0]}* ]
connect_debug_port u_ila_0/probe{current_port_id} [ get_nets [list {net_list} ] ]
"""

    current_port_id += 1
# ---- ----

template = f"""
# This file is generated automatically by Python script
# create the debug core (and dbg_hub automatically)
create_debug_core u_ila_0 ila

# some fixed parameter that is used in the dialog
set_property ALL_PROBE_SAME_MU true [get_debug_cores u_ila_0]
set_property ALL_PROBE_SAME_MU_CNT 4 [get_debug_cores u_ila_0]
set_property C_ADV_TRIGGER true [get_debug_cores u_ila_0]
set_property C_DATA_DEPTH {depth} [get_debug_cores u_ila_0]
set_property C_EN_STRG_QUAL true [get_debug_cores u_ila_0]
set_property C_INPUT_PIPE_STAGES {pipe_stages} [get_debug_cores u_ila_0]
set_property C_TRIGIN_EN false [get_debug_cores u_ila_0]
set_property C_TRIGOUT_EN false [get_debug_cores u_ila_0]

# Setup the clock for u_ila_0
set_property port_width 1 [get_debug_ports u_ila_0/clk]
connect_debug_port u_ila_0/clk [get_nets [list {nets_clk}]]

{res}

# Something for the debug hub
# when you create u_ila_0, the dbg_hub is created as well
# these parts should be constant
set_property C_CLK_INPUT_FREQ_HZ {nets_clk_mhz}000000 [get_debug_cores dbg_hub]
set_property C_ENABLE_CLK_DIVIDER true [get_debug_cores dbg_hub]
set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
connect_debug_port dbg_hub/clk [get_nets {nets_clk}]

"""


print(template)
