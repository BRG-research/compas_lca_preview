def name(element):
    try:
        return element.Name
    except Exception:
        return "Not defined"

def globalid(element):
    try:
        return element.GlobalId
    except Exception:
        return "Not defined"

def entity(element):
    try:
        return type(element).__name__
    except Exception:
        return "Not defined"

def uid(element):
    try:
        return str(element.id())
    except Exception:
        return "Not defined"
    
def objecttype(element):
    try:
        return element.ObjectType
    except Exception:
        return "Not defined"

def description(element):
    return getattr(element, "Description", None) or "Unknown"

# Function to extract classification information using IfcRelAssociatesClassification
# The relationship is used to assign a classification notation or a classification reference to objects.
# If provided within the file, IfcRelAssociatesClassification links the IfcElement to standards like OmniClass.
# Very useful for downstream applications, but is usually not provided in IFC files.
def extract_classification_info(element, rel_classifications):
    classifications = []
    for rel in rel_classifications:
        if element in rel.RelatedObjects:
            classification_ref = rel.RelatingClassification
            classification_data = {
                "IfcEntity": type(classification_ref).__name__,
                "Identification": getattr(classification_ref, "Identification", "Unknown"),
                "System Name": getattr(getattr(classification_ref, "ReferencedSource", None), "Name", "Unknown"),
                "Name": getattr(classification_ref, "Name", "Unknown")
            }
            classifications.append(classification_data)
    if not classifications:
        return "Not defined"
    return classifications


# Extracts the "IsDecomposedBy" relationship: which smaller objects are part of the element
def extract_hierarchy(element, aggregates):
    decomposes = {}
    is_decomposed_by = []
    for rel in aggregates:
        if element in rel.RelatedObjects:
            decomposes = {
                "Name": rel.RelatingObject.Name if hasattr(rel.RelatingObject, "Name") and rel.RelatingObject.Name else "Unnamed",
                "IfcEntity": type(rel.RelatingObject).__name__,
                "GlobalId": rel.RelatingObject.GlobalId if hasattr(rel.RelatingObject, "GlobalId") else "Unknown"
            }
        if element == rel.RelatingObject:
            is_decomposed_by.extend([
                {
                    "Name": obj.Name if hasattr(obj, "Name") and obj.Name else "Unnamed",
                    "IfcEntity": type(obj).__name__,
                    "GlobalId": obj.GlobalId if hasattr(obj, "GlobalId") else "Unknown"
                }
                for obj in rel.RelatedObjects
            ])
    return decomposes, is_decomposed_by
