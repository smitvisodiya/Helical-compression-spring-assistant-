import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & TITLE
# ==========================================
st.set_page_config(
    page_title="Helical Compression Spring Assistant",
    page_icon="⚙️",
    layout="wide"
)

# Team / Project Information
st.title("⚙️ Helical Compression Spring Design Assistant")
st.markdown("""
**Course:** Diploma in Mechanical Engineering (Semester 3)  
**Topic:** Spring Calculations & 3D Load-Deflection Simulation
""")

# Sidebar for Team Details
st.sidebar.header("👨‍🎓 Group Details")
st.sidebar.markdown("""
**Group No:** 5  
- **Member 1:** [Smit visodiya ] (Enrollment No. 25012250610004)  
- **Member 2:** [Meet rathod] (Enrollment No. 25012250610010)  
- **Member 3:** [Naman dave ] (Enrollment No. 25012250610025)  
""")
st.sidebar.markdown("---")

# ==========================================
# INPUT PARAMETERS (SIDEBAR)
# ==========================================
st.sidebar.header("📥 Input Parameters")

P = st.sidebar.number_input("Axial Load (P) [N]", min_value=1.0, value=500.0, step=10.0)
tau_allow = st.sidebar.number_input("Allowable Shear Stress (τ) [N/mm²]", min_value=10.0, value=350.0, step=10.0)
d = st.sidebar.number_input("Wire Diameter (d) [mm]", min_value=0.5, value=5.0, step=0.5)
D = st.sidebar.number_input("Mean Coil Diameter (D) [mm]", min_value=5.0, value=40.0, step=1.0)
G = st.sidebar.number_input("Modulus of Rigidity (G) [N/mm²]", min_value=1000.0, value=80000.0, step=1000.0, help="For steel, typical G = 79,000 - 81,000 N/mm²")

end_condition = st.sidebar.selectbox(
    "Coil End Condition",
    ["Squared and Ground Ends", "Plain Ends", "Squared Ends", "Plain and Ground Ends"]
)

# Extra coil calculation based on end condition
extra_coils = {
    "Squared and Ground Ends": 2.0,
    "Plain Ends": 0.0,
    "Squared Ends": 2.0,
    "Plain and Ground Ends": 1.0
}[end_condition]

# ==========================================
# VALIDATION CHECKS
# ==========================================
spring_index = D / d

if d >= D:
    st.error("🚨 **Error:** Mean coil diameter (D) must be significantly greater than wire diameter (d).")
    st.stop()

if spring_index < 4 or spring_index > 12:
    st.warning(f"⚠️ **Warning:** Current Spring Index C = {spring_index:.2f}. For optimal mechanical design, C should ideally be between 4 and 12.")

# Wahl Stress Factor Calculation
K = ((4 * spring_index - 1) / (4 * spring_index - 4)) + (0.615 / spring_index)
# Actual Shear Stress
tau_actual = K * ((8 * P * D) / (np.pi * (d ** 3)))

if tau_actual > tau_allow:
    st.error(f"🚨 **Design Unsafe!** Actual Shear Stress ({tau_actual:.2f} N/mm²) exceeds Allowable Shear Stress ({tau_allow:.2f} N/mm²). Increase wire diameter (d) or mean coil diameter (D).")

# ==========================================
# MATHEMATICAL CALCULATIONS
# ==========================================
# 1. Number of Active Coils (N) using Wahl corrected stress limit
# tau = K * (8 * P * D) / (pi * d^3)
# Deflection delta = (8 * P * (D^3) * N) / (G * d^4)
# Solving N from allowable stress:
N = (tau_allow * np.pi * (d**3)) / (K * 8 * P * D) if tau_actual <= tau_allow else (tau_actual * np.pi * (d**3)) / (K * 8 * P * D)
N = max(1.0, float(N))  # Minimum 1 coil

# 2. Total Coils (Nt)
Nt = N + extra_coils

# 3. Spring Stiffness / Rate (k)
k = (G * (d**4)) / (8 * (D**3) * N)

# 4. Maximum Deflection (delta)
delta = P / k

# 5. Solid Length (Ls)
Ls = Nt * d

# 6. Free Length (Lf)
# Free Length = Solid Length + Total Deflection + Clearance (assumed 15% of deflection)
clearance = 0.15 * delta
Lf = Ls + delta + clearance

# ==========================================
# DISPLAY RESULTS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Primary Calculations")
    st.metric("Spring Index (C = D/d)", f"{spring_index:.2f}")
    st.metric("Wahl Factor (K)", f"{K:.3f}")
    st.metric("Actual Stress (τ_act)", f"{tau_actual:.2f} N/mm²", 
              delta=f"{tau_allow - tau_actual:.2f} N/mm² Margin", 
              delta_color="normal" if tau_actual <= tau_allow else "inverse")
    st.metric("Spring Stiffness (k)", f"{k:.2f} N/mm")

with col2:
    st.subheader("📏 Geometry & Length Deliverables")
    st.metric("Active Coils (N)", f"{N:.2f}")
    st.metric("Total Coils (N_t)", f"{Nt:.2f}")
    st.metric("Deflection under Load (δ)", f"{delta:.2f} mm")
    st.metric("Solid Length (L_s)", f"{Ls:.2f} mm")
    st.metric("Free Length (L_f)", f"{Lf:.2f} mm")

st.markdown("---")

# ==========================================
# TABS FOR VISUALIZATIONS & FORMULAS
# ==========================================
tab1, tab2, tab3 = st.tabs(["📉 Load vs. Deflection Plot", "🌀 Interactive 3D Spring Model", "📖 Engineering Formulas"])

# Tab 1: 2D Load vs Deflection Plot
with tab1:
    st.subheader("Load vs. Deflection Characteristic Curve")
    
    deflection_array = np.linspace(0, delta * 1.2, 100)
    load_array = k * deflection_array

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(deflection_array, load_array, color='#1f77b4', linewidth=2.5, label='Spring Performance Line')
    ax.scatter([delta], [P], color='red', s=80, zorder=5, label=f'Design Point (P={P}N, δ={delta:.2f}mm)')
    
    ax.axvline(delta, color='red', linestyle='--', alpha=0.5)
    ax.axhline(P, color='red', linestyle='--', alpha=0.5)
    
    ax.set_title("Load (P) vs Deflection (δ)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Deflection (mm)")
    ax.set_ylabel("Axial Load (N)")
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend()
    
    st.pyplot(fig)

# Tab 2: 3D Spring Interactive Model
with tab2:
    st.subheader("3D Interactive Helical Coil Spring")
    st.markdown("Adjust the slider to simulate the compression of the spring under load in 3D space.")
    
    compression_percent = st.slider("Simulate Applied Load / Compression (%)", 0, 100, 0)
    
    # Calculate compressed height for 3D plot
    current_deflection = (compression_percent / 100.0) * delta
    current_height = max(Ls, Lf - current_deflection)
    
    # Generate helix points
    num_points = 500
    theta = np.linspace(0, 2 * np.pi * Nt, num_points)
    z = np.linspace(0, current_height, num_points)
    r = D / 2.0
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # Plot using Plotly 3D
    fig_3d = go.Figure()
    
    # Main Helix Center Line
    fig_3d.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color='crimson', width=8),
        name='Spring Helix'
    ))

    # Layout styling for 3D plot
    fig_3d.update_layout(
        scene=dict(
            xaxis_title='X (mm)',
            yaxis_title='Y (mm)',
            zaxis_title='Height (mm)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=500
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    st.caption(f"Current Compressed Length: **{current_height:.2f} mm** | Active Deflection: **{current_deflection:.2f} mm**")

# Tab 3: Formula Reference
with tab3:
    st.subheader("📐 Formulas Used in Calculations")
    st.latex(r"C = \frac{D}{d} \quad \text{(Spring Index)}")
    st.latex(r"K = \frac{4C - 1}{4C - 4} + \frac{0.615}{C} \quad \text{(Wahl Stress Factor)}")
    st.latex(r"\tau = K \cdot \frac{8 P D}{\pi d^3} \quad \text{(Shear Stress)}")
    st.latex(r"k = \frac{G \cdot d^4}{8 \cdot D^3 \cdot N} \quad \text{(Spring Stiffness)}")
    st.latex(r"\delta = \frac{P}{k} \quad \text{(Deflection)}")
    st.latex(r"L_s = N_t \cdot d \quad \text{(Solid Length)}")
    st.latex(r"L_f = L_s + \delta + 0.15 \cdot \delta \quad \text{(Free Length)}")
  
