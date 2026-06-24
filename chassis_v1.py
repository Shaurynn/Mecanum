import FreeCAD as App
import Part

# ==============================================================================
# 1. GLOBAL CHASSIS PARAMETERS
# ==============================================================================
W = 180.0          
L = 220.0          
H = 4.0            

m3_r = 1.6         # 3.2mm diameter for M3 screw shafts
m3_cb_r = 3.2      # 6.4mm diameter for M3 hex socket cap (Counterbore)
m2_5_r = 1.4       # 2.8mm diameter for M2.5 screws clearance
standoff_inset = 8.0 

deck2_z = 45.0     
deck3_z = 90.0     

# ==============================================================================
# 2. STRUCTURAL RIB & MOTOR PAD PARAMETERS
# ==============================================================================
rib_h = 3.0        
rib_w = 2.0        
rib_spacing = 35.0 

pad_l, pad_w, pad_h = 45.0, 40.0, 4.0        

motor_cutout_w, motor_cutout_l = 15.0, 20.0
mc_positions = [
    (8.0, pad_l),                                           
    (W - 8.0 - motor_cutout_w, pad_l),                      
    (8.0, L - pad_l - motor_cutout_l),                      
    (W - 8.0 - motor_cutout_w, L - pad_l - motor_cutout_l)  
]

# ==============================================================================
# 3. PCB & SENSOR MOUNTING PARAMETERS
# ==============================================================================
cytron_hx, cytron_hy, cytron_center_y = 97.0, 67.0, 55.0 
nucleo_hx, nucleo_hy, nucleo_center_y = 58.0, 71.0, 165.0 

pmw_hx, pmw_tail_w, pmw_tail_l = 32.0, 44.0, 30.0  
pmw_cx, pmw_cy = W / 2, -(pmw_tail_l / 2) 
tof_hx, tof_cx = 20.0, W / 2     

um982_hx, um982_hy = 27.0, 45.0
um982_cx, um982_cy = 25.0, 65.0 

jetson_hx, jetson_hy = 58.0, 87.0
jetson_cx, jetson_cy = 90.0, 65.0

sx_hx, sx_hy = 44.0, 66.0 
sx_cx, sx_cy = 155.0, 65.0

# Modular Boom & RTK Parameters
rtk_base_r = 28.0                              
rtk_ir, rtk_or, rtk_h = 22.4, 25.4, 14.0       
sma_hole_r = 7.0   

boom_overlap = 30.0    # Boom arms insert 30mm under the chassis
boom_w = 48.0      
boom_y = (L/2) - (boom_w/2)     
rtk_left_x = -66.0     # Exactly 312mm baseline span
rtk_right_x = 246.0    

# Create a new document
doc = App.newDocument("Mecanum_Chassis_Modular")

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def get_rib_grid(z_offset):
    """Generates the structural lattice so it can be fused or used as a boolean cutting tool"""
    grid = Part.makeBox(0.1, 0.1, 0.1) 
    grid.translate(App.Vector(-10, -10, -10))
    
    for i in range(1, int(L / rib_spacing)):
        y_pos = i * rib_spacing
        rib = Part.makeBox(W, rib_w, rib_h)
        rib.translate(App.Vector(0, y_pos - (rib_w/2), z_offset - rib_h))
        grid = grid.fuse(rib)
        
    for j in range(1, int(W / rib_spacing)):
        x_pos = j * rib_spacing
        rib = Part.makeBox(rib_w, L, rib_h)
        rib.translate(App.Vector(x_pos - (rib_w/2), 0, z_offset - rib_h))
        grid = grid.fuse(rib)
        
    return grid

def create_plate(name, z_offset):
    plate = Part.makeBox(W, L, H)
    plate.translate(App.Vector(0, 0, z_offset))
    plate = plate.fuse(get_rib_grid(z_offset))
        
    corners = [(standoff_inset, standoff_inset), (W - standoff_inset, standoff_inset),
               (standoff_inset, L - standoff_inset), (W - standoff_inset, L - standoff_inset)]
    for cx, cy in corners:
        hole = Part.makeCylinder(m3_r, H + rib_h + 2)
        hole.translate(App.Vector(cx, cy, z_offset - rib_h - 1))
        plate = plate.cut(hole)
        
    return plate

# ==============================================================================
# DECK 1: DRIVE & ODOMETRY
# ==============================================================================
deck1 = create_plate("Deck1_Base", 0)

pad_positions = [(0, 0), (W - pad_w, 0), (0, L - pad_l), (W - pad_w, L - pad_l)]
for px, py in pad_positions:
    pad = Part.makeBox(pad_w, pad_l, pad_h)
    pad.translate(App.Vector(px, py, -pad_h)) 
    deck1 = deck1.fuse(pad)
    
    cx, cy = px + (pad_w / 2), py + (pad_l / 2)
    for dx, dy in [(-12.5, -12.5), (12.5, -12.5), (-12.5, 12.5), (12.5, 12.5)]:
        hole = Part.makeCylinder(m3_r, H + pad_h + 2)
        hole.translate(App.Vector(cx + dx, cy + dy, -pad_h - 1))
        deck1 = deck1.cut(hole)
        cb_hole = Part.makeCylinder(m3_cb_r, 4.0)
        cb_hole.translate(App.Vector(cx + dx, cy + dy, 1.5)) 
        deck1 = deck1.cut(cb_hole)

for mx, my in mc_positions:
    mc = Part.makeBox(motor_cutout_w, motor_cutout_l, H + rib_h + pad_h + 2)
    mc.translate(App.Vector(mx, my, -pad_h - 1))
    deck1 = deck1.cut(mc)

safe_x = [50.0, 90.0, 130.0] 
safe_y = [50.0, 85.0, 120.0, 155.0]
for sx in safe_x:
    for sy in safe_y:
        bat_hole = Part.makeCylinder(m3_r, H + rib_h + 2)
        bat_hole.translate(App.Vector(sx, sy, -rib_h - 1))
        deck1 = deck1.cut(bat_hole)

for hx in [tof_cx - 10, tof_cx + 10]:
    tof_mount = Part.makeCylinder(m3_r, H + rib_h + 2)
    tof_mount.translate(App.Vector(hx, L - 10, -rib_h - 1))
    deck1 = deck1.cut(tof_mount)

Part.show(deck1)
doc.ActiveObject.Label = "Deck_1_Drive"


# ==============================================================================
# DECK 2: LOGIC & POWER
# ==============================================================================
deck2 = create_plate("Deck2_Logic", deck2_z)

power_passthrough_2 = Part.makeBox(50, 20, H + rib_h + 2)
power_passthrough_2.translate(App.Vector((W/2)-25, (L/2)-10, deck2_z - rib_h - 1))
deck2 = deck2.cut(power_passthrough_2)

for mx, my in mc_positions:
    mc = Part.makeBox(motor_cutout_w, motor_cutout_l, H + rib_h + 2)
    mc.translate(App.Vector(mx, my, deck2_z - rib_h - 1))
    deck2 = deck2.cut(mc)

for hx, hy in [(W/2 - cytron_hx/2 -2, cytron_center_y - cytron_hy/2), (W/2 + cytron_hx/2 -2, cytron_center_y - cytron_hy/2),
               (W/2 - cytron_hx/2 -2, cytron_center_y + cytron_hy/2), (W/2 + cytron_hx/2 -2, cytron_center_y + cytron_hy/2)]:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(hx, hy, deck2_z - rib_h - 1))
    deck2 = deck2.cut(hole)

for hx, hy in [(W/2 - nucleo_hx/2, nucleo_center_y + nucleo_hy/2), (W/2 - nucleo_hx/2, nucleo_center_y - nucleo_hy/2), 
               (W/2 + nucleo_hx/2, nucleo_center_y - nucleo_hy/2)]:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(hx, hy, deck2_z - rib_h - 1))
    deck2 = deck2.cut(hole)

Part.show(deck2)
doc.ActiveObject.Label = "Deck_2_Logic"


# ==============================================================================
# DECK 3: AUTONOMY & MODULAR HARD POINTS
# ==============================================================================
deck3 = create_plate("Deck3_Autonomy", deck3_z)

# Central Passthrough
power_passthrough_3 = Part.makeBox(50, 20, H + rib_h + 2)
power_passthrough_3.translate(App.Vector((W/2)-25, (L/2)-10, deck3_z - rib_h - 1))
deck3 = deck3.cut(power_passthrough_3)

# 1. Unicore UM982 Holes
for hx, hy in [(um982_cx - um982_hx/2, um982_cy - um982_hy/2), (um982_cx + um982_hx/2, um982_cy - um982_hy/2),
               (um982_cx - um982_hx/2, um982_cy + um982_hy/2), (um982_cx + um982_hx/2, um982_cy + um982_hy/2)]:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(hx, hy, deck3_z - rib_h - 1))
    deck3 = deck3.cut(hole)

# 2. Jetson Orin Nano Super Holes
for hx, hy in [(jetson_cx - jetson_hx/2, jetson_cy - jetson_hy/2), (jetson_cx + jetson_hx/2, jetson_cy - jetson_hy/2),
               (jetson_cx - jetson_hx/2, jetson_cy + jetson_hy/2), (jetson_cx + jetson_hx/2, jetson_cy + jetson_hy/2)]:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(hx, hy, deck3_z - rib_h - 1))
    deck3 = deck3.cut(hole)

# 3. Silicontra SX1280 Bay Holes
for hx, hy in [(sx_cx - sx_hx/2, sx_cy - sx_hy/2), (sx_cx + sx_hx/2, sx_cy - sx_hy/2),
               (sx_cx - sx_hx/2, sx_cy + sx_hy/2), (sx_cx + sx_hx/2, sx_cy + sx_hy/2)]:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(hx, hy, deck3_z - rib_h - 1))
    deck3 = deck3.cut(hole)

# 4. Modular Boom Arm Attachment Points (Counterbored)
boom_screw_points = [
    (8, 94), (22, 94), (8, 126), (22, 126),         # Left side overlap mounts
    (158, 94), (172, 94), (158, 126), (172, 126)    # Right side overlap mounts
]
for bx, by in boom_screw_points:
    hole = Part.makeCylinder(m3_r, H + rib_h + 2)
    hole.translate(App.Vector(bx, by, deck3_z - rib_h - 1))
    deck3 = deck3.cut(hole)
    
    cb_hole = Part.makeCylinder(m3_cb_r, 4.0)
    cb_hole.translate(App.Vector(bx, by, deck3_z + H - 2.5)) 
    deck3 = deck3.cut(cb_hole)

# 5. Direct Optical Flow Tail
tail_plate = Part.makeBox(pmw_tail_w, pmw_tail_l, H)
tail_plate.translate(App.Vector(W/2 - pmw_tail_w/2, -pmw_tail_l, deck3_z))
deck3 = deck3.fuse(tail_plate)

tail_viewport = Part.makeBox(20, 20, H + 2)
tail_viewport.translate(App.Vector(pmw_cx - 10, pmw_cy - 10, deck3_z - 1))
deck3 = deck3.cut(tail_viewport)

for hx in [pmw_cx - 16.0, pmw_cx + 16.0]:
    m25_hole = Part.makeCylinder(m2_5_r, H + 2)
    m25_hole.translate(App.Vector(hx, pmw_cy, deck3_z - 1))
    deck3 = deck3.cut(m25_hole)

# 6. Modular Payload Grid
grid_start_y = L * 0.55  
spacing = 15.0           
for i in range(int((W - 30) / spacing) + 1):
    for j in range(int(((L - grid_start_y) - 15) / spacing) + 1):
        grid_hole = Part.makeCylinder(m3_r, H + rib_h + 2)
        grid_hole.translate(App.Vector(15.0 + (i * spacing), grid_start_y + (j * spacing), deck3_z - rib_h - 1))
        deck3 = deck3.cut(grid_hole)

# 7. M5Stack Bracket Holes
for hx in [(W/2) - 17, (W/2) + 17]:
    m5_mount = Part.makeCylinder(m3_r, H + rib_h + 2)
    m5_mount.translate(App.Vector(hx, L - 12, deck3_z - rib_h - 1))
    deck3 = deck3.cut(m5_mount)

# 8. GPS Mast Holes
for dx, dy in [(-10, -10), (10, -10), (-10, 10), (10, 10)]:
    gps_mount = Part.makeCylinder(m3_r, H + rib_h + 2)
    gps_mount.translate(App.Vector((W/2) + dx, 20 + dy, deck3_z - rib_h - 1))
    deck3 = deck3.cut(gps_mount)

Part.show(deck3)
doc.ActiveObject.Label = "Deck_3_Autonomy"

# ==============================================================================
# SEPARATE MODULAR COMPONENTS (Printed Independently)
# ==============================================================================

def create_boom_arm(name, is_left):
    b_span = abs(rtk_left_x) + boom_overlap 
    b_start_x = rtk_left_x if is_left else (W - boom_overlap)
    pad_x = rtk_left_x if is_left else rtk_right_x
    
    # 1. Base Plate (Bolts directly flush underneath Deck 3)
    boom_base = Part.makeBox(b_span, boom_w, H)
    boom_base.translate(App.Vector(b_start_x, boom_y, deck3_z - H))
    
    boom_pad = Part.makeCylinder(rtk_base_r, H)
    boom_pad.translate(App.Vector(pad_x, L/2, deck3_z - H))
    boom = boom_base.fuse(boom_pad)
    
    # 2. Structural Ribs (Recalculated to end at the circular wall)
    # The ribs span strictly from the chassis edge to the outer radius of the RTK wall
    rib_length = abs(rtk_left_x) - rtk_or 
    rib_start_x = (rtk_left_x + rtk_or) if is_left else W
    
    top_rib1 = Part.makeBox(rib_length, rib_w, rib_h)
    top_rib1.translate(App.Vector(rib_start_x, boom_y + 12.0, deck3_z))
    boom = boom.fuse(top_rib1)
    
    top_rib2 = Part.makeBox(rib_length, rib_w, rib_h)
    top_rib2.translate(App.Vector(rib_start_x, boom_y + boom_w - 12.0, deck3_z))
    boom = boom.fuse(top_rib2)
    
    # 3. RTK Circular Ring
    rtk_outer = Part.makeCylinder(rtk_or, rtk_h)
    rtk_inner = Part.makeCylinder(rtk_ir, rtk_h)
    rtk_tube = rtk_outer.cut(rtk_inner)
    rtk_tube.translate(App.Vector(pad_x, L/2, deck3_z))
    boom = boom.fuse(rtk_tube)
    
    # 4. SMA Central Hole
    sma_cut = Part.makeCylinder(sma_hole_r, H + 2)
    sma_cut.translate(App.Vector(pad_x, L/2, deck3_z - H - 1))
    boom = boom.cut(sma_cut)
    
    # 5. Snap-Fit Interlocking Trenches
    boom = boom.cut(get_rib_grid(deck3_z))
    
    # 6. Bolt Holes for Deck Mating
    holes = boom_screw_points[:4] if is_left else boom_screw_points[4:]
    for bx, by in holes:
        bh = Part.makeCylinder(m3_r, H + 2)
        bh.translate(App.Vector(bx, by, deck3_z - H - 1))
        boom = boom.cut(bh)
        
    boom.translate(App.Vector(-20, 60, 0) if is_left else App.Vector(20, 60, 0))
    Part.show(boom)
    doc.ActiveObject.Label = name

create_boom_arm("Mount_Boom_Left", is_left=True)
create_boom_arm("Mount_Boom_Right", is_left=False)

# ------------------------------------------------------------------------------
# REMAINING MODULAR MOUNTS
# ------------------------------------------------------------------------------

# VL53L1X L-Bracket
vl53_base = Part.makeBox(34, 20, 4)
vl53_upright = Part.makeBox(34, 4, 16)
vl53_upright.translate(App.Vector(0, 16, 0)) 
vl53_bracket = vl53_base.fuse(vl53_upright)
for hx in [7, 27]:
    hole = Part.makeCylinder(m3_r, 6)
    hole.translate(App.Vector(hx, 10, -1))
    vl53_bracket = vl53_bracket.cut(hole)
for hx in [17 - (tof_hx/2), 17 + (tof_hx/2)]:
    hole = Part.makeCylinder(m2_5_r, 6)
    hole.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    hole.translate(App.Vector(hx, 21, 10))
    vl53_bracket = vl53_bracket.cut(hole)
vl53_bracket.translate(App.Vector(-50, 0, 0))
Part.show(vl53_bracket)
doc.ActiveObject.Label = "Mount_VL53L1X"

# M5Stack CoreS3 Bracket 
m5_base = Part.makeBox(54, 20, 4)
m5_upright = Part.makeBox(54, 4, 60)
m5_upright.translate(App.Vector(0, 16, 0))
m5_bracket = m5_base.fuse(m5_upright)
for hx in [10, 44]:
    hole = Part.makeCylinder(m3_r, 6)
    hole.translate(App.Vector(hx, 8, -1))
    m5_bracket = m5_bracket.cut(hole)
for gx in [5, 49]:   
    for gz in [10, 54]: 
        hole = Part.makeCylinder(m3_r, 6)
        hole.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
        hole.translate(App.Vector(gx, 21, gz))
        m5_bracket = m5_bracket.cut(hole)
m5_bracket.translate(App.Vector(-120, 0, 0))
Part.show(m5_bracket)
doc.ActiveObject.Label = "Mount_M5Stack"

# GPS External Hollow Mast 
gps_base = Part.makeBox(30, 30, 4)
gps_base.translate(App.Vector(-15, -15, 0))
gps_outer = Part.makeCylinder(8, 80)
gps_inner = Part.makeCylinder(5, 80)
gps_pipe = gps_outer.cut(gps_inner)
gps_pipe.translate(App.Vector(0, 0, 4))
cable_door = Part.makeBox(10, 10, 8)
cable_door.translate(App.Vector(-5, 0, 4)) 
gps_pipe = gps_pipe.cut(cable_door)
gps_top = Part.makeBox(30, 30, 4)
gps_top.translate(App.Vector(-15, -15, 84)) 
gps_assembly = gps_base.fuse(gps_pipe).fuse(gps_top)
for dx, dy in [(-10, -10), (10, -10), (-10, 10), (10, 10)]:
    hole = Part.makeCylinder(m3_r, 6)
    hole.translate(App.Vector(dx, dy, -1))
    gps_assembly = gps_assembly.cut(hole)
top_sma = Part.makeCylinder(sma_hole_r, 10)
top_sma.translate(App.Vector(0, 0, 80))
gps_assembly = gps_assembly.cut(top_sma)
top_cable_channel = Part.makeBox(5, 20, 6)
top_cable_channel.translate(App.Vector(-2.5, 0, 83))
gps_assembly = gps_assembly.cut(top_cable_channel)
bottom_sma = Part.makeCylinder(sma_hole_r, 10)
bottom_sma.translate(App.Vector(0, 0, 0))
gps_assembly = gps_assembly.cut(bottom_sma)
bottom_cable_channel = Part.makeBox(5, 20, 6)
bottom_cable_channel.translate(App.Vector(-2.5, 0, 0))
gps_assembly = gps_assembly.cut(bottom_cable_channel)
gps_assembly.translate(App.Vector(-120, 80, 0))
Part.show(gps_assembly)
doc.ActiveObject.Label = "Mount_GPS_Mast"

doc.recompute()
App.Gui.SendMsgToActiveView("ViewFit")