# This is a prompt previewer!
from pathlib import Path
from methods.utils import load_yaml_config
from methods.prompt_builder_material import build_material_prompt

master_config_path = Path("config/master_config.yaml")
config = load_yaml_config(master_config_path)
output_path = Path("data/output/prompt_preview/material_prompt.txt")

def preview_material_prompt():

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

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(prompt, encoding="utf-8")

if __name__ == "__main__":
    preview_material_prompt()
    print("\n")
    print("=================================")
    print("Material prompt preview saved to:")
    print(output_path)
    print("=================================")
    print("\n")