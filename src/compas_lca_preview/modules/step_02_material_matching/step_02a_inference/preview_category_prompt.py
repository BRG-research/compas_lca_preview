# This is a prompt previewer!
from pathlib import Path
from .methods.utils import load_yaml_config
from .methods.prompt_builder_category import build_category_prompt
import compas_lca_preview

def preview_category_prompt(master_config_path):

    if master_config_path is None:
        master_config_path = Path(f"{compas_lca_preview.HERE}/configs/master_config.yaml")

    config = load_yaml_config(master_config_path)

    # Set dummy
    mode = "element"
    bim_element = "IFC Data of Iterated Element / Target Layer (as filtered by the user)"
    category_entries = "List of Category Entries of the Current Node (kbob or oekobaudat)"

    # Build the prompt
    prompt = build_category_prompt(
        bim_element=bim_element,
        category_entries=category_entries,
        mode=mode,
        config = config
    )

    return prompt
