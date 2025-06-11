# runner.py
import os
import json
from pathlib import Path
from .methods.utils import create_inference_folders, load_yaml_config, simplify_category_list, simplify_material_lists, simplify_material_lists_density, simplify_lci_lists_oekobaudat
from .methods.traverse import traverse_lci_hierarchy

import compas_lca_preview

def match_bim_files(input_dir, output_dir, lci_base_dir, mode_label, config):
    for filename in os.listdir(input_dir):
        if not filename.endswith(".json"):
            continue
        element_id = os.path.splitext(filename)[0]
        element_path = os.path.join(input_dir, filename)
        results_dir = os.path.join(output_dir, element_id)
        os.makedirs(results_dir, exist_ok=True)
        with open(element_path, "r", encoding="utf-8") as f:
            bim_element = json.load(f)
        print(f"> Processing {mode_label.upper()} → {element_id}")
        result = traverse_lci_hierarchy(
            bim_element=bim_element,
            current_dir=lci_base_dir,
            lci_base_dir=lci_base_dir,
            mode=mode_label,
            results_dir=results_dir,
            config=config,
            step=1,
            path_trace = None
        )


def material_matcher(project_path=None):

    # setup paths & directories
    input_elements = Path(f"{project_path}/step_01_data_extraction/step_01d_filter_data/Elements")
    input_target_layers = Path(f"{project_path}/step_01_data_extraction/step_01d_filter_data/Target_Layers")
    master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")
    master_config = load_yaml_config(master_config_path)
    config_database = master_config.get("database_config", {}).get("database")

    # Specify custom path such that both databases can be used and compared simulataneously
    if config_database == "kbob":
        inference_elements_folders = Path(f"{project_path}/step_02_material_matching/step_02a_inference/kbob/Elements")
        inference_target_layers_folders = Path(f"{project_path}/step_02_material_matching/step_02a_inference/kbob/Target_Layers")
    else:
        inference_elements_folders = Path(f"{project_path}/step_02_material_matching/step_02a_inference/oekobaudat/Elements")
        inference_target_layers_folders = Path(f"{project_path}/step_02_material_matching/step_02a_inference/oekobaudat/Target_Layers")

    # create folders for each element/target layer for recursive inference process
    create_inference_folders(input_elements, inference_elements_folders)
    create_inference_folders(input_target_layers, inference_target_layers_folders)

    # Get configurations from master_config.yaml
    var_include_density = master_config.get("material_prompt_variables", {}).get("include_density")

    # Simplify Index lists and make them LLM friendly (by minimizing tokens and irrelevant information)
    if config_database == "kbob":
        lci_base_dir = Path(f"{compas_lca_preview.HERE}/LCI_database/KBOB")
        category_index_path = Path(f"{compas_lca_preview.HERE}/LCI_database/KBOB/index.json")
        simplify_category_list(category_index_path) 
        if var_include_density: 
            simplify_material_lists_density(lci_base_dir)
        else:
            simplify_material_lists(lci_base_dir)
    else:
        lci_base_dir = Path(f"{compas_lca_preview.HERE}/LCI_database/OEKOBAUDAT")
        category_index_path = Path(f"{compas_lca_preview.HERE}/LCI_database/OEKOBAUDAT/index.json")
        simplify_lci_lists_oekobaudat(lci_base_dir, var_include_density)
    
    # Match elements
    match_bim_files(
        input_dir=input_elements,
        output_dir=inference_elements_folders,
        lci_base_dir=lci_base_dir,
        mode_label="element",
        config = master_config
    )

    # Match target layers
    match_bim_files(
        input_dir=input_target_layers,
        output_dir=inference_target_layers_folders,
        lci_base_dir=lci_base_dir,
        mode_label="layer",
        config = master_config
    )

if __name__ == "__main__":
    material_matcher()
