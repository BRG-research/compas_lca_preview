import os
import json
import concurrent.futures
from . import helpers_units as unit
from . import helpers_io as inout
from . import helpers_metadata as meta
from . import helpers_material as mat
from . import helpers_geometry as geo
from . import helpers_psets as prop
from . import helpers_relationships as rela
from . import helpers_location as loc
from . import helpers_file_metadata as file_meta


def extractor(brep_toggle, brep_timeout, ifc_input_file, model, out_directory_elements, out_directory_compositions, out_directory_boq, entity_config, entity_bool=True):

    # Initialize counters for single and composition elements & bill of quantities rows
    count_single_elements = 0
    count_composition_elements = 0
    count_skipped_elements = 0
    brep_timeouts = []

    # Check IFC schema version to specify the correct entity type
    schema_version = model.schema_name
    entity_type = "IfcBuiltElement" if schema_version.startswith("IFC4.3") else "IfcBuildingElement"

    # Load all IfcBuildingElements from IFC model
    elements = model.get_entities_by_type(entity_type)

    # Extract global model values before looping element
    formatted_units, lc_factor = unit.model_units(model)
    sorted_storey_map = loc.sorted_storey_map(model, lc_factor)
    hierarchy_tree, parent_lookup = loc.extract_spatial_hierarchy(model, lc_factor)
    classification_relationships = model.get_entities_by_type("IfcRelAssociatesClassification")
    property_relationships = model.get_entities_by_type("IfcRelDefinesByProperties")
    type_relationships = model.get_entities_by_type("IfcRelDefinesByType")
    material_relationships = model.get_entities_by_type("IfcRelAssociatesMaterial")
    spatial_relationships = model.get_entities_by_type("IfcRelContainedInSpatialStructure")
    aggregates_relationships = model.get_entities_by_type("IfcRelAggregates")
    nesting_relationships = model.get_entities_by_type("IfcRelNests")
    covering_relationships = model.get_entities_by_type("IfcRelCoversBldgElements")
    void_relationships = model.get_entities_by_type("IfcRelVoidsElement")
    group_relationships = model.get_entities_by_type("IfcRelAssignsToGroup")

    # Get File Metadata for overview sheet
    file_metadata = file_meta.get_file_metadata(ifc_input_file, model, formatted_units)

    # Some IFC files have identical names for elements. Keep track of used names
    used_names = {}

    # Iterate over all IfcBuildingElements
    for element in elements:

        # Get entity and skip based on config/1_extraction_config.yaml
        element_type = meta.entity(element)
        if entity_bool == False:
            if not entity_config.get(element_type, False):
                count_skipped_elements += 1
                continue # Skip this element

        try:
            # === CREATE DATA SHEETS FOR EACH ELEMENT ===

            # Initialize the data dictionary for each element
            element_data = {}

            # --- ELEMENT METADATA ---
            metadata = {}
            metadata["Name"] = meta.name(element)
            metadata["Description"] = meta.description(element)
            metadata["UID"] = meta.uid(element)
            metadata["GlobalId"] = meta.globalid(element)
            metadata["Type"] = meta.entity(element)
            metadata["ObjectType"] = meta.objecttype(element)
            metadata["Classification"] = meta.extract_classification_info(element, classification_relationships)
            decomposes, is_decomposed_by = meta.extract_hierarchy(element, aggregates_relationships)
            metadata["Decomposes"] = decomposes
            metadata["Is Decomposed By"] = is_decomposed_by
            element_data["Element Metadata"] = metadata

            # --- MATERIAL DATA ---
            material_data = mat.extract_material_associations(element, material_relationships, type_relationships, lc_factor)
            element_data["Element Material Data"] = material_data

            # --- GEOMETRY DATA ---
            geometry_data = {}
            geometry_data["Quantities (IFC)"] = geo.quantities_ifc(element, property_relationships, lc_factor)
            geometry_data["Geometric Representation"] = geo.representation(element)

            # Calculate BREP-related geometry data with boolean and timout specifications
            if brep_toggle:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(geo.compute_brep_geometry_data, element, lc_factor)
                    try:
                        brep_result, obb_dimensions = future.result(brep_timeout)
                        geometry_data.update(brep_result)
                    except concurrent.futures.TimeoutError:
                        print(f"[TIMEOUT] Skipping BREP geometry for element {meta.name(element)}")
                        brep_timeouts.append({
                            "Name": meta.name(element),
                            "GlobalId": meta.globalid(element)
                        })
            element_data["Element Geometry Data"] = geometry_data

            # --- PROPERTY SETS ---
            psets_data = {}
            psets_data["Psets Element"] = prop.extract_element_psets(element, property_relationships)
            psets_data["Psets Object Type"] = prop.extract_type_psets(element, type_relationships)
            element_data["Element Property Sets"] = psets_data
                
            # --- RELATIONSHIPS ---
            relationships_data = {}
            relationships_data["Nests"] = rela.nests(element, nesting_relationships)
            relationships_data["Is Nested By"] = rela.is_nested_by(element, nesting_relationships)
            relationships_data["Covers"] = rela.covers(element, covering_relationships)
            relationships_data["Is Covered By"] = rela.is_covered_by(element, covering_relationships)
            relationships_data["Has Openings"] = rela.openings(element, void_relationships)
            relationships_data["Assigned Groups"] = rela.group_assignments(element, group_relationships)
            element_data["Element Relationships"] = relationships_data

            # --- LOCATION ---
            location_data = {}
            location_data["Storeys Map"] = sorted_storey_map
            location_data["Element Located in Storey"] = loc.element_storey_name(element)
            location_data["Spatial Relationship"] = loc.extract_full_spatial_hierarchy(element, spatial_relationships, parent_lookup, hierarchy_tree)
            element_data["Element Location"] = location_data

            # --- EXPORT ---
            base_name = meta.name(element) or "Unnamed"

            if base_name not in used_names:
                used_names[base_name] = 0
                final_name = base_name
            else:
                used_names[base_name] += 1
                final_name = f"{base_name}_{used_names[base_name]}"


            # Choose directory based on is_decompsed_by
            if is_decomposed_by:
                inout.save_individual_json(element_data, out_directory_compositions, final_name)
                count_composition_elements += 1
            else:     
                inout.save_individual_json(element_data, out_directory_elements, final_name)
                count_single_elements += 1

        except Exception as e:
            name = meta.name(element) or "Unnamed"
            globalid = meta.globalid(element) or "No GlobalId"
            print(f"Error processing element: Name='{name}', GlobalId='{globalid}'")
            print(f"Exception: {e}")
            continue
    
    # Add composition and skipped element counters to metadata
    file_metadata["Module 01: Data Extraction"] = {
        "Module 01a: Extract All Elements": {
            "Building Elements with Childern (Disregarded for inference)": count_composition_elements,
            "Building Elements without Childern": count_single_elements,
            "Skipped Elements due to Configuration": count_skipped_elements,
            "BREP Timeouts": brep_timeouts
        }
    }

    # Export the Metadata JSON file
    file_metadata_output_path = os.path.join(out_directory_boq, "metadata_step_01a.json")
    with open(file_metadata_output_path, "w", encoding="utf-8") as jsonfile:
        json.dump(file_metadata, jsonfile, indent=4)