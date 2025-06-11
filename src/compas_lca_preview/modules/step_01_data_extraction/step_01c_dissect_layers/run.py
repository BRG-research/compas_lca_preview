from pathlib import Path
from .methods.dissector import dissector_element, dissector_boq

def dissect_layers(project_path=None):

    # Config (iterate over all source directories)
    # Source elements
    source_dirs = [
        Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/Elements_Aggregated"),
        Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/Elements_Unique")
    ]

    # Source BOQ
    compiled_boq_path = Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/BoQ_step_01b.csv")

    # Source Metadata
    metadata_path = Path(f"{project_path}/step_01_data_extraction/step_01b_aggregate_elements/metadata_step_01b.json")

    # New elements directory (for elements with no or only 1 material layer)
    elements_directory = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/Elements")

    # Target Layer directory, for new JSON format of split multi-layer elements
    target_layer_directory = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/Target_Layers")

    # Directory for updated BoQ
    output_folder = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers")

    # Run the dissector for elements
    dissector_element(source_dirs, elements_directory, target_layer_directory, metadata_path, output_folder)

    # Run the dissector for BoQ and update
    dissector_boq(compiled_boq_path, target_layer_directory, elements_directory, output_folder)

if __name__ == "__main__":
    dissect_layers()