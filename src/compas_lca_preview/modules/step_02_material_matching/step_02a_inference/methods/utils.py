# utils.py
import json
import os
import yaml

def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json_files_from_directory(dir_path):
    files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    return [load_json(os.path.join(dir_path, f)) for f in files]


def create_inference_folders(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if not filename.endswith(".json") or filename == ".gitkeep":
            continue
        element_id = os.path.splitext(filename)[0]
        element_folder_path = os.path.join(output_dir, element_id)
        os.makedirs(element_folder_path, exist_ok=True)



# Extracts a simplified, Pythonic list of material categories
def simplify_category_list(category_index_path):
    with open(category_index_path, 'r', encoding='utf-8') as f:
        db_index = json.load(f)
    
    # Extract just the names into a list of strings
    category_names = [item["name"] for item in db_index.get("items", [])]

    # Deduplicate and sort
    category_names = sorted(set(category_names), key=str.casefold)

    # Save as JSON object with a key
    base_dir = os.path.dirname(category_index_path)
    output_path = os.path.join(base_dir, "llm_categories.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"categories": category_names}, f, indent=2, ensure_ascii=False)

    return category_names

# Recursively traverses the material database and returns/writes a flat list of material names
def simplify_material_lists(base_dir):
    processed_paths = []

    for root, dirs, files in os.walk(base_dir):
        # Skip non-leaf directories
        if dirs:
            continue
        if "index.json" not in files:
            continue

        index_path = os.path.join(root, "index.json")
        output_path = os.path.join(root, "llm_materials.json")

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue

        material_names = [
            item.get("Name") for item in data.get("items", []) if item.get("Name")
        ]

        material_names = sorted(set(material_names), key=str.casefold)
        material_names = material_names[:40] # Limit to 40 such that token limit not exceeded

        try:
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump({"material_options": material_names}, out_f, indent=2, ensure_ascii=False)
            processed_paths.append(root)
        except Exception:
            pass

    return processed_paths



# Recursively traverses a material database directory structure and creates dictionary of material entries with densities from an index.json
def simplify_material_lists_density(base_dir):
    processed_paths = []

    for root, dirs, files in os.walk(base_dir):
        # Skip folders that contain other subfolders — only process leaf folders
        if dirs:
            continue
        if "index.json" not in files:
            continue 
        index_path = os.path.join(root, "index.json")
        llm_output_path = os.path.join(root, "llm_materials.json")
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        material_entries = []
        for item in data.get("items", []):
            name = item.get("Name")
            if not name:
                continue
            entry = {
                "Name": name
            }
            density = item.get("Density (kg/m3)")
            if density:
                try:
                    entry["Density [kg/m³]"] = float(density)
                except ValueError:
                    entry["Density [kg/m³]"] = density
            material_entries.append(entry)
        material_entries = material_entries[:30] # Limit to 30 such that token limit not exceeded, less than without density (since more tokens)
        llm_data = {"Material Options": material_entries}
        try:
            with open(llm_output_path, 'w', encoding='utf-8') as out_f:
                json.dump(llm_data, out_f, indent=2, ensure_ascii=False)
            processed_paths.append(root)
        except Exception:
            pass
    return processed_paths




def simplify_lci_lists_oekobaudat(base_dir, include_density=False):
    processed_paths = []

    for root, dirs, files in os.walk(base_dir):
        if "index.json" not in files:
            continue

        index_path = os.path.join(root, "index.json")
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue

        index_type = data.get("type")
        items = data.get("items", [])

        if index_type == "materials":
            MAX_MATERIALS = 40 if not include_density else 30

            material_entries = []
            for item in items:
                name = item.get("Name")
                if not name:
                    continue

                if include_density:
                    entry = {"Name": name}
                    density = item.get("Density (kg/m3)")
                    if density:
                        try:
                            entry["Density [kg/m³]"] = float(density)
                        except ValueError:
                            entry["Density [kg/m³]"] = density
                    material_entries.append(entry)
                else:
                    material_entries.append(name)

            llm_data = {"Material Options": material_entries[:MAX_MATERIALS]}
            output_path = os.path.join(root, "llm_materials.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(llm_data, f, indent=2, ensure_ascii=False)
            processed_paths.append(output_path)

        elif index_type in ("categories", "mixed"):
            category_entries = [item["name"] for item in items if "name" in item]
            llm_data = {"Material Categories": category_entries}
            output_path = os.path.join(root, "llm_categories.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(llm_data, f, indent=2, ensure_ascii=False)
            processed_paths.append(output_path)

    return processed_paths
