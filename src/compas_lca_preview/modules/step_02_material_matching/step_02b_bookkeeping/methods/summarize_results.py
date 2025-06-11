import json
from pathlib import Path
from .costs import get_token_cost
import os

def summarize_inferences(base_dir, output_dir, config):
    base_dir = Path(base_dir)

    model_category = config.get("category_inference_config", {}).get("model")
    model_material = config.get("material_inference_config", {}).get("model")

    for element_dir in base_dir.iterdir():
        if not element_dir.is_dir():
            continue

        summary = {
            "name": element_dir.name,
            "total_steps": 0,
            "total_tokens": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_processing_time": 0.0,
            "total_cost_usd": 0.0,
            "inference_steps": [],
            "llm_responses_raw": []  # New key for grouped responses
        }

        for file in sorted(element_dir.iterdir()):
            if not file.name.endswith(".json") or file.name.startswith("summary"):
                continue

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            meta = data.get("llm_metadata", {})
            llm_response = data.get("llm_response", {})

            matched_type = meta.get("matched_type")
            matched_name = None

            if matched_type == "category":
                matched_name = llm_response.get("Matched Category")
                model = model_category
            elif matched_type == "material":
                matched_name = llm_response.get("Matched Materials")
                model = model_material
            else:
                model = "unknown"

            token_usage = meta.get("token_usage", {})
            prompt_tokens = token_usage.get("prompt_tokens", 0)
            completion_tokens = token_usage.get("completion_tokens", 0)
            total_tokens = token_usage.get("total_tokens", 0)
            processing_time = meta.get("processing_time", 0.0)

            cost_rates = get_token_cost(model)
            step_cost = (
                (prompt_tokens / 1000) * cost_rates["prompt"] +
                (completion_tokens / 1000) * cost_rates["completion"]
            )

            summary["total_steps"] += 1
            summary["total_tokens"] += total_tokens
            summary["total_prompt_tokens"] += prompt_tokens
            summary["total_completion_tokens"] += completion_tokens
            summary["total_processing_time"] += round(processing_time, 6)
            summary["total_cost_usd"] += round(step_cost, 6)

            summary["inference_steps"].append({
                "step": meta.get("step"),
                "matched_type": matched_type,
                "matched_name": matched_name,
                "matched_path": meta.get("matched_path"),
                "message": meta.get("message"),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "processing_time": processing_time,
                "llm_model": model,
                "inference_cost_usd": round(step_cost, 6)
            })

            step_num = meta.get("step", summary["total_steps"])
            summary["llm_responses_raw"].append({
                "step": step_num,
                "response": llm_response
            })

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        summary_path = output_dir / f"{summary['name']}_inference.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
