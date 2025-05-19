import streamlit as st
import pandas as pd
from rectpack import newPacker
import matplotlib.pyplot as plt

# Pallet dimensions
PALLET_L = 48
PALLET_W = 40
MAX_HEIGHT = 59

st.title("Pallet Optimization & Visualizer")

# User inputs
carton_length = st.number_input("Carton Length (inches)", min_value=1)
carton_width = st.number_input("Carton Width (inches)", min_value=1)
carton_height = st.number_input("Carton Height (inches)", min_value=1)

# Calculate cartons per layer
def calculate_capacity(l, w):
    orient1 = (PALLET_L // l) * (PALLET_W // w)
    orient2 = (PALLET_L // w) * (PALLET_W // l)
    return max(orient1, orient2), orient1 >= orient2

# Special case for 17x13 cartons
if (carton_length == 17 and carton_width == 13) or (carton_length == 13 and carton_width == 17):
    cartons_per_layer = 8
    use_original = False
else:
    cartons_per_layer, use_original = calculate_capacity(carton_length, carton_width)

# Calculate layers and total
max_layers = MAX_HEIGHT // carton_height if carton_height > 0 else 0
total_cartons = cartons_per_layer * max_layers

# Visualization
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title(f"Pallet Layer: {cartons_per_layer} Cartons")
ax.set_xlim(0, PALLET_L)
ax.set_ylim(0, PALLET_W)
ax.set_aspect('equal')

if cartons_per_layer > 0:
    used_l = carton_length if use_original else carton_width
    used_w = carton_width if use_original else carton_length
    
    for i in range(PALLET_L // used_l):
        for j in range(PALLET_W // used_w):
            rect = plt.Rectangle(
                (i*used_l, j*used_w), used_l, used_w,
                edgecolor='#006699', facecolor='#0099e6', alpha=0.5
            )
            ax.add_patch(rect)
else:
    ax.text(24, 20, "Carton too large!", ha='center', va='center', color='red')

st.pyplot(fig)
st.subheader("Results")
st.write(f"Cartons/layer: **{cartons_per_layer}**")
st.write(f"Max layers (59\"): **{max_layers}**")
st.write(f"Total cartons: **{total_cartons}**")
