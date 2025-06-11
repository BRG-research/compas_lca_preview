import os
import json
import copy
import csv

# Method to spot multi-layer elements and dissect them into new JSON files with target layer emphasis
def dissector_element(source_dirs, elements_directory, target_layer_directory, metadata_path, output_folder):

    # Initialize counters
    single_counter = 0
    multi_counter = 0
    target_layer_counter = 0

    # Process all files in source directory
    for source_dir in source_dirs:
        for filename in os.listdir(source_dir):
            if not filename.endswith(".json"):
                continue

            source_path = os.path.join(source_dir, filename)
            with open(source_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue

            # Find material layers and store full metadata
            material_data = data.get("Element Material Data", [])
            layers = []
            material_metadata = None  # <- NEW
            for mat in material_data:
                if not isinstance(mat, dict):
                    continue
                if mat.get("IfcEntity") in ("IfcMaterialLayerSetUsage", "IfcMaterialLayerSet") and "Layers" in mat:
                    layers = mat["Layers"]
                    material_metadata = mat  # <- store full object
                    break

            # No layers or single-layer elements → copy as-is to elements_directory

            if not layers or len(layers) == 1:
                # Remove the key from the original file data
                for mat in material_data:
                    if isinstance(mat, dict) and "Layer Direction and Growth description" in mat:
                        mat.pop("Layer Direction and Growth description", None)

                if not os.path.exists(elements_directory):
                    os.makedirs(elements_directory, exist_ok=True)

                target_path = os.path.join(elements_directory, filename)
                with open(target_path, "w", encoding="utf-8") as out_file:
                    json.dump(data, out_file, indent=4, ensure_ascii=False)
                single_counter += 1
                continue

            # If an element has more than 2 layers, it is dissected into multiple "Target Layer" files
            elif len(layers) > 1:
                base_filename = filename[:-5]  # strip ".json"
                multi_counter += 1

                for idx, target_layer in enumerate(layers):
                    # Collect all other layers except the target one
                    other_layers = []
                    for i, layer in enumerate(layers):
                        if i == idx:
                            continue
                        other_layers.append({
                            "Material Name": layer.get("Material Name", "Unknown"),
                            "Thickness": layer.get("Thickness", 0),
                            "Thickness Unit": layer.get("Thickness unit", "N/A"),
                            "Layer Number": i + 1
                        })

                    # Append material metadata at the end of other layers list



                    # Build Building Element Context conditionally
                    building_element_context = {}

                    if "Element Metadata" in data:
                        building_element_context["Element Metadata"] = copy.deepcopy(data["Element Metadata"])
                    building_element_context["Other Material Layers"] = other_layers
                    if material_metadata:
                        material_metadata_cleaned = copy.deepcopy(material_metadata)
                        material_metadata_cleaned.pop("Layers", None)
                        building_element_context["Layer Set Metadata"] = material_metadata_cleaned
                    if "Element Geometry Data" in data:
                        building_element_context["Element Geometry Data"] = copy.deepcopy(data["Element Geometry Data"])
                    if "Element Property Sets" in data:
                        building_element_context["Element Property Sets"] = copy.deepcopy(data["Element Property Sets"])
                    if "Element Location" in data:
                        building_element_context["Element Location"] = copy.deepcopy(data["Element Location"])

                    # Create output structure
                    output_data = {
                        "Target Layer of Material Inference": {
                            "Material Name": target_layer.get("Material Name", "Unknown"),
                            "Thickness": target_layer.get("Thickness", 0),
                            "Thickness Unit": target_layer.get("Thickness unit", "N/A"),
                            "Layer Number": idx + 1
                        },
                        "Building Element Context": building_element_context
                    }

                    layer_number = idx + 1
                    if "CompilationGroupID" in data:
                        output_data["CompilationGroupID"] = f"{data['CompilationGroupID']}_L{layer_number}"
                    elif "Element Metadata" in data and "GlobalId" in data["Element Metadata"]:
                        # Inject modified GlobalId inside nested metadata
                        output_data.setdefault("Building Element Context", {}).setdefault("Element Metadata", {})
                        output_data["Building Element Context"]["Element Metadata"]["GlobalId"] = f"{data['Element Metadata']['GlobalId']}_L{layer_number}"

                    output_filename = f"{base_filename}_L{layer_number}.json"
                    output_path = os.path.join(target_layer_directory, output_filename)

                    if not os.path.exists(target_layer_directory):
                        os.makedirs(target_layer_directory, exist_ok=True)

                    with open(output_path, "w", encoding="utf-8") as out_file:
                        json.dump(output_data, out_file, indent=4, ensure_ascii=False)

                    target_layer_counter += 1

    # Update metadata JSON
    with open(metadata_path, "r", encoding="utf-8") as meta_file:
        metadata = json.load(meta_file)

    metadata["Module 01: Data Extraction"]["Module 01c: Dissect Layers"] = {
        "Total multilayer elements": multi_counter,
        "Total Target Layer JSON files created": target_layer_counter,
        "Total single-layer or non-layer elements": single_counter
    }

    metadata["Module 01: Data Extraction"]["Required Inferences"] = target_layer_counter + single_counter

    new_metadata_path = os.path.join(output_folder, "metadata_step_01c.json")
    with open(new_metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)



# Method to load material names for non-dissected elements (i.e., no or 1 layer only)
# This descriptor is then mapped to the BOQ for traceability (i.e., to easily compare LLM output with original descriptor)
def load_material_descriptors(elements_directory):
    mapping = {}

    for filename in os.listdir(elements_directory):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(elements_directory, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue

        # Determine the ID key (CompilationGroupID preferred)
        id_key = data.get("CompilationGroupID")
        if not id_key:
            id_key = data.get("Element Metadata", {}).get("GlobalId")

        if not id_key:
            continue  # Skip if no ID

        material_name = "Unknown"
        thickness = None

        material_data = data.get("Element Material Data", "Not defined")

        if isinstance(material_data, list):
            for mat in material_data:
                if mat.get("IfcEntity") in ("IfcMaterialLayerSetUsage", "IfcMaterialLayerSet"):
                    layers = mat.get("Layers", [])
                    if layers and isinstance(layers, list):
                        first_layer = layers[0]
                        material_name = first_layer.get("Material Name", "Unknown")
                        thickness = first_layer.get("Thickness")  # May be None
                        break
                elif mat.get("IfcEntity") == "IfcMaterial":
                    material_name = mat.get("Material Name", "Unknown")
                    # No thickness for single material entity
                    break

        mapping[id_key] = {
            "Material Name": material_name,
            "Thickness": thickness
        }

    return mapping



# Method to load all dissected target layer JSONs and build a mapping for BOQ reference.
# Mapping key is either CompilationGroupID (preferred) or GlobalId (fallback)
# Each entry contains: list of layer dicts with thickness, layer number and total thickness.
# The mapping shall be used to determine thickness ratios with which the BOQ volume is dissected
def load_dissected_layers(target_layer_directory):
    mapping = {}

    for filename in os.listdir(target_layer_directory):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(target_layer_directory, filename)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            continue

        group_id = data.get("CompilationGroupID")
        if not group_id:
            group_id = data.get("Building Element Context", {}).get("Element Metadata", {}).get("GlobalId")

        if not group_id:
            continue  # Skip if neither available

        # Extract base ID (strip layer suffix like _L1)
        base_id = group_id.rsplit("_L", 1)[0]


        # Extract target layer thickness
        target_layer = data.get("Target Layer of Material Inference", {})
        target_thickness = target_layer.get("Thickness", 0)
        layer_number = target_layer.get("Layer Number", 0)
        material_name = target_layer.get("Material Name", "Unknown")

        # Extract other material layers
        other_layers = data.get("Building Element Context", {}).get("Other Material Layers", [])

        other_thickness_sum = 0.0
        for layer in other_layers:
            other_thickness_sum += layer.get("Thickness", 0) or 0.0

        # Now compute total thickness
        total_thickness = (target_thickness or 0.0) + other_thickness_sum

        if base_id not in mapping:
            mapping[base_id] = {"layers": [], "total_thickness": 0.0}

        mapping[base_id]["layers"].append({
            "Layer Number": layer_number,
            "Thickness": target_thickness,
            "Material Name": material_name
        })
        mapping[base_id]["total_thickness"] = total_thickness


    # Sort layers by Layer Number for consistency
    for group_info in mapping.values():
        group_info["layers"].sort(key=lambda x: x["Layer Number"])

    return mapping



# A BoQ row with matching dissected layers info is split into multiple rows
# "Volume" and "Name" columns are adjusted accordingly
def split_row_by_layers(row, layers_info):
    id_ = row["Id"]
    base_name = row["Name"]
    entity = row["Entity"]
    object_type = row["ObjectType"]
    length = float(row["Length [m]"])
    area = float(row["Largest Surface Area [m^2]"])
    volume = float(row["Volume [m^3]"])
    compiled = row["Compiled"]
    compilation_count = row["Elements Compiled"]

    total_thickness = layers_info["total_thickness"] or 0.0

    split_rows = []

    if total_thickness == 0:
        for layer in layers_info["layers"]:
            layer_num = layer["Layer Number"]
            ratio = 1.0
        split_rows.append({
            "Id": f"{id_}_L{layer_num}",
            "Name": f"{base_name} (L{layer_num})",
            "Entity": entity,
            "ObjectType": object_type,
            "Length [m]": round(length, 4),
            "Largest Surface Area [m^2]": round(area, 4),
            "Volume [m^3]": round(volume * ratio, 4),
            "Compiled": compiled,
            "Elements Compiled": compilation_count,
            "Layer Number": layer_num,
            "Material Descriptor": layer.get("Material Name", "Unknown"),
            "Layer Thickness [m]": layer.get("Thickness") if layer.get("Thickness") else 0
        })

    else:
        # Scale volume by thickness proportion
        for layer in layers_info["layers"]:
            layer_num = layer["Layer Number"]
            layer_thickness = layer.get("Thickness", 0)
            ratio = layer_thickness / total_thickness if total_thickness else 1.0

            split_rows.append({
                "Id": f"{id_}_L{layer_num}",
                "Name": f"{base_name} (L{layer_num})",
                "Entity": entity,
                "ObjectType": object_type,
                "Length [m]": round(length, 4),
                "Largest Surface Area [m^2]": round(area, 4),
                "Volume [m^3]": round(volume * ratio, 4),
                "Compiled": compiled,
                "Elements Compiled": compilation_count,
                "Layer Number": layer_num,
                "Material Descriptor": layer.get("Material Name", "Unknown"),
                "Layer Thickness [m]": layer.get("Thickness") if layer.get("Thickness") else 0
            })

    return split_rows

# Method to dissect the compiled BoQ from step 1b on dissected layers
# Creates an updated BoQ with the dissected layers accounted for
def dissector_boq(compiled_boq_path, target_layer_directory, elements_directory, output_folder):

    # Load dissected layers mapping
    dissected_layers = load_dissected_layers(target_layer_directory)
    non_dissected_elements = load_material_descriptors(elements_directory)

    # Load compiled BoQ
    rows = []
    with open(compiled_boq_path, "r", newline='', encoding="utf-8-sig") as cf:
        reader = csv.DictReader(cf)
        for row in reader:
            # Parse and normalize numeric fields
            row["Length [m]"] = float(row.get("Length [m]", 0) or 0)
            row["Largest Surface Area [m^2]"] = float(row.get("Largest Surface Area [m^2]", 0) or 0)
            row["Volume [m^3]"] = float(row.get("Volume [m^3]", 0) or 0)
            row["Compiled"] = True if str(row.get("Compiled", "False")) == "True" else False
            row["Elements Compiled"] = int(row.get("Elements Compiled", 1))
            rows.append(row)

    # Build final rows
    final_rows = []
    for row in rows:
        id_ = row["Id"]

        if id_ in dissected_layers:
            split_rows = split_row_by_layers(row, dissected_layers[id_])
            final_rows.extend(split_rows)
        else:
            # No split needed
            row["Layer Number"] = 0
            material_descriptor = non_dissected_elements.get(id_, {}).get("Material Name", "Unknown")
            thickness = non_dissected_elements.get(id_, {}).get("Thickness", 0)
            row["Material Descriptor"] = material_descriptor
            row["Layer Thickness [m]"] = thickness
            final_rows.append(row)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Write to output CSV
    output_fieldnames = [
        "Id",
        "Compiled", 
        "Elements Compiled", 
        "Name",
        "Entity",
        "ObjectType",
        "Material Descriptor", 
        "Layer Number", 
        "Layer Thickness [m]",
        "Length [m]", 
        "Largest Surface Area [m^2]", 
        "Volume [m^3]"
        ]
    output_filename = "BoQ_step_01c.csv"
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "w", newline='', encoding="utf-8-sig") as outf:
        writer = csv.DictWriter(outf, fieldnames=output_fieldnames)
        writer.writeheader()
        writer.writerows(final_rows)
