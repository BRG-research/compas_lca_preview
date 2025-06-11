import os
import json

# Function that selects one representative element per compilation ID from overview and copies it to the compiled folder
def selector(source_folder, overview_path, elements_compiled_folder):
    # Make sure destination folder exists
    os.makedirs(elements_compiled_folder, exist_ok=True)

    # Load compiled overview
    with open(overview_path, "r", encoding="utf-8") as file:
        compiled_overview = json.load(file)

    copied_count = 0  # Counter for number of representative elements copied

    # Loop over compilation groups
    for compilation_id, compilation_data in compiled_overview.items():
        if "Elements" in compilation_data and compilation_data["Elements"]:
            first_element = compilation_data["Elements"][0]
            name = first_element["Name"]

            # Search for the original file in source folder
            for filename in os.listdir(source_folder):
                if filename.endswith(".json"):
                    source_path = os.path.join(source_folder, filename)
                    try:
                        with open(source_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            element_metadata = data.get("Element Metadata", {})

                            if element_metadata.get("Name") == name:
                                # Inject CompilationGroupID into the data
                                data["CompilationGroupID"] = compilation_id

                                # Save the modified JSON to compiled folder under the ORIGINAL filename
                                destination_path = os.path.join(elements_compiled_folder, filename)
                                with open(destination_path, "w", encoding="utf-8") as out_file:
                                    json.dump(data, out_file, indent=4, ensure_ascii=False)

                                copied_count += 1  # Increment counter
                                break  # Once found and saved, break inner loop
                    except (json.JSONDecodeError, KeyError):
                        continue  # Skip bad files

    print(f"Total representative elements copied: {copied_count}")

