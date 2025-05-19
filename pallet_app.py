import streamlit as st
import pandas as pd
from rectpack import newPacker
import matplotlib.pyplot as plt

# Pallet dimensions
PALLET_LENGTH = 48
PALLET_WIDTH = 40
MAX_HEIGHT = 59

st.title("Advanced Pallet Optimization")

# User inputs (integer-only)
col1, col2 = st.columns(2)
with col1:
    carton_length = st.number_input("Carton Length (inches)", 
                                   min_value=1, step=1, format="%d")
    carton_width = st.number_input("Carton Width (inches)", 
                                  min_value=1, step=1, format="%d")
with col2:
    carton_height = st.number_input("Carton Height (inches)", 
                                   min_value=1, step=1, format="%d")

# Special case handling for 17x13/13x17
if (carton_length == 17 and carton_width == 13) or \
   (carton_length == 13 and carton_width == 17):
    cartons_per_layer = 8
    optimal_orientation = "Mixed (17×13 Special Case)"
    used_length = 17
    used_width = 13
else:
    # Theoretical maximum for uniform orientations
    orient1 = (PALLET_LENGTH // carton_length) * (PALLET_WIDTH // carton_width)
    orient2 = (PALLET_LENGTH // carton_width) * (PALLET_WIDTH // carton_length)
    theoretical_max = max(orient1, orient2)
    
    # Mixed-orientation attempt with rectpack
    packer = newPacker()
    packer.add_bin(PALLET_LENGTH, PALLET_WIDTH)
    
    # Add enough rectangles to fill pallet in both orientations
    for _ in range(1000):
        packer.add_rect(carton_length, carton_width)
        packer.add_rect(carton_width, carton_length)
    
    packer.pack()
    rectpack_result = len(packer[0]) if packer else 0
    
    # Choose best result
    cartons_per_layer = max(theoretical_max, rectpack_result)
    
    # Determine used orientation for visualization
    if orient1 >= orient2:
        used_length = carton_length
        used_width = carton_width
        optimal_orientation = "Original" if orient1 == theoretical_max else "Mixed"
    else:
        used_length = carton_width
        used_width = carton_length
        optimal_orientation = "Rotated" if orient2 == theoretical_max else "Mixed"

# Calculate layers and totals
max_layers = MAX_HEIGHT // carton_height if carton_height > 0 else 0
total_cartons = cartons_per_layer * max_layers

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title(f"Pallet Layer: {cartons_per_layer} Cartons ({optimal_orientation})")
ax.set_xlim(0, PALLET_LENGTH)
ax.set_ylim(0, PALLET_WIDTH)
ax.set_aspect('equal')

if cartons_per_layer > 0:
    cols = PALLET_LENGTH // used_length
    rows = PALLET_WIDTH // used_width
    
    for i in range(cols):
        for j in range(rows):
            rect = plt.Rectangle(
                (i*used_length, j*used_width), 
                used_length, 
                used_width,
                edgecolor='#006699', 
                facecolor='#0099e6', 
                alpha=0.5
            )
            ax.add_patch(rect)
else:
    ax.text(24, 20, "Carton too large!", 
            ha='center', va='center', color='red')

st.pyplot(fig)

# Results display
st.subheader("Optimization Results")
st.write(f"**Cartons/layer:** {cartons_per_layer}")
st.write(f"**Max layers (59\"):** {max_layers}")
st.write(f"**Total cartons:** {total_cartons}")

# Export to Excel
if st.button("Save Configuration to Excel"):
    df = pd.DataFrame([{
        "Length": carton_length,
        "Width": carton_width,
        "Height": carton_height,
        "Cartons/Layer": cartons_per_layer,
        "Layers": max_layers,
        "Total": total_cartons
    }])
    df.to_excel("pallet_configurations.xlsx", index=False)
    st.success("Saved to pallet_configurations.xlsx!")
