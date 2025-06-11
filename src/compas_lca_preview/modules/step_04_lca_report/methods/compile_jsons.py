import json
import shutil
from pathlib import Path
from collections import defaultdict, OrderedDict
import re


def compile_elements(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for json_file in input_dir.rglob("*.json"):
        with open(json_file, encoding="utf-8-sig") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {json_file}")
                continue

        # === Strip _indicators or _emissions from filename ===
        original_name = json_file.stem
        if original_name.endswith("_indicators"):
            new_name = original_name[:-11]
        elif original_name.endswith("_emissions"):
            new_name = original_name[:-10]
        else:
            new_name = original_name

        output_path = output_dir / f"{new_name}.json"

        if "GlobalId" in data:
            # Ensure "Name" is first
            ordered = OrderedDict()
            if "Name" in data:
                ordered["Name"] = data.pop("Name")
            for k, v in data.items():
                ordered[k] = v

            with open(output_path, "w", encoding="utf-8-sig") as outf:
                json.dump(ordered, outf, indent=2, ensure_ascii=False)

        elif "CompilationGroupID" in data:
            # Rename "Name" to "ObjectType Name"
            if "Name" in data:
                data["ObjectType Name"] = data.pop("Name")

            # Ensure "ObjectType Name" is first
            ordered = OrderedDict()
            if "ObjectType Name" in data:
                ordered["ObjectType Name"] = data.pop("ObjectType Name")
            for k, v in data.items():
                ordered[k] = v

            with open(output_path, "w", encoding="utf-8-sig") as outf:
                json.dump(ordered, outf, indent=2, ensure_ascii=False)

        else:
            continue




def compile_target_layers(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    grouped_files = defaultdict(list)

    # Step 1: Group files by base object (without _L{n}_suffix)
    pattern = re.compile(r"(.*)_L(\d+)_.*\.json")
    for json_file in input_dir.rglob("*.json"):
        match = pattern.match(json_file.name)
        if match:
            base_name = match.group(1)
            layer_num = int(match.group(2))
            grouped_files[base_name].append((layer_num, json_file))

    # Step 2: Process each group
    for base_name, files in grouped_files.items():
        combined = OrderedDict()

        # Sort files by layer number
        files.sort()

        for layer_num, file_path in files:
            with open(file_path, encoding="utf-8-sig") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file_path}")
                    continue

            # Set top-level name & ID (stripped of _L{n})
            if not combined:
                name = data.get("Name", "")
                cleaned_name = re.sub(r"_L\d+$", "", name)
                compilation_id = re.sub(r"_L\d+$", "", data.get("CompilationGroupID", ""))
                combined["ObjectType Name"] = cleaned_name
                combined["CompilationGroupID"] = compilation_id

            # Add layer data
            layer_key = f"Layer {layer_num}"
            layer_data = OrderedDict()
            if "Volume [m^3]" in data:
                layer_data["Volume [m^3]"] = data["Volume [m^3]"]
            if "Largest Surface Area [m^2]" in data:
                layer_data["Largest Surface Area [m^2]"] = data["Largest Surface Area [m^2]"]

            # Find the emissions indicator field (KBOB or OEKOBAUDAT)
            matched_keys = [k for k in data if k.startswith("Matched Materials with")]
            if matched_keys:
                layer_data[matched_keys[0]] = data[matched_keys[0]]

            combined[layer_key] = layer_data

        # Step 3: Write to new JSON file
        output_file = output_dir / f"{base_name}.json"
        with open(output_file, "w", encoding="utf-8-sig") as out_f:
            json.dump(combined, out_f, indent=2, ensure_ascii=False)
