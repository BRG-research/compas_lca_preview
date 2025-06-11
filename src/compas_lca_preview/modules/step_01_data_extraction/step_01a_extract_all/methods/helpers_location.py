# ----------------------------------------------------------------
# Location determination methods (helpful for reinforcment ratio)
# ----------------------------------------------------------------

def get_storey_elevation(storey, lc_factor=1):
    try:
        if storey.ObjectPlacement and storey.ObjectPlacement.RelativePlacement:
            location = storey.ObjectPlacement.RelativePlacement.Location
            if location and location.Coordinates:
                return round(location.Coordinates[2] * lc_factor, 2)  # no rounding here for precise sorting
    except Exception:
        pass
    return float("inf")  # Treat missing elevation as highest (or you can raise)


def sorted_storey_map(model, lc_factor=1):
    storeys = model.building_storeys
    sorted_storeys = sorted(
        storeys,
        key=lambda s: get_storey_elevation(s, lc_factor)
    )

    storey_map = {}
    for storey in sorted_storeys:
        elevation = get_storey_elevation(storey, lc_factor)
        if isinstance(elevation, (int, float)):
            storey_map[storey.Name] = {
                "Elevation": round(elevation, 3),
                "Unit": "meters"
            }
    return storey_map



def element_storey_name(element):
    ancestor = element.parent
    while ancestor:
        if ancestor.is_a("IfcBuildingStorey"):
            return ancestor.Name
        ancestor = ancestor.parent
    return "Unknown"



# This is a helper function to display the entire spatial hierarchy later for the IfcElements
# Extracts the full spatial hierarchy and also returns a lookup dictionary
# Maps each entity (storeys, buildings, sites, etc.) to its parent.
def extract_spatial_hierarchy(model, lc_factor=1):
    hierarchy_tree = {}
    parent_lookup = {}  # Stores GlobalId -> Parent GlobalId

    # Extract Project
    projects = model.get_entities_by_type("IfcProject")
    if not projects:
        return "No IfcProject found.", {}
    
    project = projects[0]  # Assuming a single IfcProject
    hierarchy_tree[project.GlobalId] = {
        "IfcEntity": "IfcProject",
        "Name": getattr(project, "Name", "Unnamed"),
        "GlobalId": getattr(project, "GlobalId", "Unknown"),
        "Children": []
    }
    parent_lookup[project.GlobalId] = None  # Root has no parent

    # Extract Sites
    sites = model.get_entities_by_type("IfcSite")
    for site in sites:
        hierarchy_tree[site.GlobalId] = {
            "IfcEntity": "IfcSite",
            "Name": getattr(site, "Name", "Unnamed"),
            "GlobalId": getattr(site, "GlobalId", "Unknown"),
            "Children": []
        }
        parent_lookup[site.GlobalId] = project.GlobalId

        # Extract Buildings under Site
        buildings = model.get_entities_by_type("IfcBuilding")
        for building in buildings:
            hierarchy_tree[building.GlobalId] = {
                "IfcEntity": "IfcBuilding",
                "Name": getattr(building, "Name", "Unnamed"),
                "GlobalId": getattr(building, "GlobalId", "Unknown"),
                "Children": []
            }
            parent_lookup[building.GlobalId] = site.GlobalId

            # Extract Storeys under Building
            if hasattr(building, "storeys") and building.storeys:
                for storey in building.storeys:
                    hierarchy_tree[storey.GlobalId] = {
                        "IfcEntity": "IfcBuildingStorey",
                        "Name": getattr(storey, "Name", "Unnamed"),
                        "GlobalId": getattr(storey, "GlobalId", "Unknown"),
                        "Elevation": get_storey_elevation(storey, lc_factor),
                        "Children": []  # Stores IfcSpaces (NEW)
                    }
                    parent_lookup[storey.GlobalId] = building.GlobalId

            # Extract Spaces under Storeys
            spaces = model.get_entities_by_type("IfcSpace")
            for space in spaces:
                if hasattr(space, "Decomposes") and space.Decomposes:
                    parent_storey = space.Decomposes()[0].RelatingObject  # Get the parent structure
                    if parent_storey and parent_storey.is_a("IfcBuildingStorey"):
                        hierarchy_tree[space.GlobalId] = {
                            "IfcEntity": "IfcSpace",
                            "Name": getattr(space, "Name", "Unnamed"),
                            "GlobalId": getattr(space, "GlobalId", "Unknown"),
                            "CompositionType": getattr(space, "CompositionType", "Unknown"),
                        }
                        parent_lookup[space.GlobalId] = parent_storey.GlobalId
                        
                        # Append IfcSpace under the correct IfcBuildingStorey
                        if parent_storey.GlobalId in hierarchy_tree:
                            hierarchy_tree[parent_storey.GlobalId]["Children"].append(hierarchy_tree[space.GlobalId])

    return hierarchy_tree, parent_lookup


# Function to extract spatial containment relationships using IfcRelContainedInSpatialStructure
# IfcRelContainedInSpatialStructure defines the relationship where IfcElements are contained within spatial structures
# like buildings, storeys, or spaces, establishing their physical location and organization.
def extract_full_spatial_hierarchy(element, spatial_relationships, parent_lookup, hierarchy_tree):
    """
    Traces the full spatial hierarchy from an IfcElement up to the IfcProject level
    using the precomputed parent lookup dictionary.
    """
    spatial_hierarchy = []

    # Find the parent (e.g., a storey, building, etc.)
    parent_id = None

    for rel in spatial_relationships:
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