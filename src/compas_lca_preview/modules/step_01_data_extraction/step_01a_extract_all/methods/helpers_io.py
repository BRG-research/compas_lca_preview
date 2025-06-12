from compas_ifc.model import Model
import os
import re
import json
import yaml
from pathlib import Path

# Function to load an IFC file using COMPAS-IFC
def load_ifc_file(filepath, brep_toggle):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The file '{filepath}' does not exist.")
    try:
        model = Model(filepath, use_occ=brep_toggle, load_geometries=brep_toggle)  # COMPAS-IFC Model class
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to load IFC file: {e}")


# Replace illegal filename characters with "-", preserving unicode like umlauts.
def sanitize_filename(name):
    if not name:
        return "UnnamedElement"
    cleaned = re.sub(r'[^\w\säöüÄÖÜß-]', '-', name, flags=re.UNICODE)
    return cleaned.replace(" ", "-")

# Save each IfcElement's extracted data into a separate JSON file
def save_individual_json(element_data, output_directory, element_name):
    """
    Saves the given element_data to a JSON file named after the element's name,
    with illegal characters replaced by "-". Allows UTF-8 characters like umlauts.
    """
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    # Get element name and sanitize it for filesystem use
    sanitized_name = sanitize_filename(element_name)
    # Construct full file path
    filename = f"{sanitized_name}.json"
    filepath = os.path.join(output_directory, filename)
    # Write JSON file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(element_data, f, indent=4, ensure_ascii=False)

# Recursively cleans dictionary data by removing unwanted values
# At the top/root level, certain keys are preserved even if empty
def clean_dict(data, preserve_keys_at_root=None, level=0):

    unwanted_values = ["Unknown", "Not defined", None]

    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            v_clean = clean_dict(v, preserve_keys_at_root, level=level+1)

            # Special logic for root level
            if level == 0 and preserve_keys_at_root:
                if k in preserve_keys_at_root:
                    cleaned[k] = v_clean if v_clean != {} else {}
                elif v_clean not in unwanted_values and v_clean != {} and v_clean != []:
                    cleaned[k] = v_clean
            else:
                if v_clean not in unwanted_values and v_clean != {} and v_clean != []:
                    cleaned[k] = v_clean
        return cleaned

    elif isinstance(data, list):
        cleaned = [clean_dict(v, preserve_keys_at_root, level=level+1) for v in data]
        cleaned = [v for v in cleaned if v not in unwanted_values and v != {} and v != []]
        return cleaned

    else:
        return data


def get_single_ifc_file():
    ifc_dir = Path("data/input/IFC_model")
    ifc_files = list(ifc_dir.glob("*.ifc"))

    if len(ifc_files) != 1:
        raise FileNotFoundError(f"Expected exactly one IFC file in {ifc_dir.resolve()}, but found {len(ifc_files)}.")

    return ifc_files[0]


# Loads the 'Extraction Configuration' section from a YAML file.
def load_yaml_config(yaml_path):
    with open(yaml_path, "r") as f:
        config_data = yaml.safe_load(f)
    return config_data