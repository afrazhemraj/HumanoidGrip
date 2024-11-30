import json
import matplotlib.pyplot as plt

# Path to the JSON file
json_file_path = "annotations.json"

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Define options for size and shape
sizes = ["small", "medium", "large"]
shapes = ["circular", "rectangular", "other"]

# Initialize counts for size and shape
size_counts = {size: 0 for size in sizes}
shape_counts = {shape: 0 for shape in shapes}

# Count occurrences of each size and shape
for item in data:
    size = item.get("size", "medium")  # Default to "medium" if size is missing
    shape = item.get("shape", "other")  # Default to "other" if shape is missing

    if size in sizes:
        size_counts[size] += 1
    if shape in shapes:
        shape_counts[shape] += 1

# Data preparation for size
size_keys = list(size_counts.keys())
size_values = list(size_counts.values())

# Data preparation for shape
shape_keys = list(shape_counts.keys())
shape_values = list(shape_counts.values())

# Create bar chart for size
plt.figure(figsize=(8, 6))
plt.bar(size_keys, size_values, color='skyblue')
plt.title("Bar Chart for Size")
plt.xlabel("Size")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# Create bar chart for shape
plt.figure(figsize=(8, 6))
plt.bar(shape_keys, shape_values, color='lightcoral')
plt.title("Bar Chart for Shape")
plt.xlabel("Shape")
plt.ylabel("Count")
plt.tight_layout()
plt.show()
