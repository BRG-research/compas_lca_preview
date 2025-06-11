import copy
import os
import json
import time
from .utils import load_json
from .llm_interface import category_inference, material_inference

def traverse_lci_hierarchy(bim_element, current_dir, lci_base_dir, results_dir, mode, config, step=1, path_trace=None):

    path_trace = path_trace or []

    category_file = os.path.join(current_dir, "llm_categories.json")
    materials_file = os.path.join(current_dir, "llm_materials.json")
    index_file = os.path.join(current_dir, "index.json")

    if not os.path.exists(index_file):
        raise FileNotFoundError(f"Missing index.json in {current_dir}")

    index_data = load_json(index_file)

    # === Category Inference ===
    if os.path.exists(category_file):
        lci_data = load_json(category_file)

        # Actual inference
        start_time = time.time()
        llm_response, token_usage = category_inference(bim_element, lci_data, mode, config)
        end_time = time.time()
        processing_time = round(end_time - start_time, 3)

        # Get match name
        category_name = llm_response.get("Matched Category")
        if category_name in [None, "None", "", []]:
            category_name = None

        # Token usage and cost calculation
        token_data = token_usage.to_dict()
        prompt_tokens = token_data.get("prompt_tokens", 0)
        completion_tokens = token_data.get("completion_tokens", 0)

        # Apply modular logic here later, this is only for GPT-4o
        cost_per_1k_prompt = 0.005
        cost_per_1k_completion = 0.02
        total_cost = round(
            (prompt_tokens * cost_per_1k_prompt / 1000) +
            (completion_tokens * cost_per_1k_completion / 1000), 6
        )

        # Get model settings metadata from config
        category_config = config.get("category_inference_config", {})
        company_category_inference = category_config.get("company")
        model_category_inference = category_config.get("model")

        # Append metadata
        metadata = {
            "step": step,
            "matched_type": "category",
            "matched_path": str(current_dir),
            "trace": path_trace,
            "message": "Match successful" if category_name else "No match found",
            "token_usage": token_usage.to_dict(),
            "processing_time": processing_time,
            "company": company_category_inference,
            "model": model_category_inference,
            "inference_cost_usd": total_cost
        }

        result = {
            "llm_response": llm_response,
            "llm_metadata": metadata
        }

        result_path = os.path.join(results_dir, f"step_{step}_category.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if not category_name:
            return result

        match = next((item for item in index_data["items"] if item["name"] == category_name), None)
        if not match:
            result["llm_metadata"]["matched_type"] = "none"
            result["llm_metadata"]["message"] = f"No match for '{category_name}' in index.json"
            return result

        next_dir = os.path.join(current_dir, os.path.dirname(match["path"]))

        return traverse_lci_hierarchy(
            bim_element=bim_element,
            current_dir=next_dir,
            lci_base_dir=lci_base_dir,
            results_dir=results_dir,
            mode=mode,
            config=copy.deepcopy(config),
            step=step + 1,
            path_trace=path_trace + [category_name]
        )

    # === Material inference (leaf node) ===
    elif os.path.exists(materials_file):
        lci_data = load_json(materials_file)

        # Load the last "trace", which is the last category name. With this, conditionals can be set for context-aware examples on material nodes
        category = path_trace[-1] if path_trace else None

        start_time = time.time()
        llm_response, token_usage = material_inference(bim_element, lci_data, mode, config, category)
        end_time = time.time()
        processing_time = round(end_time - start_time, 3)

        matched_name = llm_response.get("Matched Materials")
        if matched_name in [None, "None", "", []]:
            matched_name = None

        # Token usage and cost calculation
        token_data = token_usage.to_dict()
        prompt_tokens = token_data.get("prompt_tokens", 0)
        completion_tokens = token_data.get("completion_tokens", 0)

        # Apply modular logic here later, this is only for GPT-4o
        cost_per_1k_prompt = 0.005
        cost_per_1k_completion = 0.02
        total_cost = round(
            (prompt_tokens * cost_per_1k_prompt / 1000) +
            (completion_tokens * cost_per_1k_completion / 1000), 6
        )

        # Get model settings metadata from config
        material_config = config.get("material_inference_config", {})
        company_material_inference = material_config.get("company")
        model_material_inference = material_config.get("model")

        # Append metadata
        metadata = {
            "step": step,
            "matched_type": "material",
            "matched_path": str(current_dir),
            "trace": path_trace,
            "message": "Match successful" if matched_name else "No match found",
            "token_usage": token_usage.to_dict(),
            "processing_time": processing_time,
            "company": company_material_inference,
            "model": model_material_inference,
            "inference_cost_usd": total_cost
        }

        result = {
            "llm_response": llm_response,
            "llm_metadata": metadata
        }

        result_path = os.path.join(results_dir, f"step_{step}_material_match.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    # Gracefully handle if matching inference file found
    else:
        result = {
            "llm_response": {},
            "llm_metadata": {
                "step": step,
                "matched_type": "none",
                "matched_name": None,
                "matched_path": str(current_dir),
                "trace": path_trace,
                "message": "No llm_categories.json or llm_materials.json found in directory",
                "token_usage": {},
                "processing_time": 0.0
            }
        }

        result_path = os.path.join(results_dir, f"step_{step}_no_match.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result