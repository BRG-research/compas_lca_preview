from .methods.utils import append_id, load_yaml_config
from .methods.summarize_results import summarize_inferences
from .methods.update_metadata_file import update_metadata
from pathlib import Path
import compas_lca_preview

def bookkeeper(project_path=None, master_config_path=None):


    # Root folders of all unfiltered source files
    source_root_elements = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/Elements")
    source_root_target_layers = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/Target_Layers")

    # Metadata file path
    metadata_file_path = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/metadata_step_01c.json")

    # Master config path
    if master_config_path is None:
        master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")
    master_config = load_yaml_config(master_config_path)
    config_database = master_config.get("database_config", {}).get("database")

    # Specify custom path such that both databases can be used and compared simulataneously
    if config_database == "kbob":

        # Root folders of all (step-wise) inferences
        inference_root_elements = Path(f"{project_path}/step_02_material_matching/step_02a_inference/kbob/Elements")
        inference_root_target_layers = Path(f"{project_path}/step_02_material_matching/step_02a_inference/kbob/Target_Layers")

        # Output folders for summaries
        output_elements = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/kbob/Elements")
        output_target_layers = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/kbob/Target_Layers")

        # Metadata output path
        metadata_output_path = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/kbob")

    else:

        # Root folders of all (step-wise) inferences
        inference_root_elements = Path(f"{project_path}/step_02_material_matching/step_02a_inference/oekobaudat/Elements")
        inference_root_target_layers = Path(f"{project_path}/step_02_material_matching/step_02a_inference/oekobaudat/Target_Layers")

        # Output folders for summaries
        output_elements = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/oekobaudat/Elements")
        output_target_layers = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/oekobaudat/Target_Layers")

        # Metadata output path
        metadata_output_path = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/oekobaudat")

    print(f"Summary of inferences save at {metadata_output_path}")


    # summarize inferences
    summarize_inferences(inference_root_elements, output_elements, master_config)
    summarize_inferences(inference_root_target_layers, output_target_layers, master_config)

    # Append GroupId or GlobalId to inference files for overview
    append_id(output_elements, source_root_elements)
    append_id(output_target_layers, source_root_target_layers)

    # update metadata file with totals and LLM metadata
    update_metadata(
        metadata_input_path=metadata_file_path,
        directories_to_scan=[output_elements, output_target_layers],
        metadata_output_path=metadata_output_path,
        config=master_config)

if __name__ == "__main__":
    bookkeeper()