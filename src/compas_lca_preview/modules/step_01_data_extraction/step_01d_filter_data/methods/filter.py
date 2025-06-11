import yaml
import json
import os
import importlib.util



def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def clean_dict(data, preserve_keys_at_root=None, empty_values=None, level=0):
    if empty_values is None:
        empty_values = ["Not defined", "Unknown", [], {}]

    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            v_clean = clean_dict(v, preserve_keys_at_root, empty_values, level + 1)
            if level == 0 and preserve_keys_at_root and k in preserve_keys_at_root:
                cleaned[k] = v_clean  # Preserve even if empty
            elif v_clean not in empty_values and v_clean != {} and v_clean != []:
                cleaned[k] = v_clean
        return cleaned

    elif isinstance(data, list):
        cleaned_list = [clean_dict(item, preserve_keys_at_root, empty_values, level + 1) for item in data]
        return [item for item in cleaned_list if item not in empty_values and item != {} and item != []]

    else:
        return data


def decode_unicode(directory_path, recursive=False):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    pass
        if not recursive:
            break


def reorder_keys(data: dict, preferred_order: list) -> dict:
    ordered = {}
    for key in preferred_order:
        if key in data:
            ordered[key] = data[key]
    for key in data:
        if key not in ordered:
            ordered[key] = data[key]
    return ordered


def apply_element_filter(data, config):
    if not isinstance(data, dict):
        return data

    result = {}

    for key, rule in config.items():
        if key.startswith("_") or key not in data:
            continue

        value = data[key]

        if isinstance(rule, dict):
            if isinstance(value, dict):
                if rule.get("_include", True):
                    nested = apply_element_filter(value, rule)
                    if nested or nested == {}:
                        result[key] = nested

            elif isinstance(value, list):
                filtered_items = []

                for item in value:
                    if not isinstance(item, dict):
                        continue

                    # Determine rule based on IfcEntity or fallback to default item rule
                    if "IfcEntity" in item and item["IfcEntity"] in rule:
                        item_rule = rule[item["IfcEntity"]]
                    else:
                        item_rule = rule.get("item", rule)

                    if not item_rule.get("_include", True):
                        continue

                    # Apply filtering recursively
                    filtered = apply_element_filter(item, item_rule)
                    if filtered or filtered == {}:
                        filtered_items.append(filtered)

                if filtered_items or rule.get("_include", True):
                    result[key] = filtered_items

            else:
                # Scalar value inside a nested rule
                if rule.get("_include", True):
                    result[key] = value

        elif rule is True:
            result[key] = value

    return result


def filter_element_json(data, config, remove_empty=False):

    # hard-code keys to preserve (since some prompt variable specify these) & empty values 
    preserve_keys = [
        "Element Metadata",
        "Element Material Data",
        "Element Geometry Data",
        "Element Property Sets"
    ]
    empty_values = ["Not defined", "Unknown", [], {}, None]

    # Apply filtering
    filtered = apply_element_filter(data, {k: v for k, v in config.items() if not k.startswith("_")})

    # Clean result if requested
    if remove_empty:
        filtered = clean_dict(filtered, preserve_keys_at_root=preserve_keys, empty_values=empty_values)

    return filtered


def filter_target_layer_json(data, config, remove_empty=False):

    # hard-code keys to preserve (since some prompt variable specify these) & empty values 
    preserve_keys = [
        "Element Metadata",
        "Element Material Data",
        "Element Geometry Data",
        "Element Property Sets"
    ]
    empty_values = ["Not defined", "Unknown", [], {}, None]

    # Apply filtering
    filtered = apply_element_filter(data, {k: v for k, v in config.items() if not k.startswith("_")})

    # Clean result if requested
    if remove_empty:
        filtered = clean_dict(filtered, preserve_keys_at_root=preserve_keys, empty_values=empty_values)

    return filtered


def reorder_keys_target_layer(data, preferred_order):
    if not isinstance(data, dict):
        return data
    ordered = {k: data[k] for k in preferred_order if k in data}
    for k in data:
        if k not in ordered:
            ordered[k] = data[k]
    return ordered


# Methods for filtering of selected property sets
def load_selected_keys(py_file_path: str) -> set:
    spec = importlib.util.spec_from_file_location("pset_module", py_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.selected_keys)

def filter_psets(psets: dict, selected_keys: set) -> dict:
    def try_round(value):
        try:
            # Try converting string to float
            float_val = float(value)
            return str(round(float_val, 4))
        except (ValueError, TypeError):
            return value


    return {
        k: try_round(v) for k, v in psets.items()
        if k in selected_keys
    }

    
def apply_pset_filter(data: dict, selected_keys: set) -> dict:
    updated = False

    if "Element Property Sets" in data:
        for pset_name in ["Psets Object Type", "Psets Element"]:
            if pset_name in data["Element Property Sets"]:
                data["Element Property Sets"][pset_name] = filter_psets(
                    data["Element Property Sets"][pset_name], selected_keys
                )
                updated = True

    if "Building Element Context" in data and "Element Property Sets" in data["Building Element Context"]:
        for pset_name in ["Psets Object Type", "Psets Element"]:
            if pset_name in data["Building Element Context"]["Element Property Sets"]:
                data["Building Element Context"]["Element Property Sets"][pset_name] = filter_psets(
                    data["Building Element Context"]["Element Property Sets"][pset_name],
                    selected_keys
                )
                updated = True

    return data