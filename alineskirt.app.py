import streamlit as st
import matplotlib.pyplot as plt

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="Production Pattern Generator", layout="wide")
st.title("✂️ Production Pants Pattern Generator")
st.write("Generates Front/Back blocks, Waistband, Pocket Bag, and Fabric Estimates.")

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("Measurements")
unit = st.sidebar.radio("Select Unit:", ["cm", "inches"])

# Defaults based on unit
if unit == "cm":
    def_w, def_h, def_l = 76.0, 100.0, 100.0
    wb_height = 4.0
    pocket_open = 14.0
    dart_w_f, dart_w_b = 2.0, 3.0
else:
    def_w, def_h, def_l = 30.0, 40.0, 40.0
    wb_height = 1.5
    pocket_open = 5.5
    dart_w_f, dart_w_b = 0.75, 1.25

waist = st.sidebar.number_input("Waist", value=def_w)
hips = st.sidebar.number_input("Hips", value=def_h)
length = st.sidebar.number_input("Length", value=def_l)
client_name = st.sidebar.text_input("Client Name", "Client A")

# --- 3. HELPER FUNCTIONS ---

def get_curve(start, end, control, res=20):
    """Calculates Bezier curve points"""
    px, py = [], []
    for i in range(res + 1):
        t = i / res
        x = (1 - t)**2 * start[0] + 2 * (1 - t) * t * control[0] + t**2 * end[0]
        y = (1 - t)**2 * start[1] + 2 * (1 - t) * t * control[1] + t**2 * end[1]
        px.append(x)
        py.append(y)
    return px, py

def calculate_fabric(length, hips, unit):
    """Estimates fabric usage"""
    if unit == "cm":
        width_std = 140 # Standard fabric width in cm
        # Rule of thumb: length * 2 + extra for waistbands/pockets
        needed = (length * 2) + 20
        # If hips are very wide, we might need even more width or length layout
        return f"{needed/100:.2f} Meters"
    else:
        width_std = 58 # Standard fabric width in inches
        needed = (length * 2) + 8
        return f"{needed/36:.2f} Yards"

# --- 4. MAIN GENERATION ENGINE ---
if st.button("Generate Full Pattern"):
    
    # --- A. CALCULATIONS ---
    crotch_depth = hips / 4
    
    # Quarter measurements (Back > Front for fit)
    q_hip_f = (hips / 4) - 1 if unit == "cm" else (hips/4) - 0.5
    q_hip_b = (hips / 4) + 1 if unit == "cm" else (hips/4) + 0.5
    
    # Waist calculations (Target/4 + Dart Allowance)
    w_f = (waist / 4) - 1 + dart_w_f if unit == "cm" else (waist/4) - 0.5 + dart_w_f
    w_b = (waist / 4) + 1 + dart_w_b if unit == "cm" else (waist/4) + 0.5 + dart_w_b
    
    # Crotch Extensions
    ext_f = hips / 16
    ext_b = hips / 8
    
    # Pocket Dimensions
    p_width = 4.0 if unit == "cm" else 1.5  # distance from side seam
    p_depth = pocket_open # distance down side seam

    # --- B. FRONT PIECE ---
    f_cf_waist = (0, 0)
    f_crotch_level = (0, -crotch_depth)
    f_crotch_tip = (-ext_f, -crotch_depth)
    f_hem_in = (0, -length)
    f_hem_out = (q_hip_f, -length)
    f_hip_pt = (q_hip_f, -crotch_depth)
    
    # Pocket Cutout
    f_waist_side_raw = (w_f, 0)
    f_pocket_top = (w_f - p_width, 0) # Top of slant
    f_pocket_bot = (q_hip_f, -p_depth) # Bottom of slant

    # Front Dart
    d_center_x = f_pocket_top[0] / 2
    d_len = 8.0 if unit=="cm" else 3.5
    dart_f = [
        (d_center_x - dart_w_f/2, 0),
        (d_center_x, -d_len),
        (d_center_x + dart_w_f/2, 0)
    ]

    # Front Curves
    cx, cy = get_curve(f_cf_waist, f_crotch_tip, (0, -crotch_depth/2))
    # Note: Hip/Pocket curve is now part of the pocket slant
    
    # Assemble Front Polygon
    x_front = [0] + cx + [f_hem_in[0], f_hem_out[0], f_hip_pt[0]] + [f_pocket_bot[0], f_pocket_top[0]] + [dart_f[2][0], dart_f[1][0], dart_f[0][0]] + [0]
    y_front = [0] + cy + [f_hem_in[1], f_hem_out[1], f_hip_pt[1]] + [f_pocket_bot[1], f_pocket_top[1]] + [dart_f[2][1], dart_f[1][1], dart_f[0][1]] + [0]

    # --- C. BACK PIECE ---
    offset = (hips/2) + (15 if unit == "cm" else 6) # Spacing between pieces
    
    b_cb_waist = (offset, 2 if unit=="cm" else 1) # Raised back rise
    b_crotch_tip = (offset - ext_b, -crotch_depth)
    b_hem_in = (offset, -length)
    b_hem_out = (offset + q_hip_b, -length)
    b_hip_pt = (offset + q_hip_b, -crotch_depth)
    b_waist_side = (offset + w_b, 0)
    
    # Back Dart
    bd_center_x = offset + (w_b / 2)
    bd_len = 10.0 if unit=="cm" else 4.0
    dart_b = [
        (bd_center_x - dart_w_b/2, (b_cb_waist[1] + b_waist_side[1])/2 ),
        (bd_center_x, -bd_len),
        (bd_center_x + dart_w_b/2, (b_cb_waist[1] + b_waist_side[1])/2 )
    ]

    # Back Curves
    bcx, bcy = get_curve(b_cb_waist, b_crotch_tip, (offset, -crotch_depth/2))
    bhx, bhy = get_curve(b_hip_pt, b_waist_side, (b_hip_pt[0], b_waist_side[1]))

    # Assemble Back Polygon
    x_back = [b_cb_waist[0]] + bcx + [b_hem_in[0], b_hem_out[0]] + bhx + [dart_b[2][0], dart_b[1][0], dart_b[0][0]] + [b_cb_waist[0]]
    y_back = [b_cb_waist[1]] + bcy + [b_hem_in[1], b_hem_out[1]] + bhy + [dart_b[2][1], dart_b[1][1], dart_b[0][1]] + [b_cb_waist[1]]

    # --- D. EXTRAS (Waistband & Pocket Bag) ---
    # Waistband
    wb_y_start = -length - (10 if unit=="cm" else 4)
    wb_len = waist + 5 
    x_wb = [0, wb_len, wb_len, 0, 0]
    y_wb = [wb_y_start, wb_y_start, wb_y_start - wb_height, wb_y_start - wb_height, wb_y_start]

    # Pocket Bag
    pb_x_offset = q_hip_f + (10 if unit=="cm" else 4)
    pb_y_start = -5 
    pb_w = 16 if unit=="cm" else 7
    pb_h = 28 if unit=="cm" else 11
    x_pb = [pb_x_offset, pb_x_offset + pb_w, pb_x_offset + pb_w, pb_x_offset, pb_x_offset]
    y_pb = [pb_y_start, pb_y_start, pb_y_start - pb_h, pb_y_start - pb_h, pb_y_start]

    # --- E. PLOTTING ---
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Plot Front
    ax.plot(x_front, y_front, 'k-', label="Front")
    ax.fill(x_front, y_front, 'skyblue', alpha=0.3)
    ax.text(q_hip_f/2, -length/2, "FRONT\n(Cut 2)", ha='center')
    
    # Plot Back
    ax.plot(x_back, y_back, 'k-', label="Back")
    ax.fill(x_back, y_back, 'pink', alpha=0.3)
    ax.text(offset + q_hip_b/2, -length/2, "BACK\n(Cut 2)", ha='center')
    
    # Plot Waistband
    ax.plot(x_wb, y_wb, 'g-', label="Waistband")
    ax.text(wb_len/2, wb_y_start - wb_height/2, f"WAISTBAND\nL:{wb_len:.1f}", ha='center', va='center')
    
    # Plot Pocket Bag
    ax.plot(x_pb, y_pb, 'b--', label="Pocket Bag")
    ax.text(pb_x_offset + pb_w/2, pb_y_start - pb_h/2, "POCKET\nBAG", ha='center')

    ax.set_title(f"Production Pattern: {client_name} (Unit: {unit})")
    ax.axis('equal')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.5)

    # 1. Show Plot
    st.pyplot(fig)
    
    # 2. Fabric Calculation
    est_fabric = calculate_fabric(length, hips, unit)
    st.success(f"📏 Estimated Fabric Required: **{est_fabric}** (assuming standard width)")

    # 3. PDF Download Button
    fn = f"{client_name}_pattern.pdf"
    fig.savefig(fn)
    
    with open(fn, "rb") as pdf_file:
        st.download_button(
            label="📄 Download Pattern as PDF",
            data=pdf_file,
            file_name=fn,
            mime="application/pdf"
        )
