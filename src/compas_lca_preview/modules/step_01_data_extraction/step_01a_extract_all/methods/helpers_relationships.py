

# Returns a list of elements that are nested by the input element (i.e., its children in the hierarchy)
def nests(element, nesting_relationships):
    children = []
    for rel in nesting_relationships:
        if element == rel.RelatingObject:
            for obj in rel.RelatedObjects:
                children.append({
                    "Name": obj.Name if hasattr(obj, "Name") and obj.Name else "Unnamed",
                    "IfcEntity": type(obj).__name__,
                    "GlobalId": obj.GlobalId if hasattr(obj, "GlobalId") else "Unknown"
                })
    return children if children else None

# Returns the element that the input is nested into (i.e., its parent in the hierarchy)
def is_nested_by(element, nesting_relationships):
    for rel in nesting_relationships:
        if element in rel.RelatedObjects:
            relating_obj = rel.RelatingObject
            return {
                "Name": relating_obj.Name if hasattr(relating_obj, "Name") and relating_obj.Name else "Unnamed",
                "IfcEntity": type(relating_obj).__name__,
                "GlobalId": relating_obj.GlobalId if hasattr(relating_obj, "GlobalId") else "Unknown"
            }
    return None

# Returns the building elements covered by the given covering element.
def covers(covering_element, covering_relationships):
    covered_elements = []
    for rel in covering_relationships:
        if covering_element == rel.RelatingCovering:
            covered_elements.extend([
                {
                    "IfcEntity": type(obj).__name__,
                    "Name": obj.Name if hasattr(obj, "Name") and obj.Name else "Unnamed",
                    "GlobalId": obj.GlobalId if hasattr(obj, "GlobalId") else "Unknown"
                }
                for obj in rel.RelatedObjects
            ])
    return covered_elements if covered_elements else None


# Returns the coverings applied to the given building element.
# Returns all coverings applied to the given building element.
def is_covered_by(element, covering_relationships):
    coverings = []
    for rel in covering_relationships:
        if element in rel.RelatedObjects:
            coverings.append({
                "IfcEntity": type(rel.RelatingCovering).__name__,
                "Material": rel.RelatingCovering.Name if hasattr(rel.RelatingCovering, "Name") else "Unknown"
            })
    return coverings if coverings else None


# Function to extract opening relationships using IfcRelVoidsElement
def openings(element, void_relationships):
    openings = []
    for rel in void_relationships:
        if element == rel.RelatingBuildingElement:  # Correct way to check relationship
            openings.append({
                "IfcEntity": type(rel.RelatedOpeningElement).__name__,
                "GlobalId": rel.RelatedOpeningElement.GlobalId if hasattr(rel.RelatedOpeningElement, "GlobalId") else "Not defined",
                "OpeningType": rel.RelatedOpeningElement.PredefinedType if hasattr(rel.RelatedOpeningElement, "PredefinedType") else "Not defined"
            })
    return openings if openings else None


# Function to extract assignments using IfcRelAssigns (e.g., group assignments)
# A "Group" (IfcGroup) is a logical collection of things
# It's an aggregation under some non-geometrical / topological grouping aspects
def group_assignments(element, group_relationships):
    assignments = []
    for rel in group_relationships:
        if element in rel.RelatedObjects:
            relating_group = rel.RelatingGroup
            group_type = type(relating_group).__name__  # Extracts the actual subclass (IfcSystem, IfcZone, etc.)
            
            assignments.append({
                "IfcEntity": group_type,  # Captures the specific subclass name
                "Group Name": relating_group.Name if hasattr(relating_group, "Name") and relating_group.Name is not None else "Not defined",
                "Group Description": relating_group.Description if hasattr(relating_group, "Description") and relating_group.Description is not None else "Not defined"
            })
    return assignments if assignments else None



# Function to extract spatial containment relationships using IfcRelContainedInSpatialStructure
# IfcRelContainedInSpatialStructure defines the relationship where IfcElements are contained within spatial structures
# like buildings, storeys, or spaces, establishing their physical location and organization.
def extract_full_spatial_hierarchy(element, model, parent_lookup, hierarchy_tree):
    """
    Traces the full spatial hierarchy from an IfcElement up to the IfcProject level
    using the precomputed parent lookup dictionary.
    """
    spatial_hierarchy = []

    # Find the parent (e.g., a storey, building, etc.)
    parent_id = None
    contained_relations = model.get_entities_by_type("IfcRelContainedInSpatialStructure")  # Now using passed model

    for rel in contained_relations:
        if element in rel.RelatedElements:
            parent_id = rel.RelatingStructure.GlobalId  # Store GlobalId of parent
            break  # Assume one primary spatial containment

    # Traverse upwards using parent_lookup
    while parent_id:
        if parent_id in hierarchy_tree:
            entity_data = hierarchy_tree[parent_id]
            spatial_hierarchy.insert(0, {  # Insert at the beginning to maintain order
                "name": entity_data["Name"],
                "type": entity_data["IfcEntity"]
            })
        parent_id = parent_lookup.get(parent_id)  # Move to the next parent

    return spatial_hierarchy if spatial_hierarchy else [{"name": "Unknown", "type": "Unknown"}]