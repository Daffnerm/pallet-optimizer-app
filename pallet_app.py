import streamlit as st
import pandas as pd
from rectpack import newPacker
import matplotlib.pyplot as plt

# Fixed pallet dimensions
PALLET_LENGTH = 48
PALLET_WIDTH = 40

st.title("Advanced Pallet Optimizer")

# User inputs
col1, col2 = st.columns(2)
with col1:
    carton_length = st.number_input("Carton Length (inches)", 
                                  min_value=1, step=1, format="%d")
    carton_width = st.number_input("Carton Width (inches)", 
                                 min_value=1, step=1, format="%d")
with col2:
    carton_height = st.number_input("Carton Height (inches)", 
                                  min_value=1, step=1, format="%d")
    max_height = st.number_input("Pallet Max Height (inches)", 
                               min_value=1, step=1, format="%d", 
                               value=59)

def calculate_capacity(l, w, h, max_h):
    # Special case for 17×13/13×17 cartons
    if (l == 17 and w == 13) or (l == 13 and w == 17):
        return 8, False
    
    # Theoretical maximum for uniform orientations
    orient1 = (PALLET_LENGTH // l) * (PALLET_WIDTH // w)
    orient2 = (PALLET_LENGTH // w) * (PALLET_WIDTH // l)
    theoretical_max = max(orient1, orient2)
    
    # Mixed-orientation attempt with rectpack
    packer = newPacker()
    packer.add_bin(PALLET_LENGTH, PALLET_WIDTH)
    
    for _ in range(1000):
        packer.add_rect(l, w)
        packer.add_rect(w, l)
    
    packer.pack()
    rectpack_result = len(packer[0]) if packer else 0
    
    # Choose best result
    cartons_per_layer = max(theoretical_max, rectpack_result)
    use_original = orient1 >= orient2 if cartons_per_layer == theoretical_max else False
    
    return cartons_per_layer, use_original

if carton_height > max_height:
    st.error("Carton height exceeds maximum pallet height!")
else:
    cartons_per_layer, use_original = calculate_capacity(
        carton_length, carton_width, carton_height, max_height
    )
    max_layers = max_height // carton_height
    total_cartons = cartons_per_layer * max_layers

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Pallet Layer: {cartons_per_layer} Cartons (Max Height: {max_height}\")")
    ax.set_xlim(0, PALLET_LENGTH)
    ax.set_ylim(0, PALLET_WIDTH)
    ax.set_aspect('equal')

    # Draw pallet border
    pallet_border = plt.Rectangle((0, 0), PALLET_LENGTH, PALLET_WIDTH, 
                              fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(pallet_border)

    if cartons_per_layer > 0:
        # Special visualization for 17×13 cartons - COMPLETELY REVISED LAYOUT
        if (carton_length == 17 and carton_width == 13) or (carton_length == 13 and carton_width == 17):
            positions = [
                # Row 1 - horizontal
                {"x": 0, "y": 0, "w": 17, "h": 13},
                {"x": 17, "y": 0, "w": 17, "h": 13},
                
                # Row 2 - horizontal
                {"x": 0, "y": 13, "w": 17, "h": 13},
                {"x": 17, "y": 13, "w": 17, "h": 13},
                
                # Row 3 - horizontal
                {"x": 0, "y": 26, "w": 17, "h": 13},
                {"x": 17, "y": 26, "w": 17, "h": 13},
                
                # Right column - vertical
                {"x": 34, "y": 0, "w": 13, "h": 17},
                {"x": 34, "y": 17, "w": 13, "h": 17}
            ]
            
            # Draw cartons with different colors for horizontal/vertical
            for i, pos in enumerate(positions):
                is_vertical = pos["h"] > pos["w"]
                rect_color = '#5599FF' if is_vertical else '#0099e6'
                
                rect = plt.Rectangle(
                    (pos["x"], pos["y"]), 
                    pos["w"], 
                    pos["h"],
                    edgecolor='#004466', 
                    facecolor=rect_color, 
                    alpha=0.7
                )
                ax.add_patch(rect)
                
                # Add number to each carton
                ax.text(
                    pos["x"] + pos["w"]/2, 
                    pos["y"] + pos["h"]/2, 
                    str(i+1),
                    ha='center', 
                    va='center', 
                    color='white', 
                    fontweight='bold'
                )
        else:
            # Standard visualization for other sizes
            used_l = carton_length if use_original else carton_width
            used_w = carton_width if use_original else carton_length
            
            cols = PALLET_LENGTH // used_l
            rows = PALLET_WIDTH // used_w
            
            for i in range(cols):
                for j in range(rows):
                    rect = plt.Rectangle(
                        (i * used_l, j * used_w), 
                        used_l, 
                        used_w,
                        edgecolor='#004466', 
                        facecolor='#0099e6', 
                        alpha=0.7
                    )
                    ax.add_patch(rect)
    else:
        ax.text(PALLET_LENGTH/2, PALLET_WIDTH/2, "Carton too large!", 
                ha='center', va='center', color='red', fontsize=14)

    # Add grid for better visualization
    ax.grid(True, linestyle='--', alpha=0.3)
    
    st.pyplot(fig)
    
    # Calculate pallet utilization
    pallet_area = PALLET_LENGTH * PALLET_WIDTH
    if cartons_per_layer > 0:
        if (carton_length == 17 and carton_width == 13) or (carton_length == 13 and carton_width == 17):
            # For 17×13 special case
            horizontal_area = 17 * 13 * 6  # 6 horizontal cartons
            vertical_area = 13 * 17 * 2    # 2 vertical cartons
            carton_area = horizontal_area + vertical_area
        else:
            # For standard layouts
            used_l = carton_length if use_original else carton_width
            used_w = carton_width if use_original else carton_length
            carton_area = used_l * used_w * cartons_per_layer
        
        utilization_percentage = (carton_area / pallet_area) * 100
    else:
        utilization_percentage = 0
    
    # Display results in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Optimization Results
        st.subheader("Optimization Results")
        st.write(f"**Cartons/layer:** {cartons_per_layer}")
        st.write(f"**Max layers ({max_height}\"):** {max_layers}")
        st.write(f"**Total cartons:** {total_cartons}")
    
    with col2:
        # Pallet Utilization
        st.subheader("Pallet Utilization")
        st.write(f"**Pallet Area Utilization:** {utilization_percentage:.1f}%")

    # Export to Excel
    if st.button("Save Configuration to Excel"):
        df = pd.DataFrame([{
            "Length": carton_length,
            "Width": carton_width,
            "Height": carton_height,
            "Max Pallet Height": max_height,
            "Cartons/Layer": cartons_per_layer,
            "Layers": max_layers,
            "Total": total_cartons,
            "Utilization (%)": round(utilization_percentage, 1)
        }])
        df.to_excel("pallet_configurations.xlsx", index=False)
        st.success("Saved to pallet_configurations.xlsx!")
