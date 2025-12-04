import streamlit as st
import matplotlib.pyplot as plt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="Pants Pattern Generator", layout="wide")
st.title("👖 Custom Pants Pattern Generator")
st.write("Enter your measurements to generate a schematic for Front and Back pants blocks.")

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Measurements")

# Unit Switcher
unit = st.sidebar.radio("Select Unit:", ["cm", "inches"])

if unit == "cm":
    def_waist, def_hips, def_length = 80.0, 100.0, 105.0
    step_val = 1.0
else:
    def_waist, def_hips, def_length = 31.0, 40.0, 41.0
    step_val = 0.5

# Input Fields
name = st.sidebar.text_input("Client Name", "Client A")
waist = st.sidebar.number_input("Waist Circumference", value=def_waist, step=step_val)
hips = st.sidebar.number_input("Hip Circumference", value=def_hips, step=step_val)
length = st.sidebar.number_input("Outseam Length", value=def_length, step=step_val)

# --- 3. HELPER FUNCTION FOR CURVES ---
def get_curve_points(start, end, control, resolution=20):
    path_x = []
    path_y = []
    for i in range(resolution + 1):
        t = i / resolution
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        path_x.append(x)
        path_y.append(y)
    return path_x, path_y

# --- 4. CALCULATION ENGINE ---
if st.button("Generate Pattern"):
    # Define Constants based on unit
    if unit == "cm":
        crotch_depth = hips / 4
        crotch_ext_f = 4.0
        crotch_ext_b = hips / 10  # Standard back crotch formula
        hem_width = (hips / 4) - 2
        offset = (hips / 2) + 15
    else:
        crotch_depth = hips / 4
        crotch_ext_f = 1.5
        crotch_ext_b = hips / 10
        hem_width = (hips / 4) - 1
        offset = (hips / 2) + 6

    # Coordinate Math
    q_waist = waist / 4
    q_hips = hips / 4

    # --- FRONT PIECE ---
    f_waist_center = (0, length)
    f_waist_side   = (q_waist, length)
    f_hip_side     = (q_hips, length - crotch_depth)
    f_crotch_pt    = (-crotch_ext_f, length - crotch_depth)
    f_hem_outer    = (hem_width, 0)
    f_hem_inner    = (0, 0)

    # 1. Front Crotch Curve
    fc_start = f_waist_center
    fc_end = f_crotch_pt
    fc_control = (0, length - crotch_depth + (crotch_depth/2))
    fx_curve, fy_curve = get_curve_points(fc_start, fc_end, fc_control)

    # 2. Front Hip Curve (New!)
    # We curve from the Hip Point up to the Waist Point.
    # Control point logic: (Hip X, Waist Y) creates a standard convex hip shape.
    fh_start = f_hip_side
    fh_end = f_waist_side
    fh_control = (f_hip_side[0], f_waist_side[1]) 
    fh_curve_x, fh_curve_y = get_curve_points(fh_start, fh_end, fh_control)

    # Assemble Front Points
    # Order: Crotch Curve -> Crotch Pt -> Hem Inner -> Hem Outer -> Hip Curve -> Waist Center
    x_front = fx_curve + [f_crotch_pt[0], f_hem_inner[0], f_hem_outer[0]] + fh_curve_x + [f_waist_center[0]]
    y_front = fy_curve + [f_crotch_pt[1], f_hem_inner[1], f_hem_outer[1]] + fh_curve_y + [f_waist_center[1]]

    # --- BACK PIECE ---
    b_waist_center = (offset, length + (2 if unit=="cm" else 1)) # Higher back rise
    b_waist_side   = (offset + q_waist + 1, length) 
    b_hip_side     = (offset + q_hips + 1, length - crotch_depth)
    b_crotch_pt    = (offset - crotch_ext_b, length - crotch_depth)
    b_hem_outer    = (offset + hem_width + 1, 0)
    b_hem_inner    = (offset, 0)

    # 1. Back Crotch Curve
    bc_start = b_waist_center
    bc_end = b_crotch_pt
    bc_control = (offset, length - crotch_depth + (crotch_depth/3))
    bx_curve, by_curve = get_curve_points(bc_start, bc_end, bc_control)

    # 2. Back Hip Curve (New!)
    bh_start = b_hip_side
    bh_end = b_waist_side
    bh_control = (b_hip_side[0], b_waist_side[1])
    bh_curve_x, bh_curve_y = get_curve_points(bh_start, bh_end, bh_control)

    # Assemble Back Points
    x_back = bx_curve + [b_crotch_pt[0], b_hem_inner[0], b_hem_outer[0]] + bh_curve_x + [b_waist_center[0]]
    y_back = by_curve + [b_crotch_pt[1], b_hem_inner[1], b_hem_outer[1]] + bh_curve_y + [b_waist_center[1]]

    # --- PLOTTING ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Front
    ax.plot(x_front, y_front, color='navy', label="Front")
    ax.fill(x_front, y_front, color='lightblue', alpha=0.3)
    
    # Plot Back
    ax.plot(x_back, y_back, color='darkred', label="Back")
    ax.fill(x_back, y_back, color='pink', alpha=0.3)
    
    # Labels
    ax.text(q_waist/2, length/2, "FRONT", ha='center', fontweight='bold')
    ax.text(offset + q_waist/2, length/2, "BACK", ha='center', fontweight='bold')
    
    ax.set_title(f"Pattern for: {name}")
    ax.axis('equal')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

    # Display in Streamlit
    st.pyplot(fig)

    # Fabric Calc
    st.success("Pattern Generated Successfully!")
    if unit == "cm":
        st.info(f"Estimated Fabric: {(length*2 + 20)/100} Meters")
    else:
        st.info(f"Estimated Fabric: {(length*2 + 8)/36:.2f} Yards")
Gemini 3 Pro
edit the code again, I only want the hip curve, not the waist end, waist line should stay straight


Thought Process
expand
I have updated the code below.

I reorganized the Calculation Engine to explicitly define the boundary of the pattern in segments. The list of coordinates now builds the shape clockwise:

Rise (Curved)
Inseam (Straight)
Hem (Straight)
Lower Outseam (Straight)
Hip (Curved)
Waistline (Strictly Straight)
This ensures the line connecting the side of the waist to the center of the waist is a perfectly straight line, while the hip stays smooth.

python
import streamlit as st
import matplotlib.pyplot as plt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="Pants Pattern Generator", layout="wide")
st.title("👖 Custom Pants Pattern Generator")
st.write("Enter your measurements to generate a schematic for Front and Back pants blocks.")

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Measurements")

# Unit Switcher
unit = st.sidebar.radio("Select Unit:", ["cm", "inches"])

if unit == "cm":
    def_waist, def_hips, def_length = 80.0, 100.0, 105.0
    step_val = 1.0
else:
    def_waist, def_hips, def_length = 31.0, 40.0, 41.0
    step_val = 0.5

# Input Fields
name = st.sidebar.text_input("Client Name", "Client A")
waist = st.sidebar.number_input("Waist Circumference", value=def_waist, step=step_val)
hips = st.sidebar.number_input("Hip Circumference", value=def_hips, step=step_val)
length = st.sidebar.number_input("Outseam Length", value=def_length, step=step_val)

# --- 3. HELPER FUNCTION FOR CURVES ---
def get_curve_points(start, end, control, resolution=20):
    path_x = []
    path_y = []
    for i in range(resolution + 1):
        t = i / resolution
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        path_x.append(x)
        path_y.append(y)
    return path_x, path_y

# --- 4. CALCULATION ENGINE ---
if st.button("Generate Pattern"):
    # Define Constants based on unit
    if unit == "cm":
        crotch_depth = hips / 4
        crotch_ext_f = 4.0
        crotch_ext_b = hips / 10  
        hem_width = (hips / 4) - 2
        offset = (hips / 2) + 15
    else:
        crotch_depth = hips / 4
        crotch_ext_f = 1.5
        crotch_ext_b = hips / 10
        hem_width = (hips / 4) - 1
        offset = (hips / 2) + 6

    # Coordinate Math
    q_waist = waist / 4
    q_hips = hips / 4

    # --- FRONT PIECE ---
    f_waist_center = (0, length)
    f_waist_side   = (q_waist, length)
    f_hip_side     = (q_hips, length - crotch_depth)
    f_crotch_pt    = (-crotch_ext_f, length - crotch_depth)
    f_hem_outer    = (hem_width, 0)
    f_hem_inner    = (0, 0)

    # A. Front Rise Curve (Waist Center -> Crotch Point)
    fc_start = f_waist_center
    fc_end = f_crotch_pt
    fc_control = (0, length - crotch_depth + (crotch_depth/2))
    fx_curve, fy_curve = get_curve_points(fc_start, fc_end, fc_control)

    # B. Front Hip Curve (Hip Side -> Waist Side)
    # Control point: (Hip X, Waist Y) creates a gentle curve that meets the waist cleanly
    fh_start = f_hip_side
    fh_end = f_waist_side
    fh_control = (f_hip_side[0], f_waist_side[1]) 
    fh_curve_x, fh_curve_y = get_curve_points(fh_start, fh_end, fh_control)

    # ASSEMBLE FRONT (Clockwise logic for clarity)
    # 1. Rise (Curved) -> 2. Inseam (Straight) -> 3. Hem (Straight) 
    # -> 4. Lower Side (Straight) -> 5. Hip (Curved) -> 6. Waist (Straight connection)
    x_front = fx_curve + [f_hem_inner[0], f_hem_outer[0]] + fh_curve_x + [f_waist_center[0]]
    y_front = fy_curve + [f_hem_inner[1], f_hem_outer[1]] + fh_curve_y + [f_waist_center[1]]

    # --- BACK PIECE ---
    b_waist_center = (offset, length + (2 if unit=="cm" else 1)) 
    b_waist_side   = (offset + q_waist + 1, length) 
    b_hip_side     = (offset + q_hips + 1, length - crotch_depth)
    b_crotch_pt    = (offset - crotch_ext_b, length - crotch_depth)
    b_hem_outer    = (offset + hem_width + 1, 0)
    b_hem_inner    = (offset, 0)

    # A. Back Rise Curve
    bc_start = b_waist_center
    bc_end = b_crotch_pt
    bc_control = (offset, length - crotch_depth + (crotch_depth/3))
    bx_curve, by_curve = get_curve_points(bc_start, bc_end, bc_control)

    # B. Back Hip Curve
    bh_start = b_hip_side
    bh_end = b_waist_side
    bh_control = (b_hip_side[0], b_waist_side[1])
    bh_curve_x, bh_curve_y = get_curve_points(bh_start, bh_end, bh_control)

    # ASSEMBLE BACK
    x_back = bx_curve + [b_hem_inner[0], b_hem_outer[0]] + bh_curve_x + [b_waist_center[0]]
    y_back = by_curve + [b_hem_inner[1], b_hem_outer[1]] + bh_curve_y + [b_waist_center[1]]

    # --- PLOTTING ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot Front
    ax.plot(x_front, y_front, color='navy', label="Front")
    ax.fill(x_front, y_front, color='lightblue', alpha=0.3)
    
    # Plot Back
    ax.plot(x_back, y_back, color='darkred', label="Back")
    ax.fill(x_back, y_back, color='pink', alpha=0.3)
    
    # Labels
    ax.text(q_waist/2, length/2, "FRONT", ha='center', fontweight='bold')
    ax.text(offset + q_waist/2, length/2, "BACK", ha='center', fontweight='bold')
    
    ax.set_title(f"Pattern for: {name}")
    ax.axis('equal')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)

    # Display in Streamlit
    st.pyplot(fig)

    # Fabric Calc
    st.success("Pattern Generated Successfully!")
    if unit == "cm":
        st.info(f"Estimated Fabric: {(length*2 + 20)/100} Meters")
    else:
        st.info(f"Estimated Fabric: {(length*2 + 8)/36:.2f} Yards")
