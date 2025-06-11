import yaml
import shutil
from pathlib import Path
from datetime import datetime
import json
import shutil

def copy_metadata_to_report(config_database: str, metadata_output_dir: Path, project_path: Path):
    # Determine the source metadata path
    metadata_input_path = Path(f"{project_path}/step_02_material_matching/step_02b_bookkeeping") / config_database.lower() / "metadata_step_02b.json"
    output_file_path = metadata_output_dir / "compas_lca.json"

    if not metadata_input_path.exists():
        print(f"Metadata file not found: {metadata_input_path}")
        return

    # Read and load the original JSON
    with open(metadata_input_path, "r", encoding="utf-8-sig") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Invalid JSON format in: {metadata_input_path}")
            return

    # Add timestamp fields at the top
    now = datetime.now()
    annotated_data = {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
    }
    # Append rest of the data
    annotated_data.update(data)

    # Ensure output dir exists
    metadata_output_dir.mkdir(parents=True, exist_ok=True)

    # Save to new location
    with open(output_file_path, "w", encoding="utf-8-sig") as out_f:
        json.dump(annotated_data, out_f, indent=2, ensure_ascii=False)


def copy_boq_to_report(boq_source: Path, report_dir: Path):
    report_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    target = report_dir / "Bill_of_Quantities.csv"
    shutil.copy(boq_source, target)


def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)