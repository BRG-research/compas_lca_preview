from . import helpers_boq as boq
import csv
import os
import json

def extractor_boq(out_directory_elements, out_directory_boq):

    # Filename list
    source_files = os.listdir(out_directory_elements)

    boq_rows = []

    # Iterate over source files
    for filename in source_files:
        if filename.endswith(".json"):
            source_path = os.path.join(out_directory_elements, filename)

            try:

                with open(source_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                element_metadata = data.get("Element Metadata", {})
                geometry_data = data.get("Element Geometry Data", {})
                psets_element = data.get("Element Property Sets", {}).get("Psets Element", {})

                element_entity = element_metadata.get("Type")
                ifc_quants_element = geometry_data.get("Quantities (IFC)", {})
                element_quantities_compas = geometry_data.get("Quantities (COMPAS)", {})
                volume_compas = element_quantities_compas.get("Net Volume")
                obb_dimensions = geometry_data.get("Bounding Box Dimensions (OBB - local frame)", {})

                # Calculate prioritized quantities & log sources
                volume, area, length, volume_source, area_source, length_source = boq.extract_quantities(
                    volume_compas, element_entity, ifc_quants_element, psets_element, obb_dimensions
                )

                boq_row = {
                    "GlobalId": element_metadata.get("GlobalId", "Unknown"),
                    "Name": element_metadata.get("Name", "Unknown"),
                    "Entity": element_entity,
                    "ObjectType": element_metadata.get("ObjectType", "Unknown"),
                    "Length [m]": length or 0,
                    "Length Source": length_source,
                    "Largest Surface Area [m^2]": area or 0,
                    "Area Source": area_source,
                    "Volume [m^3]": volume or 0,
                    "Volume Source": volume_source
                }

                boq_rows.append(boq_row)

            except Exception as e:
                continue

    # Export the Bill of Quantities to a CSV file
    boq_output_path = os.path.join(out_directory_boq, "BoQ_step_01a.csv")
    boq_fieldnames = ["GlobalId", "Name", "Entity", "ObjectType", "Length [m]", "Length Source", "Largest Surface Area [m^2]", "Area Source", "Volume [m^3]", "Volume Source"]

    with open(boq_output_path, "w", newline='', encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=boq_fieldnames)
        writer.writeheader()
        writer.writerows(boq_rows)

