import math

# =================================================================================================================================
# EXTRACT GEOMETRY DATA USING IFC CLASSES / PROPERTIES
# =================================================================================================================================

# Function to extract geometry quantities like volume, area, and dimensions from IfcElementQuantity
# This only uses IFC entities and Psets (no COMPAS)
def quantities_ifc(element, property_relationships, lc_factor):
    quantities = {
        "Width": "Not defined",
        "Width unit": "METRE",
        "Length": "Not defined",
        "Length unit": "METRE",
        "Height": "Not defined",
        "Height unit": "METRE",
        "Gross Side Area": "Not defined",
        "Gross Side Area unit": "SQUARE_METRE",
        "Net Side Area": "Not defined",
        "Net Side Area unit": "SQUARE_METRE",
        "Gross Footprint Area": "Not defined",
        "Gross Footprint Area unit": "SQUARE_METRE",
        "Net Footprint Area": "Not defined",
        "Net Footprint Area unit": "SQUARE_METRE",
        "Gross Volume": "Not defined",
        "Gross Volume unit": "CUBIC_METRE",
        "Net Volume": "Not defined",
        "Net Volume unit": "CUBIC_METRE"
    }

    try:

        for rel in property_relationships:
            if element in rel.RelatedObjects:
                if hasattr(rel, "RelatingPropertyDefinition") and rel.RelatingPropertyDefinition:
                    quantity_set = rel.RelatingPropertyDefinition
                    
                    # Check if the property is of type IfcElementQuantity and has quantities
                    if quantity_set.is_a("IfcElementQuantity") and hasattr(quantity_set, "Quantities"):
                        for quantity in quantity_set.Quantities:
                            if hasattr(quantity, "Name"):
                                q_name = quantity.Name.lower()  # Normalize for comparison

                                # Extract volume values
                                if "volume" in q_name and hasattr(quantity, "VolumeValue"):
                                    if "gross" in q_name:
                                        quantities["Gross Volume"] = round(quantity.VolumeValue, 4)
                                    elif "net" in q_name:
                                        quantities["Net Volume"] = round(quantity.VolumeValue, 4)

                                # Extract area values
                                elif "area" in q_name and hasattr(quantity, "AreaValue"):
                                    if "grossside" in q_name:
                                        quantities["Gross Side Area"] = round(quantity.AreaValue, 4)
                                    elif "netside" in q_name:
                                        quantities["Net Side Area"] = round(quantity.AreaValue, 4)
                                    elif "grossfootprint" in q_name:
                                        quantities["Gross Footprint Area"] = round(quantity.AreaValue, 4)
                                    elif "netfootprint" in q_name:
                                        quantities["Net Footprint Area"] = round(quantity.AreaValue, 4)

                                # Extract length values and apply conversion factor
                                elif "length" in q_name and hasattr(quantity, "LengthValue"):
                                    quantities["Length"] = round((lc_factor * quantity.LengthValue), 4)
                                elif "width" in q_name and hasattr(quantity, "LengthValue"):
                                    quantities["Width"] = round((lc_factor * quantity.LengthValue), 4)
                                elif "height" in q_name and hasattr(quantity, "LengthValue"):
                                    quantities["Height"] = round((lc_factor * quantity.LengthValue), 4)
    except Exception as e:
        pass
    # Clean up unused fields
    cleaned_quantities = {
        k: v for k, v in quantities.items()
        if v != "Not defined" and not (
            k.endswith("unit") and quantities.get(k.replace(" unit", "")) == "Not defined"
        )
    }
    return cleaned_quantities if cleaned_quantities else {}

# Function to extract geometric representation type(s) from IfcProduct
def representation(element):
    try:
        if hasattr(element, "Representation") and element.Representation:
            representations = element.Representation.Representations
            if representations:
                geometry_types = {repr.RepresentationType for repr in representations if hasattr(repr, "RepresentationType")}
                return list(geometry_types) if geometry_types else "Not defined"
    except Exception as e:
        pass
    return "Not defined"



# =================================================================================================================================
# EXTRACT GEOMETRY DATA USING COMPAS
# =================================================================================================================================


# Method to convert element to mesh
def get_mesh(element):
    brep = element.geometry
    try:
        mesh, polylines = brep.to_viewmesh(linear_deflection=0.001)
        obb = mesh.obb()
        return mesh, obb
    except Exception as e:
        return None, None


def quantities_compas(brep, lc_factor):
    quantities = {}
    try:
        if brep is not None:
            volume = brep.volume * (lc_factor ** 3)
            if volume is not None:
                quantities["Net Volume"] = round(volume, 4)
                quantities["Net Volume unit"] = "CUBIC_METRE"
            area = brep.area * (lc_factor ** 2)
            if area is not None:
                quantities["Entire Surface Area"] = round(area, 4)
                quantities["Entire Surface Area unit"] = "SQUARE_METRE"
    except AttributeError:
        pass
    return quantities if quantities else {}

# Method to get tessellation counts (i.e., describing the complexity of the mesh)
def face_count(mesh):
    try:
        return {
            "Face Count": len(list(mesh.faces()))
        }
    except Exception:
        return {}

# Method to get tessellation counts (i.e., describing the complexity of the mesh)
def vertex_count(mesh):
    try:
        return {
            "Vertex Count": len(list(mesh.vertices()))
        }
    except Exception:
        return {}
    
# Method to get tessellation counts (i.e., describing the complexity of the mesh)
def edge_count(mesh):
    try:
        return {
            "Edge Count": len(list(mesh.edges()))
        }
    except Exception:
        return {}


# Bounding box dimensions with dominant axis handling
def bounding_box_dimensions(obb, length_conversion_factor):
    if obb is None:
        return {}

    try:
        xaxis, yaxis, zaxis = obb.frame.xaxis, obb.frame.yaxis, obb.frame.zaxis

        # Find the dominant axis (the one most aligned with global Z)
        dominant_axis = max(
            [("X", abs(xaxis.z)), ("Y", abs(yaxis.z)), ("Z", abs(zaxis.z))],
            key=lambda x: x[1]
        )[0]

        # Rearrange box dimensions based on dominant axis
        if dominant_axis == "Z":
            x_size, y_size, z_size = obb.xsize, obb.ysize, obb.zsize
        elif dominant_axis == "Y":
            x_size, y_size, z_size = obb.xsize, obb.zsize, obb.ysize
        else:  # dominant_axis == "X"
            x_size, y_size, z_size = obb.ysize, obb.xsize, obb.zsize

        return {
            "X": round(x_size * length_conversion_factor, 2),
            "Y": round(y_size * length_conversion_factor, 2),
            "Z": round(z_size * length_conversion_factor, 2),
            "Bounding Box Dimensions Unit": "METRE"
        }
    except AttributeError:
        return {}

def bounding_box_volume(obb_dimensions):
    obb_values = [obb_dimensions.get(axis) for axis in ("X", "Y", "Z") if obb_dimensions.get(axis) is not None]
    if len(obb_values) == 3:
        try:
            x, y, z = obb_values
            volume = round(x * y * z, 4)
        except (ValueError, TypeError):
            volume = None
        return volume

def real_volume_to_bounding_box_ratio(brep, obb_volume, lc_factor):
    if brep is not None:
        actual_volume = brep.volume * (lc_factor ** 3)
    try:
        if actual_volume is None or obb_volume is None:
            return None
        if obb_volume == 0:
            return None  # Avoid division by zero
        ratio = actual_volume / obb_volume
        if ratio < 0:
            return None  # Negative values are meaningless
        return round(ratio, 4)
    except Exception:
        return None    

# Converts the x-axis orientation vector of the obb into a cardinal direction (N, NE, E, SE, S, SW, W, NW).
def get_cardinal_direction_from_vector(obb):
    if not obb or not hasattr(obb, "frame") or not hasattr(obb.frame, "xaxis"):
        return "Not defined"

    xaxis = obb.frame.xaxis
    x, y = xaxis.x, xaxis.y

    if x == 0 and y == 0:
        return "Undefined"

    angle_rad = math.atan2(y, x)
    angle_deg = (math.degrees(angle_rad) + 360) % 360

    directions = [
        (22.5, "E"), (67.5, "NE"), (112.5, "N"), (157.5, "NW"),
        (202.5, "W"), (247.5, "SW"), (292.5, "S"), (337.5, "SE")
    ]

    for upper_bound, direction in directions:
        if angle_deg <= upper_bound:
            return direction

    return "E"  # Default fallback


def compute_brep_geometry_data(element, lc_factor):
    try:
        geometry_data = {}
        mesh, obb = get_mesh(element)
        brep = element.geometry
        geometry_data["Quantities (COMPAS)"] = quantities_compas(brep, lc_factor)
        obb_dimensions = bounding_box_dimensions(obb, lc_factor)
        geometry_data["Bounding Box Dimensions (OBB - local frame)"] = obb_dimensions
        obb_volume = bounding_box_volume(obb_dimensions)
        geometry_data["Bounding Box Volume"] = obb_volume
        geometry_data["Real Volume to Bounding Box Volume Ratio"] = real_volume_to_bounding_box_ratio(brep, obb_volume, lc_factor)
        geometry_data["Face Count (tessellated element)"] = face_count(mesh)
        geometry_data["Vertex Count (tessellated element)"] = vertex_count(mesh)
        geometry_data["Edge Count (tessellated element)"] = edge_count(mesh)
        geometry_data["Primary Object Axis (Cardinal Direction)"] = get_cardinal_direction_from_vector(obb)
        return geometry_data, obb_dimensions
    except Exception as e:
        print(f"[BREP ERROR] Failed to extract geometry: {e}")
        return {}, None
