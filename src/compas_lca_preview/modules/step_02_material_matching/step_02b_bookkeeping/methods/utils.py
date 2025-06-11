import os
import json
import yaml

def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Universal method to find GlobalID/GroupID regardless of element/target layer data format
def recursive_finder(data, target_keys):
    if isinstance(data, dict):
        for target_key in target_keys:
            if target_key in data:
                return target_key, data[target_key]
        for value in data.values():
            result = recursive_finder(value, target_keys)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = recursive_finder(item, target_keys)
            if result:
                return result
    return None


# Find GlobalId or GroupId and append to inference files
def append_id(inference_root, source_root):
    for filename in os.listdir(inference_root):
        if not filename.endswith("_inference.json"):
            continue

        # Derive the base element name (remove "_inference.json")
        element_name = filename.replace("_inference.json", "")
        source_file_path = os.path.join(source_root, f"{element_name}.json")

        if not os.path.exists(source_file_path):
            continue

        # Load source data to extract the ID
        with open(source_file_path, "r", encoding="utf-8") as f:
            source_data = json.load(f)

        result = recursive_finder(source_data, ["GlobalId"])
        if not result:
            continue

        id_key, id_value = result

        # Load the inference file
        inference_file_path = os.path.join(inference_root, filename)
        with open(inference_file_path, "r", encoding="utf-8") as f:
            inference_data = json.load(f)

        # Append the ID
        updated_data = {id_key: id_value}
        updated_data.update(inference_data)

        # Save back to the same file
        with open(inference_file_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=2)