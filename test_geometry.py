from geometry import (
    estimate_cylinder,
    estimate_cuboid,
    estimate_sphere,
    estimate_ellipsoid,
    diameter_to_radius,
    DENSITY_TABLE
)

# Round khobz: 15cm diameter, 3cm height
radius = diameter_to_radius(15)
mass = estimate_cylinder(radius, 3, DENSITY_TABLE["khobz"])
print(f"Round khobz (15cm diameter, 3cm high): {mass}g")

# Slice of bread: 10cm x 10cm x 1.5cm
mass = estimate_cuboid(10, 10, 1.5, DENSITY_TABLE["white_bread"])
print(f"Bread slice (10x10x1.5cm): {mass}g")

# Apple: radius 4cm
mass = estimate_sphere(4, DENSITY_TABLE["apple"])
print(f"Apple (4cm radius): {mass}g")

# Egg: semi-axes 2.2cm, 2.2cm, 3cm
mass = estimate_ellipsoid(2.2, 2.2, 3, DENSITY_TABLE["egg"])
print(f"Egg (2.2 x 2.2 x 3cm): {mass}g")