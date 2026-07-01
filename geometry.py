import math

def estimate_cylinder(radius_cm, height_cm, density_g_per_cm3):
    """
    Estimates mass of a cylindrical food item.
    Examples: bread roll, glass of liquid, round cake
    """
    volume = math.pi * (radius_cm ** 2) * height_cm
    mass_g = volume * density_g_per_cm3
    return round(mass_g, 2)

def estimate_cuboid(length_cm, width_cm, height_cm, density_g_per_cm3):
    """
    Estimates mass of a rectangular food item.
    Examples: sliced bread, brownie, cheese slice
    """
    volume = length_cm * width_cm * height_cm
    mass_g = volume * density_g_per_cm3
    return round(mass_g, 2)

def estimate_sphere(radius_cm, density_g_per_cm3):
    """
    Estimates mass of a spherical food item.
    Examples: apple, orange, meatball
    """
    volume = (4/3) * math.pi * (radius_cm ** 3)
    mass_g = volume * density_g_per_cm3
    return round(mass_g, 2)

def estimate_cone(radius_cm, height_cm, density_g_per_cm3):
    """
    Estimates mass of a cone-shaped food item.
    Examples: ice cream scoop cone, conical pastry
    """
    volume = (1/3) * math.pi * (radius_cm ** 2) * height_cm
    mass_g = volume * density_g_per_cm3
    return round(mass_g, 2)

def estimate_ellipsoid(a_cm, b_cm, c_cm, density_g_per_cm3):
    """
    Estimates mass of an ellipsoid food item.
    Examples: egg, mango, avocado, potato
    a, b, c = the three semi-axes (half-lengths in each direction)
    """
    volume = (4/3) * math.pi * a_cm * b_cm * c_cm
    mass_g = volume * density_g_per_cm3
    return round(mass_g, 2)

def diameter_to_radius(diameter_cm):
    """
    Helper: converts diameter to radius.
    Useful since most people measure diameter, not radius.
    """
    return diameter_cm / 2


DENSITY_TABLE = {
    "white_bread": 0.25,
    "khobz": 0.30,
    "banana": 0.94,
    "apple": 0.77,
    "orange": 0.84,
    "chicken_breast_raw": 1.02,
    "rice_cooked": 0.90,
    "olive_oil": 0.91,
    "water": 1.00,
    "egg": 1.03,
    "avocado": 0.67,
    "potato_raw": 1.05,
}