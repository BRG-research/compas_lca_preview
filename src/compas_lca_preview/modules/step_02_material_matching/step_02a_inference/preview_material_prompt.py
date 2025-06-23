# This is a prompt previewer!
from pathlib import Path
from .methods.utils import load_yaml_config
from .methods.prompt_builder_material import build_material_prompt
import compas_lca_preview

def preview_material_prompt(master_config_path):

    if master_config_path is None:
        master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")

    config = load_yaml_config(master_config_path)

    # Set dummy
    mode = "element"
    category = "None"
    bim_element = "IFC Data of Iterated Element / Target Layer (as filtered by the user)"
    material_entries = "List of Material Entries of the Inferred Category (kbob or oekobaudat)"

    # Build the prompt
    prompt = build_material_prompt(
        bim_element=bim_element,
        material_entries=material_entries,
        mode=mode,
        category=category,
        config = config
    )

    return prompt
