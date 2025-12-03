import streamlit as st
import matplotlib.pyplot as plt

# --- HELPER: MATH FOR CURVES (Exact same as before) ---
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

# --- THE ENGINE ---
def generate_plot(waist, hips, length, unit):
    # 1. Define Constants
    if unit == "cm":
        hip_depth = 20.0
        hem_flare = 5.0
        sa = 1.0
        label_sa = "1cm"
    else: # inches
        hip_depth = 8.0
        hem_flare = 2.0
        sa = 0.5
        label_sa = "1/2 inch"

    q_waist = waist / 4
    q_hips = hips / 4
    
    # Sew Line
    s_waist = (q_waist, 0)
    s_hip = (q_hips, -hip_depth)
    s_hem = (q_hips + hem_flare, -length)
    s_control = (q_hips, -hip_depth / 3) 
    s_curve_x, s_curve_y = get_curve_points(s_waist, s_hip, s_control)
    x_sew = [0] + s_curve_x + [s_hem[0], 0, 0]
    y_sew = [0] + s_curve_y + [s_hem[1], -length, 0]
    
    # Cut Line
    c_waist = (q_waist + sa, sa)
    c_hip = (q_hips + sa, -hip_depth)
    c_hem = (q_hips + hem_flare + sa, -length - sa)
    c_control = (q_hips + sa, -hip_depth / 3)
    c_curve_x, c_curve_y = get_curve_points(c_waist, c_hip, c_control)
    x_cut = [0] + c_curve_x + [c_hem[0], 0, 0]
    y_cut = [sa] + c_curve_y + [c_hem[1], -length - sa, sa]

    # Plot
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.plot(x_cut, y_cut, color='red', linestyle='--', label=f"Cut Line ({label_sa})")
    ax.plot(x_sew, y_sew, color='black', linewidth=2, label="Sew Line")
    ax.fill(x_sew, y_sew, color='pink', alpha=0.2)
    ax.axis('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    ax.set_title(f"Pattern Preview ({unit})")
    
    return fig

def calculate_fabric(length, hips, unit):
    if unit == "cm":
        width_std = 140
        needed = length + 10
        if hips + 10 < width_std: return f"{needed/100} Meters (Single Width)"
        else: return f"{(needed*2)/100} Meters (Double Width)"
    else:
        width_std = 58
        needed = length + 4
        if hips + 4 < width_std: return f"{needed/36:.2f} Yards (Single Width)"
        else: return f"{(needed*2)/36:.2f} Yards (Double Width)"

# --- THE WEB INTERFACE (Streamlit) ---
st.title("🧵 Global Fashion Studio")
st.write("Generate custom garment patterns instantly.")

# Sidebar for inputs
st.sidebar.header("Measurements")
unit = st.sidebar.radio("Select Unit:", ["cm", "inch"])

if unit == "cm":
    waist = st.sidebar.number_input("Waist (cm)", value=70.0)
    hips = st.sidebar.number_input("Hips (cm)", value=98.0)
    length = st.sidebar.number_input("Length (cm)", value=60.0)
else:
    waist = st.sidebar.number_input("Waist (inch)", value=28.0)
    hips = st.sidebar.number_input("Hips (inch)", value=38.0)
    length = st.sidebar.number_input("Length (inch)", value=24.0)

client_name = st.sidebar.text_input("Client Name", value="MyClient")

# Main Screen Actions
if st.sidebar.button("Generate Pattern"):
    # 1. Calculate Fabric
    fabric = calculate_fabric(length, hips, unit)
    st.success(f"Fabric Required: **{fabric}**")
    
    # 2. Draw Plot
    fig = generate_plot(waist, hips, length, unit)
    st.pyplot(fig)
    
    # 3. Create PDF Download Button
    fn = f"{client_name}_pattern.pdf"
    fig.savefig(fn)
    with open(fn, "rb") as file:
        btn = st.download_button(
            label="Download PDF Pattern",
            data=file,
            file_name=fn,
            mime="application/pdf"
        )
