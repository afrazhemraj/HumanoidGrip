import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Path to the JSON file
json_file_path = "annotations.json"

# Load the JSON data
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Define options for size and shape
sizes = ["small", "medium", "large"]
shapes = ["circular", "rectangular", "other"]

# Initialize a matrix to store counts for each size-shape combination
heatmap_data = np.zeros((len(sizes), len(shapes)))

# Count occurrences of each size-shape combination
for item in data:
    size = item.get("size", "medium")  # Default to "medium" if size is missing
    shape = item.get("shape", "other")  # Default to "other" if shape is missing

    if size in sizes and shape in shapes:
        size_idx = sizes.index(size)
        shape_idx = shapes.index(shape)
        heatmap_data[size_idx, shape_idx] += 1

# Create the heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    xticklabels=shapes,
    yticklabels=sizes,
    cmap="Blues"
)
plt.title("Heatmap of Size and Shape")
plt.xlabel("Shape")
plt.ylabel("Size")
plt.tight_layout()
plt.show()
