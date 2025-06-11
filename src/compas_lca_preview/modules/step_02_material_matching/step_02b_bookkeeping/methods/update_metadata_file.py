import json
from pathlib import Path
from .utils import load_yaml_config

def update_metadata(metadata_input_path, directories_to_scan, metadata_output_path, config):
    keys_to_sum = [
        "total_tokens",
        "total_prompt_tokens",
        "total_completion_tokens",
        "total_processing_time",
        "total_cost_usd"
    ]

    totals = {key: 0 for key in keys_to_sum}
    category_count = 0
    material_count = 0

    for directory in directories_to_scan:
        dir_path = Path(directory)
        for file in dir_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    
                    # Sum metrics
                    for key in keys_to_sum:
                        totals[key] += data.get(key, 0)

                    # Count matched types
                    for step in data.get("inference_steps", []):
                        matched_type = step.get("matched_type", "").lower()
                        if matched_type == "category":
                            category_count += 1
                        elif matched_type == "material":
                            material_count += 1

                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON file: {file}")

    # Round totals to 3 decimal places with clean float formatting
    for key in totals:
        value = round(totals[key], 3)
        totals[key] = float(f"{value:.3f}")

    # Load preexisting metadata
    with open(metadata_input_path, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    # Load YAML config and extract prompt settings
    category_settings = config.get("category_prompt_variables", {})
    material_settings = config.get("material_prompt_variables", {})
    database_settings = config.get("database_config", {})
    
    # Extract category config values
    category_inference_config = config.get("category_inference_config", {})
    category_settings["company"] = category_inference_config.get("company", "")
    category_settings["model"] = category_inference_config.get("model", "")
    category_settings["temperature"] = category_inference_config.get("temperature", "")

    # Extract material config values
    material_inference_config = config.get("material_inference_config", {})
    material_settings["company"] = material_inference_config.get("company", "")
    material_settings["model"] = material_inference_config.get("model", "")
    material_settings["temperature"] = material_inference_config.get("temperature", "")

    # Extract database config value
    database_used = database_settings.get("database", "")

    # Create nested module dictionary
    module_02a_data = {
        "LCA database used for inference": database_used,
        "Tokens and Cost for Entire Inference Process": totals,
        "Category Inference Counts": category_count,
        "Material Inference Counts": material_count,
        "Category Prompt Settings": category_settings,
        "Material Prompt Settings": material_settings
    }

    # Add to existing metadata
    existing_data["Module 02: LLM Inference"] = module_02a_data


    # Save output
    metadata_output_path = Path(metadata_output_path)
    metadata_output_path.mkdir(parents=True, exist_ok=True)
    output_file = metadata_output_path / "metadata_step_02b.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
