# This function filters the data dictionary to only include fields specified in the allowed_fields dictionary.
def filter_fields(data_dict, allowed_fields):
    return {k: v for k, v in data_dict.items() if allowed_fields.get(k, False)}

# Function to extract material layers from IfcMaterialLayerSet
def extract_material_layers(layer_set, length_conversion_factor):
    if layer_set and hasattr(layer_set, "MaterialLayers"):
        return [
            {
                "IfcEntity": "IfcMaterialLayer",
                "Material Name": layer.Material.Name if hasattr(layer.Material, "Name") else "Unknown",
                "Description": layer.Material.Description if hasattr(layer.Material, "Description") else "Unknown",
                "Category": layer.Material.Category if hasattr(layer.Material, "Category") else "Unknown",
                "Thickness": layer.LayerThickness * length_conversion_factor if hasattr(layer, "LayerThickness") else "Unknown",
                "Thickness unit": "METRE"
            }
            for layer in layer_set.MaterialLayers
        ]
    return []




# Function to extract how layers are applied using IfcMaterialLayerSetUsage
def extract_material_layer_set_usage(layer_usage, length_conversion_factor):
    direction_axis = layer_usage.LayerSetDirection if hasattr(layer_usage, "LayerSetDirection") else "Unknown"
    direction_sense = layer_usage.DirectionSense if hasattr(layer_usage, "DirectionSense") else "Unknown"
    # Determine human-readable descriptions
    if direction_axis == "AXIS2":
        growth_description = "Layers are stacked perpendicular to the element's length, defining its thickness."
        if direction_sense == "NEGATIVE":
            growth_description = "Layers are stacked perpendicular to the element's length, growing in the opposite direction from its reference surface."
    elif direction_axis == "AXIS3":
        growth_description = "Layers are stacked vertically, defining the element’s buildup."
        if direction_sense == "NEGATIVE":
            growth_description = "Layers are stacked vertically, growing downward from the element’s reference surface."
    else:
        growth_description = "Layer growth direction is unspecified."

    layer_set = layer_usage.ForLayerSet if hasattr(layer_usage, "ForLayerSet") else None
    return {
        "IfcEntity": "IfcMaterialLayerSetUsage",
        "Layer Set Name": layer_set.LayerSetName if layer_set and hasattr(layer_set, "LayerSetName") else "Unknown",
        "Layer Set Description": layer_set.Description if layer_set and hasattr(layer_set, "Description") else "Unknown",
        "Layer Set Total Thickness": layer_set.TotalThickness if layer_set and hasattr(layer_set, "TotalThickness") and layer_set.TotalThickness is not None else "Unknown",
        "Layers": extract_material_layers(layer_set, length_conversion_factor) if hasattr(layer_usage, "ForLayerSet") else [],
        "Layer Direction and Growth description": growth_description,
    }



# Method to extract material assigned to the IfcTypeObject (e.g., IfcWallType) if the element itself has no material.
def extract_material_from_type(element, material_relationships, type_relationships, length_conversion_factor):
    try:

        for rel in type_relationships:
            if element in rel.RelatedObjects:
                type_object = rel.RelatingType  # This is IfcWallType, IfcSlabType, etc.

                # check if the IfcTypeObject has a material assigned
                type_materials = extract_material_associations(type_object, material_relationships, type_relationships, length_conversion_factor)
                
                # If type has material, return it
                if type_materials and type_materials != "Not defined":
                    return type_materials

        return "Not defined"  # No type-based materials found

    except Exception as e:
        print(f"Error extracting type-based materials for element {element}: {e}")
        return "Not defined"


# Extract full material data
def extract_material_associations(element, material_relationships, type_relationships, length_conversion_factor):
    try:
        materials = []

        for rel in material_relationships:
            if element in rel.RelatedObjects:
                relating_material = rel.RelatingMaterial

                if relating_material.is_a("IfcMaterialLayerSetUsage"):
                    material_entry = extract_material_layer_set_usage(relating_material, length_conversion_factor)
                    material_entry["IfcEntity"] = "IfcMaterialLayerSetUsage"
                    materials.append(material_entry)

                elif relating_material.is_a("IfcMaterialLayerSet"):
                    material_entry = {
                        "IfcEntity": "IfcMaterialLayerSet",
                        "Layers": extract_material_layers(relating_material, length_conversion_factor)
                    }
                    materials.append(material_entry)

                elif relating_material.is_a("IfcMaterial"):
                    material_entry = {
                        "IfcEntity": "IfcMaterial",
                        "Material Name": getattr(relating_material, "Name", "Unknown"),
                        "Material Description": getattr(relating_material, "Description", "Unknown"),
                        "Material Category": getattr(relating_material, "Category", "Unknown"),
                        "Thickness": "Unknown",
                        "Thickness unit": "Unknown"
                    }
                    materials.append(material_entry)

        if not materials:
            return extract_material_from_type(element, material_relationships, type_relationships, length_conversion_factor)

        return materials if materials else "Not defined"

    except Exception as e:
        print(f"Error extracting materials for element {element}: {e}")
        return "Not defined"
