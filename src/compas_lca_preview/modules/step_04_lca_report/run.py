from pathlib import Path
from .methods.utils import load_yaml_config, copy_boq_to_report, copy_metadata_to_report
from .methods.compile_jsons import compile_elements, compile_target_layers
from .methods.compile_positives_negatives import collect_match_status
from .methods.emissions_overview import generate_emission_totals
from .methods.plots import plot_indicators

import compas_lca_preview

def make_path(*parts):
    return Path(*parts)



def create_report(project_path=None):

    # Load config
    master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")
    master_config = load_yaml_config(master_config_path)
    config_database = master_config.get("database_config", {}).get("database")

    # Base path setup
    db = config_database.lower()
    pipeline_base = make_path(project_path, "step_03_lca_calculation")
    output_base = make_path(project_path, "step_04_lca_report")

    paths = {
        "boq_csv": pipeline_base / "step_03b_gross_emissions" / db / "BoQ.csv",
        "input_metadata": make_path(project_path, "step_02_material_matching", "step_02b_bookkeeping", db, "metadata_step_02b.json"),

        "input_elements": {
            "gross_emissions": pipeline_base / "step_03b_gross_emissions" / db / "Elements",
            "specific_indicators": pipeline_base / "step_03a_specific_indicators" / db / "Elements",
        },
        "input_target_layers": {
            "gross_emissions": pipeline_base / "step_03b_gross_emissions" / db / "Target_Layers",
            "specific_indicators": pipeline_base / "step_03a_specific_indicators" / db / "Target_Layers",
        },
        
        "output_elements": {
            "gross_emissions": output_base / "elements" / "gross_emissions",
            "specific_indicators": output_base / "elements" / "specific_emissions",
        },
        
        "output_metadata": output_base / "metadata",
        "output_report": output_base,
        
        "input_parent_dir": pipeline_base / "step_03a_specific_indicators" / db,
    }


    # Compile elements
    compile_elements(paths["input_elements"]["gross_emissions"], paths["output_elements"]["gross_emissions"])
    compile_elements(paths["input_elements"]["specific_indicators"], paths["output_elements"]["specific_indicators"])

    # Compile target layers
    compile_target_layers(paths["input_target_layers"]["gross_emissions"], paths["output_elements"]["gross_emissions"])
    compile_target_layers(paths["input_target_layers"]["specific_indicators"], paths["output_elements"]["specific_indicators"])

    # Collect match metadata
    collect_match_status(paths["input_parent_dir"], paths["output_metadata"])

    # Copy BoQ
    copy_boq_to_report(paths["boq_csv"], paths["output_report"])

    # Generate plots
    plot_indicators(paths["boq_csv"], paths["output_report"] / "plots", config_database)

    # Annotate metadata with LCA calculation totals
    copy_metadata_to_report(config_database, paths["output_metadata"], project_path)

    generate_emission_totals(
        csv_file=paths["boq_csv"],
        database_config=config_database,
        output_path=paths["output_report"]
    )

    
if __name__ == "__main__":
    create_report()