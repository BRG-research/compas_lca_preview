from .methods.multiply import calculate_gross_emissions
from pathlib import Path
from .methods.utils import load_yaml_config
from .methods.update_boq import append_emissions_to_csv

import compas_lca_preview


def gross_emissions(project_path=None, master_config_path=None):

    # Input BoQ CSV file
    input_boq = Path(f"{project_path}/step_01_data_extraction/step_01c_dissect_layers/BoQ_step_01c.csv")

    # Master config path
    if master_config_path is None:
        master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")
    master_config = load_yaml_config(master_config_path)
    config_database = master_config.get("database_config", {}).get("database")

    if config_database == "kbob":
        element_indicators = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/kbob/Elements")
        target_layer_indicators = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/kbob/Target_Layers")
        output_base_dir = Path(f"{project_path}/step_03_lca_calculation/step_03b_gross_emissions/kbob")
        output_csv = Path(f"{project_path}/step_03_lca_calculation/step_03b_gross_emissions/kbob/BoQ.csv")

    else:
        element_indicators = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/oekobaudat/Elements")
        target_layer_indicators = Path(f"{project_path}/step_03_lca_calculation/step_03a_specific_indicators/oekobaudat/Target_Layers")
        output_base_dir = Path(f"{project_path}/step_03_lca_calculation/step_03b_gross_emissions/oekobaudat")
        output_csv = Path(f"{project_path}/step_03_lca_calculation/step_03b_gross_emissions/oekobaudat/BoQ.csv")

    calculate_gross_emissions(
        input_dirs=[element_indicators, target_layer_indicators], 
        output_base_dir=output_base_dir,
        input_boq_csv=input_boq)
    append_emissions_to_csv(input_boq, output_base_dir, output_csv, config_database)

if __name__ == "__main__":
    gross_emissions()
    
