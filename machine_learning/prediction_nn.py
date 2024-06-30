"""
Predicts a price based on input features.

Author: Elias Eschenauer
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import numpy as np
import pandas as pd
import joblib
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------------------------
# Load the trained model (either from a file or by retraining)
# --------------------------------------------------------------------
model_final = joblib.load('nn_model.pkl')
scaler = joblib.load('scaler.pkl')

# --------------------------------------------------------------------
# Function to predict price
# --------------------------------------------------------------------
def predict_price():
    try:
        platform = platform_var.get()
        neighbourhood_id = int(neighbourhood_var.get())
        room_type = room_type_var.get()  # Retrieve the room type as a string

        # Mapping for room type to numeric value
        room_type_mapping = {
            'Entire home/apt': 1,
            'Private room': 2,
            'Shared room': 3,
            'Hotel room': 4
        }
        room_type_id = room_type_mapping[room_type]  # Get the corresponding numeric ID

        # Dictionary for amenities
        amenities_dict = {
            "kitchen": int(kitchen_var.get()),
            "tv": int(tv_var.get()),
            "wifi": int(wifi_var.get()),
            "gym": int(gym_var.get()),
            "elevator": int(elevator_var.get()),
            "fridge": int(fridge_var.get()),
            "heating": int(heating_var.get()),
            "hair_dryer": int(hair_dryer_var.get()),
            "air_conditioning": int(air_conditioning_var.get()),
            "hot_tub": int(hot_tub_var.get()),
            "oven": int(oven_var.get()),
            "bbq": int(bbq_var.get()),
            "coffee": int(coffee_var.get()),
            "pool": int(pool_var.get()),
            "balcony": int(balcony_var.get()),
            "furniture": int(furniture_var.get()),
            "microwave": int(microwave_var.get())
        }

        beds = int(beds_var.get())
        accommodates = int(accommodates_var.get())
        bathrooms = int(bathrooms_var.get())
        bedrooms = int(bedrooms_var.get())

        # Combine all variables into a dictionary
        data_dict = {
            "platform": platform,
            "neighbourhood_id": neighbourhood_id,
            "room_type_id": room_type_id,
            **amenities_dict,
            "beds": beds,
            "accommodates": accommodates,
            "bathrooms": bathrooms,
            "bedrooms": bedrooms
        }

        # Create a DataFrame
        input_features = pd.DataFrame([data_dict])

        # Scale the input features
        input_features_scaled = scaler.transform(input_features)  # Use the same scaler as during training

        # Prediction
        predicted_log_price = model_final.predict(input_features_scaled)
        predicted_price = np.expm1(predicted_log_price)[0]  # Convert back from log space
        predicted_price = float(predicted_price)  # Convert NumPy float to Python float

        messagebox.showinfo("Predicted Price", f"Predicted Price: {predicted_price:.2f} € pro Nacht")


    except Exception as e:
        messagebox.showerror("Error", str(e))

# --------------------------------------------------------------------
# GUI setup
# --------------------------------------------------------------------
root = tk.Tk()
root.title("Price Prediction")

# Platform
tk.Label(root, text="Platform").grid(row=0, column=0, sticky=tk.W)
platform_var = tk.IntVar(value=1)
ttk.Radiobutton(root, text="Airbnb", variable=platform_var, value=0).grid(row=0, column=1, sticky=tk.W)
ttk.Radiobutton(root, text="Booking.com", variable=platform_var, value=1).grid(row=0, column=2, sticky=tk.W)

# Neighbourhood ID
tk.Label(root, text="Neighbourhood ID (1-23)").grid(row=1, column=0, sticky=tk.W)
neighbourhood_var = tk.IntVar()
ttk.Combobox(root, textvariable=neighbourhood_var, values=list(range(1, 24))).grid(row=1, column=1)

# Room Type
tk.Label(root, text="Room Type").grid(row=2, column=0, sticky=tk.W)
room_type_var = tk.StringVar()
room_type_mapping = {
    'Entire home/apt': 1,
    'Private room': 2,
    'Shared room': 3,
    'Hotel room': 4
}
ttk.Combobox(root, textvariable=room_type_var, values=list(room_type_mapping.keys())).grid(row=2, column=1)

# Amenities
amenities = {
    "kitchen": "Kitchen",
    "tv": "TV",
    "wifi": "WiFi",
    "gym": "Gym",
    "elevator": "Elevator",
    "fridge": "Fridge",
    "heating": "Heating",
    "hair_dryer": "Hair Dryer",
    "air_conditioning": "Air Conditioning",
    "hot_tub": "Hot Tub",
    "oven": "Oven",
    "bbq": "BBQ",
    "coffee": "Coffee",
    "pool": "Pool",
    "balcony": "Balcony",
    "furniture": "Furniture",
    "microwave": "Microwave"
}

amenities_vars = {}
row = 3
for amenity, text in amenities.items():
    tk.Label(root, text=text).grid(row=row, column=0, sticky=tk.W)
    var = tk.IntVar()
    tk.Checkbutton(root, variable=var).grid(row=row, column=1)
    amenities_vars[amenity] = var
    row += 1

kitchen_var = amenities_vars["kitchen"]
tv_var = amenities_vars["tv"]
wifi_var = amenities_vars["wifi"]
gym_var = amenities_vars["gym"]
elevator_var = amenities_vars["elevator"]
fridge_var = amenities_vars["fridge"]
heating_var = amenities_vars["heating"]
hair_dryer_var = amenities_vars["hair_dryer"]
air_conditioning_var = amenities_vars["air_conditioning"]
hot_tub_var = amenities_vars["hot_tub"]
oven_var = amenities_vars["oven"]
bbq_var = amenities_vars["bbq"]
coffee_var = amenities_vars["coffee"]
pool_var = amenities_vars["pool"]
balcony_var = amenities_vars["balcony"]
furniture_var = amenities_vars["furniture"]
microwave_var = amenities_vars["microwave"]

# Beds
tk.Label(root, text="Beds").grid(row=row, column=0, sticky=tk.W)
beds_var = tk.IntVar(value=1)
ttk.Spinbox(root, from_=1, to=10, textvariable=beds_var).grid(row=row, column=1)
row += 1

# Accommodates
tk.Label(root, text="Accommodates").grid(row=row, column=0, sticky=tk.W)
accommodates_var = tk.IntVar(value=1)
ttk.Spinbox(root, from_=1, to=10, textvariable=accommodates_var).grid(row=row, column=1)
row += 1

# Bathrooms
tk.Label(root, text="Bathrooms").grid(row=row, column=0, sticky=tk.W)
bathrooms_var = tk.IntVar(value=1)
ttk.Spinbox(root, from_=1, to=10, textvariable=bathrooms_var).grid(row=row, column=1)
row += 1

# Bedrooms
tk.Label(root, text="Bedrooms").grid(row=row, column=0, sticky=tk.W)
bedrooms_var = tk.IntVar(value=1)
ttk.Spinbox(root, from_=1, to=10, textvariable=bedrooms_var).grid(row=row, column=1)
row += 1

# Predict Button
ttk.Button(root, text="Predict Price", command=predict_price).grid(row=row, column=0, columnspan=2)

# Run the GUI event loop
root.mainloop()
