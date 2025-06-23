import os
import json
import hashlib
import shutil
import csv
from collections import defaultdict

# The compiler compiles IFC elements by grouping identical elements based on type, object type, material data, and material layers
# Copies elements that require unique material inference separately. Saves a compiled overview.
# The motivation to compile elements like this is to reduce the number of required LLM inference calls.
# This is important for the LCA pipeline, as it reduces the number of API calls and speeds up the process.
def aggregator_element(source_folder, elements_unique_folder, data_folder):
    # Ensure the destination folders exist
    os.makedirs(elements_unique_folder, exist_ok=True)
    os.makedirs(data_folder, exist_ok=True)

    # Filename list
    source_files = os.listdir(source_folder)

    # Grouped data structures
    grouped_elements = defaultdict(list)
    processed_files = set()
    compiled_overview = {}
    total_compiled_elements = 0
    total_unique_elements = 0

    # Iterate over source files
    for filename in source_files:
        if filename.endswith(".json"):
            source_path = os.path.join(source_folder, filename)

            try:
                with open(source_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                element_metadata = data.get("Element Metadata", {})
                material_data = data.get("Element Material Data", [])
                property_sets = data.get("Element Property Sets", {})

                type_value = element_metadata.get("Type")
                object_type = element_metadata.get("ObjectType")
                material_relationship_type = "Not defined"
                material_identifier = "Not defined"
                material_layers = []

                if isinstance(material_data, list):
                    for material in material_data:
                        if "IfcEntity" in material:
                            material_relationship_type = material.get("IfcEntity")

                            if material_relationship_type == "IfcMaterial":
                                material_identifier = material.get("Material Name")

                            elif material_relationship_type == "IfcMaterialLayerSet":
                                material_identifier = " | ".join(
                                    f'{layer.get("Material Name", "Unknown")} ({layer.get("Thickness", 0)} {layer.get("Thickness unit", "N/A")})'
                                    for layer in material.get("Layers", [])
                                    if isinstance(layer, dict)
                                )
                                material_layers = [
                                    {
                                        "Material Name": layer.get("Material Name", "Unknown"),
                                        "Thickness": layer.get("Thickness", 0),
                                        "Thickness Unit": layer.get("Thickness unit", "N/A")
                                    }
                                    for layer in material.get("Layers", []) if isinstance(layer, dict)
                                ]

                            elif material_relationship_type == "IfcMaterialLayerSetUsage":
                                material_identifier = material.get("Layer Set Name")
                                material_layers = [
                                    {
                                        "Material Name": layer.get("Material Name", "Unknown"),
                                        "Thickness": layer.get("Thickness", 0),
                                        "Thickness Unit": layer.get("Thickness unit", "N/A")
                                    }
                                    for layer in material.get("Layers", []) if isinstance(layer, dict)
                                ]

                if type_value and object_type:
                    grouping_key = (
                        type_value,
                        object_type,
                        material_relationship_type,
                        material_identifier,
                        json.dumps(material_layers, sort_keys=True)
                    )

                    grouped_elements[grouping_key].append({
                        "UID": element_metadata.get("UID"),
                        "GlobalID": element_metadata.get("GlobalId"),
                        "Name": element_metadata.get("Name"),
                        "Property Sets": property_sets,
                        "OriginalFile": filename
                    })

                    processed_files.add(filename)

            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error processing {filename}: {e}")

    # Create compiled overview
    for (type_value, object_type, material_relationship_type, material_identifier, material_layers_json), elements in grouped_elements.items():
        num_elements = len(elements)

        if num_elements >= 2:
            total_compiled_elements += num_elements

            group_key_string = f"{type_value}_{object_type}_{material_relationship_type}"
            unique_filename = hashlib.md5(group_key_string.encode()).hexdigest()[:10]

            compiled_overview[unique_filename] = {
                "Compiled Type": type_value,
                "Compiled ObjectType": object_type,
                "Elements": [
                    {
                        "Name": elem["Name"],
                        "GlobalID": elem["GlobalID"]
                    } for elem in elements
                ]
            }

        # If there is only one element that fulfilled the requirements, then it is a "single" (unique) element
        elif num_elements == 1:
            single_element = elements[0]
            original_file = single_element["OriginalFile"]
            source_path = os.path.join(source_folder, original_file)
            destination_path = os.path.join(elements_unique_folder, original_file)
            shutil.copy2(source_path, destination_path)
            total_unique_elements += 1

    # Save the compiled overview
    overview_path = os.path.join(data_folder, "aggregation_overview.json")
    with open(overview_path, "w", encoding="utf-8") as overview_file:
        json.dump(compiled_overview, overview_file, indent=4, ensure_ascii=False)

    

    # Copy files not processed into single folder
    for filename in os.listdir(source_folder):
        if filename.endswith(".json") and filename not in processed_files:
            source_path = os.path.join(source_folder, filename)
            destination_path = os.path.join(elements_unique_folder, filename)
            shutil.copy2(source_path, destination_path)
            total_unique_elements += 1  # increment counter

    groups_count = len(compiled_overview)

    print(f"Total aggregation groups generated (and representative elements for inference): {groups_count}")
    print(f"Total compiled elements: {total_compiled_elements}")
    print(f"Total unique elements: {total_unique_elements}")

    return overview_path, groups_count, total_compiled_elements, total_unique_elements


# Update BOQ
def aggregator_boq(boq_path, overview_path, data_folder):
    # Load JSON file
    with open(overview_path, "r", encoding="utf-8-sig") as jf:
        group_data = json.load(jf)

    # Build a lookup: (GlobalId, Name) --> GroupID
    element_to_group = {}
    groupid_to_compiled_objecttype = {}
    for group_id, group_info in group_data.items():
        groupid_to_compiled_objecttype[group_id] = group_info["Compiled ObjectType"]
        for elem in group_info["Elements"]:
            key = (elem["GlobalID"], elem["Name"])
            element_to_group[key] = group_id

    # Load CSV
    rows = []
    with open(boq_path, "r", newline='', encoding="utf-8-sig") as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            rows.append(row)

    # Prepare output data
    grouped_data = defaultdict(lambda: {"Length [m]": 0.0, "Largest Surface Area [m^2]": 0.0, "Volume [m^3]": 0.0, "Count": 0, "Entity": None})
    ungrouped_data = []

    for row in rows:
        globalid = row["GlobalId"]
        name = row["Name"]
        entity = row["Entity"]
        objecttype = row["ObjectType"]
        key = (globalid, name)

        # Parse numeric values safely
        try:
            length = float(row.get("Length [m]", 0) or 0)
        except ValueError:
            length = 0
        try:
            area = float(row.get("Largest Surface Area [m^2]", 0) or 0)
        except ValueError:
            area = 0
        try:
            volume = float(row.get("Volume [m^3]", 0) or 0)
        except ValueError:
            volume = 0

        if key in element_to_group:
            group_id = element_to_group[key]
            grouped_data[group_id]["Length [m]"] += length
            grouped_data[group_id]["Largest Surface Area [m^2]"] += area
            grouped_data[group_id]["Volume [m^3]"] += volume
            grouped_data[group_id]["Count"] += 1
            if grouped_data[group_id]["Entity"] is None:
                grouped_data[group_id]["Entity"] = entity
        else:
            # Save ungrouped row
            ungrouped_data.append({
                "Id": globalid,
                "Name": name,
                "Entity": entity,
                "ObjectType": objecttype,
                "Length [m]": length,
                "Largest Surface Area [m^2]": area,
                "Volume [m^3]": volume,
                "Compiled": False,
                "Elements Compiled": 1
            })

    # Handle possible duplicate Compiled ObjectType names
    compiled_objecttype_counter = defaultdict(int)
    final_rows = []

    for group_id, sums in grouped_data.items():
        base_name = groupid_to_compiled_objecttype[group_id]
        compiled_objecttype_counter[base_name] += 1
        if compiled_objecttype_counter[base_name] > 1:
            # If multiple same names, append a number
            name = f"{base_name} ({compiled_objecttype_counter[base_name]})"
        else:
            name = base_name

        final_rows.append({
            "Id": group_id,
            "Name": name,
            "Entity": sums["Entity"],
            "ObjectType": groupid_to_compiled_objecttype[group_id],
            "Length [m]": round(sums["Length [m]"], 4),
            "Largest Surface Area [m^2]": round(sums["Largest Surface Area [m^2]"], 4),
            "Volume [m^3]": round(sums["Volume [m^3]"], 4),
            "Compiled": True,
            "Elements Compiled": sums["Count"]
        })

    # Add ungrouped elements at the end
    final_rows.extend(ungrouped_data)

    # Write to new CSV
    output_fieldnames = ["Id", "Name", "Entity", "ObjectType", "Length [m]", "Largest Surface Area [m^2]", "Volume [m^3]", "Compiled", "Elements Compiled"]
    
    # Define output file name
    output_filename = "BoQ_step_01b.csv"

    # Combine directory + filename
    output_path = os.path.join(data_folder, output_filename)

    print(f"Aggregated BOQ saved to {output_path}")
    print(f"Total BoQ items count: {len(final_rows)}")

    with open(output_path, "w", newline='', encoding="utf-8-sig") as outf:
        writer = csv.DictWriter(outf, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)


# Update metadata
def aggregator_metadata(metadata_path, groups_count, total_compiled_elements, total_unique_elements, data_folder):
    # Load the existing metadata
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Ensure the base structure exists
    if "Module 01: Data Extraction" not in metadata:
        metadata["Module 01: Data Extraction"] = {}

    # Add the new aggregation data
    metadata["Module 01: Data Extraction"]["Module 01b: Aggregate Elements"] = {
        "Total individual elements aggregated (due to shared ObjectType and IfcMaterials)": total_compiled_elements,
        "Total aggregation groups generated (and representative elements for inference)": groups_count,
        "Total individual elements identified as unique": total_unique_elements
    }

    # Construct a new file path
    new_metadata_path = os.path.join(data_folder, "metadata_step_01b.json")

    # Save the updated metadata to the new file
    with open(new_metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)