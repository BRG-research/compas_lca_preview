from pathlib import Path
from .methods.aggregator import aggregator_element, aggregator_boq, aggregator_metadata
from .methods.selector import selector

def aggregate_elements(project_path=None):

    # Source folder of all extracted elements
    source_folder = Path(f"{project_path}/step_01_data_extraction/step_01a_extract_all/Elements")

    # Path to the BoQ of all elements
    boq_path = Path(f"{project_path}/step_01_data_extraction/step_01a_extract_all/BoQ_step_01a.csv")

    # This folder saves the elements that did not fulfill the compilement criteria and require unique inference
    elements_unique_folder = Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/Elements_Unique")

    # The folder where the ONE representative element that fulfilled the compilement criteria will be saved
    elements_compiled_folder = Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/Elements_Aggregated")

    # The folder where the overview of all compiled elements and the updated BOQ will be saved
    data_folder = Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements")

    # Reference the metadata JSON sheet
    metadata_path = Path(f"{project_path}/step_01_data_extraction/step_01a_extract_all/metadata_step_01a.json")

    # Run the compiler (compiles elemenets into groups based on type, object type, material data, and material layers)
    # Copies elements that do not fulfill the compilement criteria separately
    # It also returns the overview path of the compiled elements for the selector
    overview_path, groups_count, total_compiled_elements, total_unique_elements = aggregator_element(source_folder, elements_unique_folder, data_folder)

    # Run the selector (selects one representative element per compilation ID from overview and copies it to the compiled folder)
    # This element is then used for LLM inference, and its results are then assigned to all elements in the group
    selector(source_folder, overview_path, elements_compiled_folder)

    # Run the updated BoQ with the compilations
    aggregator_boq(boq_path, overview_path, data_folder)

    # Update the metadata sheet
    aggregator_metadata(metadata_path, groups_count, total_compiled_elements, total_unique_elements, data_folder)

if __name__ == "__main__":
    aggregate_elements()
