# This is a prompt previewer!
from pathlib import Path
from methods.utils import load_yaml_config
from methods.prompt_builder_category import build_category_prompt

master_config_path = Path("config/master_config.yaml")
config = load_yaml_config(master_config_path)
output_path = Path("data/output/prompt_preview/category_prompt.txt")

def preview_category_prompt():

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

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(prompt, encoding="utf-8")

if __name__ == "__main__":
    preview_category_prompt()
    print("\n")
    print("=================================")
    print("Category prompt preview saved to:")
    print(output_path)
    print("=================================")
    print("\n")