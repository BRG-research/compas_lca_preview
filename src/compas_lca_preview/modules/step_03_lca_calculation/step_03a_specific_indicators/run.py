from .methods.lca_kbob import extract_kbob_data
from .methods.lca_oekobaudat import extract_oekobaudat_data
from .methods.append_quantities import append_quantities
from .methods.utils import load_yaml_config
from pathlib import Path

import compas_lca_preview


def append_indicators(project_path=None, master_config_path=None):

    # Master config path
    if master_config_path is None:
        master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")
    master_config = load_yaml_config(master_config_path)
    config_database = master_config.get("database_config", {}).get("database")
    boq_path = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/BoQ_step_01c.csv")

    if config_database == "kbob":
        # Root folders of all (step-wise) inferences
        llm_elements = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/kbob/Elements")
        llm_target_layers = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/kbob/Target_Layers")

        # Output folders indicators enhanced
        output_base_dir = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/kbob")

    else:
        # Root folders of all (step-wise) inferences
        llm_elements = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/oekobaudat/Elements")
        llm_target_layers = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping/oekobaudat/Target_Layers")

        # Output folders indicators enhanced
        output_base_dir = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/oekobaudat")

    output_elements_dir = output_base_dir / "Elements"
    output_target_layers_dir = output_base_dir / "Target_Layers"

    print(f"Extracting indicators for {config_database} database")
    print(f"Output folder: {output_base_dir}")


    if config_database == "kbob":
        extract_kbob_data(
            input_dirs=[llm_elements, llm_target_layers], 
            output_base_dir=output_base_dir,
            selected_keys=None
        )
    else:
        extract_oekobaudat_data(
            input_dirs=[llm_elements, llm_target_layers], 
            output_base_dir=output_base_dir, 
            selected_keys=None
        )
    
    append_quantities(
        json_dirs=[output_elements_dir,output_target_layers_dir], 
        boq_path=boq_path, 
        database=config_database
        )

if __name__ == "__main__":
    
    append_indicators()
