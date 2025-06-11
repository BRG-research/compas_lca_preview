# Function to extract the clean value from IFC representations (e.g., '<IfcLabel 99>' → '99')
def clean_ifc_value(value):
    if isinstance(value, str):
        # Remove "<IfcType" wrappers if present
        if value.startswith("<Ifc") and " " in value:
            return value.split(" ", 1)[1].rstrip(">")
        return value  # Return as-is if it's already clean
    return value  # Return numbers/booleans as-is


# Function to extract Psets from the element directly
def extract_element_psets(element, property_relationships):
    try:
        properties = {}

        for relationship in property_relationships:
            if element in relationship.RelatedObjects:
                property_set = getattr(relationship, "RelatingPropertyDefinition", None)

                if property_set and property_set.is_a("IfcPropertySet"):
                    for prop in getattr(property_set, "HasProperties", []) or []:
                        if hasattr(prop, "Name") and hasattr(prop, "NominalValue"):
                            raw_value = prop.NominalValue
                            properties[prop.Name] = clean_ifc_value(str(raw_value))

        return properties if properties else {}
    
    except Exception as e:
        return {}

# Function to extract ObjectTypePsets (if the element has an ObjectType)
def extract_type_psets(element, type_relationships):
    try:
        properties = {}

        for rel in type_relationships:
            if element in rel.RelatedObjects:
                object_type = rel.RelatingType
                if object_type and hasattr(object_type, "HasPropertySets"):
                    for pset in object_type.HasPropertySets:
                        if pset.is_a("IfcPropertySet"):
                            for prop in getattr(pset, "HasProperties", []) or []:
                                if hasattr(prop, "Name") and hasattr(prop, "NominalValue"):
                                    raw_value = prop.NominalValue
                                    properties[f"{pset.Name}.{prop.Name}"] = clean_ifc_value(str(raw_value))

        return properties if properties else {}
    except Exception as e:
        return {}


### Psets are semi-standardized but can be customized.
### Extracting all Psets is the best approach.
### Performance data can be filtered post-extraction for relevant attributes.
### This avoids making assumptions about Pset names while still capturing key info.