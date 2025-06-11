import os

def get_file_metadata(input_file, model, model_units):

    # Extract project name
    projects = model.get_entities_by_type("IfcProject")
    project_name = projects[0].Name if projects and hasattr(projects[0], "Name") else "Unnamed_Project"

    # Extract application details
    applications = model.get_entities_by_type("IfcApplication")
    if applications:
        application = applications[0]  # Assume the first IfcApplication is the correct one
        application_name = getattr(application, "ApplicationFullName", "Unknown Application")
        application_version = getattr(application, "Version", "Unknown Version")
        application_identifier = getattr(application, "ApplicationIdentifier", "Unknown ID")
        application_developer = getattr(application.ApplicationDeveloper, "Name", "Unknown Developer") if hasattr(application, "ApplicationDeveloper") else "Unknown Developer"
    else:
        application_name = "Unknown Application"
        application_version = "Unknown Version"
        application_identifier = "Unknown ID"
        application_developer = "Unknown Developer"

    # Count IfcBuildingElements
    if model.schema_name.startswith("IFC4.3"):
        building_elements = model.get_entities_by_type("IfcBuiltElement")
    else:
        building_elements = model.get_entities_by_type("IfcBuildingElement")

    total_building_elements = len(building_elements)

    # Subdivision breakdown
    breakdown = {}

    for elem in building_elements:
        elem_type = type(elem).__name__  # e.g., IfcWall, IfcSlab, IfcRoof
        breakdown[elem_type] = breakdown.get(elem_type, 0) + 1

    return {
        "IFC Project Name": project_name,
        "File Name": os.path.basename(input_file),
        "File Size (MB)": round(os.path.getsize(input_file) / (1024 * 1024), 2),  # Convert to MB
        "IFC Schema": model.schema_name,
        "IFC Project Units": model_units,
        "BIM Authoring Application": {
            "Application Name": application_name,
            "Version": application_version,
            "Application Identifier": application_identifier,
            "Developer": application_developer
        },
        "Building Elements Overview": {
            "Total Building Elements": total_building_elements,
            "Breakdown by Type": breakdown
        }
    }
