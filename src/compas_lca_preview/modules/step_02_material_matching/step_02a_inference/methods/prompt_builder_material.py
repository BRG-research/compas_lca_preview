import json
from .prompt_components_material import material_prompt_components, material_prompt_components_ger

# Build dynamic prompt
def build_material_prompt(bim_element, material_entries, mode, category, config):

    # Load the inputs of the current element as strings
    ifc_string = json.dumps(bim_element, indent=2, ensure_ascii=False)

    # Corresponding material entries list
    materials_string = json.dumps(material_entries, indent=2, ensure_ascii=False)

    # Get database choice (context-aware examples for now only apply to kbob)
    database_config = config.get("database_config", {})
    database = database_config.get("database")

    # Get variables
    material_prompt_variables = config.get("material_prompt_variables", {})
    lng = material_prompt_variables.get("language")
    cot_bool = material_prompt_variables.get("chain_of_thought")
    etr_bool = material_prompt_variables.get("extract_then_reason")
    isr_bool = material_prompt_variables.get("iterative_self_refinement")
    exp_bool = material_prompt_variables.get("include_examples")
    matching_strictness = material_prompt_variables.get("matching_strictness")
    prio_sustainability = material_prompt_variables.get("prioritize_sustainability")


    # ============================================
    # English Prompt Lines
    # ============================================

    if lng == "en":

        # assign blocks based on bools
        cot = material_prompt_components["chain_of_thought"] if cot_bool else ""
        etr = material_prompt_components["extract_then_reason"] if etr_bool else ""
        isr = material_prompt_components["iterative_self_refinement"] if isr_bool else ""
        prs = material_prompt_components["prio_sustainability"] if prio_sustainability else ""

        # assign task framing prompt 
        if matching_strictness == "Mid":
            task_fr_1 = material_prompt_components["task_fr_mid_1"]
            task_fr_2 = material_prompt_components["task_fr_mid_2"]
        elif matching_strictness == "High":
            task_fr_1 = material_prompt_components["task_fr_high_1"]
            task_fr_2 = material_prompt_components["task_fr_high_2"]
        else: # Low is default fallback
            task_fr_1 = material_prompt_components["task_fr_low_1"]
            task_fr_2 = material_prompt_components["task_fr_low_2"]


        # construct dynamic output block
        output_format_map = {
            (False, False): material_prompt_components["output_format_baseline"],
            (True,  False): material_prompt_components["output_format_etr"],
            (False, True):  material_prompt_components["output_format_irs"],
            (True,  True):  material_prompt_components["output_format_etr_isr"],
        }
        output_block = output_format_map.get((etr_bool, isr_bool), material_prompt_components["output_format_baseline"])

        # Distinguish descriptor of first JSON file
        if mode == "target_layer":
            descriptor_1 = "a **Target Layer** of an IfcBuildingElement"
            descriptor_2 = "'Target Layer of Material Inference'"
        else:
            descriptor_1 = "an **IfcBuildingElement**"
            descriptor_2 = "IfcBuildingElement"

        # Initialize window and concrete specific cases
        concrete_instruct = ""
        window_instruct = ""

        # Category before concrete leaf node for both oekobaudat and kbob is "beton", so load specifc instruction
        if category == "Beton":
            concrete_instruct = "- For structural concrete, ignore reinforcement. Just match all viable generic and specifc concretes, and consider the appropriate cement mix for the element type."
        if category == "Fenster, Sonnenschutz, Fassadenplatten":
            window_instruct = "- For IfcWindow entities, just match the glazing and don't match the frame options."


        # Load context-aware few-shot examples
        exp = ""
        if exp_bool == True and database == "kbob":
            if category == "Anstrichstoffe, Beschichtungen":
                exp = material_prompt_components["examples_anstrichstoffe"]
            elif category == "Beton":
                exp = material_prompt_components["examples_beton"]
            elif category == "Bodenbeläge":
                exp = material_prompt_components["examples_bodenbelaege"]
            elif category == "Dichtungsbahnen, Schutzfolien":
                exp = material_prompt_components["examples_dichtungsbahnen"]
            elif category == "Fenster, Sonnenschutz, Fassadenplatten":
                exp = material_prompt_components["examples_fenster"]
            elif category == "Holz und Holzwerkstoffe":
                exp = material_prompt_components["examples_holz"]
            elif category == "Kunststoffe":
                exp = material_prompt_components["examples_kunststoffe"]
            elif category == "Mauersteine":
                exp = material_prompt_components["examples_mauersteine"]
            elif category == "Metallbaustoffe":
                exp = material_prompt_components["examples_metallbaustoffe"]
            elif category == "Mörtel und Putze":
                exp = material_prompt_components["examples_moertel"]
            elif category == "Steine, Schüttungen, Platten und Ziegel":
                exp = material_prompt_components["examples_platten"]
            elif category == "Türen":
                exp = material_prompt_components["examples_tueren"]
            elif category == "Wäremdämmstoffe":
                exp = material_prompt_components["examples_waermedaemstoffe"]

        # Construct static lines
        static_lines_1 = [
            "You are an expert in assigning appropriate materials from a life cycle assessment (LCA) database to BIM elements.",
            "Please complete the following task.",
            "",
            "**Material Inference Task**",
            "- You will receive two inputs:",
            f"  1. The first input describes {descriptor_1}.",
            "  2. The second input file contains a list of 'Material Options' from an LCA database.",
            f"{task_fr_1} for the {descriptor_2} from the first file.",
            f"{task_fr_2}",
            "- If no viable matches are found, don't assign any materials.",
            "- Base your decision on **all relevant contextual clues** in the first input (e.g., material data, element name, element type, psets)."
        ]

        # Construct static lines
        static_lines_2 = [
            f"**Input 1 (Data describing {descriptor_2}):**",
            "",
            "```json",
            ifc_string,
            "```",
            "",
            "**Input 2 (A list containing standardized material options):**",
            "",
            "```json",
            materials_string,
            "```"
        ]

    # ============================================
    # German Prompt Lines
    # ============================================

    else:
    
        # assign blocks based on bools
        cot = material_prompt_components_ger["chain_of_thought"] if cot_bool else ""
        etr = material_prompt_components_ger["extract_then_reason"] if etr_bool else ""
        isr = material_prompt_components_ger["iterative_self_refinement"] if isr_bool else ""
        prs = material_prompt_components_ger["prio_sustainability"] if prio_sustainability else ""

        # assign task framing prompt 
        if matching_strictness == "Mid":
            task_fr_1 = material_prompt_components_ger["task_fr_mid_1"]
            task_fr_2 = material_prompt_components_ger["task_fr_mid_2"]
        elif matching_strictness == "High":
            task_fr_1 = material_prompt_components_ger["task_fr_high_1"]
            task_fr_2 = material_prompt_components_ger["task_fr_high_2"]
        else:
            task_fr_1 = material_prompt_components_ger["task_fr_low_1"]
            task_fr_2 = material_prompt_components_ger["task_fr_low_2"]

        # construct dynamic output block
        output_format_map = {
            (False, False): material_prompt_components_ger["output_format_baseline"],
            (True,  False): material_prompt_components_ger["output_format_etr"],
            (False, True):  material_prompt_components_ger["output_format_irs"],
            (True,  True):  material_prompt_components_ger["output_format_etr_isr"],
        }
        output_block = output_format_map.get((etr_bool, isr_bool), material_prompt_components_ger["output_format_baseline"])

        # Distinguish descriptor of first JSON file
        if mode == "target_layer":
            descriptor_1 = "ein **Target Layer** von einem IfcBuildingElement"
            descriptor_2 = "die 'Target Layer of Material Inference'"
        else:
            descriptor_1 = "ein **IfcBuildingElement**"
            descriptor_2 = "das IfcBuildingElement"

        # Initialize window and concrete specific cases
        concrete_instruct = ""
        window_instruct = ""

        # Category before concrete leaf node for both oekobaudat and kbob is "beton", so load specifc instruction
        if category == "Beton":
            concrete_instruct = "- Falls tragender Beton, die Bewehrung ignorieren. Einfach alle geeigneten generischen und spezifischen Betone zuordnen und die passende Zementmischung für die Funktion des Elements berücksichtigen."
        if category == "Fenster, Sonnenschutz, Fassadenplatten":
            window_instruct = "- Bei IfcWindow-Elementen nur die Verglasung zuordnen und keine Rahmenoptionen berücksichtigen."

        # Load context-aware few-shot examples
        exp = ""
        if exp_bool == True and database == "kbob":
            if category == "Anstrichstoffe, Beschichtungen":
                exp = material_prompt_components_ger["examples_anstrichstoffe"]
            elif category == "Beton":
                exp = material_prompt_components_ger["examples_beton"]
            elif category == "Bodenbeläge":
                exp = material_prompt_components_ger["examples_bodenbelaege"]
            elif category == "Dichtungsbahnen, Schutzfolien":
                exp = material_prompt_components_ger["examples_dichtungsbahnen"]
            elif category == "Fenster, Sonnenschutz, Fassadenplatten":
                exp = material_prompt_components_ger["examples_fenster"]
            elif category == "Holz und Holzwerkstoffe":
                exp = material_prompt_components_ger["examples_holz"]
            elif category == "Kunststoffe":
                exp = material_prompt_components_ger["examples_kunststoffe"]
            elif category == "Mauersteine":
                exp = material_prompt_components_ger["examples_mauersteine"]
            elif category == "Metallbaustoffe":
                exp = material_prompt_components_ger["examples_metallbaustoffe"]
            elif category == "Mörtel und Putze":
                exp = material_prompt_components_ger["examples_moertel"]
            elif category == "Steine, Schüttungen, Platten und Ziegel":
                exp = material_prompt_components_ger["examples_platten"]
            elif category == "Türen":
                exp = material_prompt_components_ger["examples_tueren"]
            elif category == "Wäremdämmstoffe":
                exp = material_prompt_components_ger["examples_waermedaemstoffe"]
            else: # Include more specfic examples, depending on the database and last category branch before material leaf-nodes
                exp = ""


        # Construct static lines
        static_lines_1 = [
            "Du bist ein Experte darin, geeignete Materialien aus einer Ökobilanz (LCA) Datenbank Bauelementen im IFC-Modell zuzuordnen",
            "Bitte führe die folgende Aufgabe aus:",
            "",
            "**Aufgabe zur Materialzuordnung**",
            "- Du erhälst zwei Eingaben:",
            f"  1. Die erste Eingabe beschreibt {descriptor_1}.",
            "  2. Die zweite Eingabe enthält eine Liste von 'material_options' aus einer LCA-Datenbank.",
            f"{task_fr_1} für {descriptor_2} aus der ersten Eingabe darstellen. ",
            f"{task_fr_2}",
            "- Falls keine geeigneten Entsprechungen gefunden werden, ordne keine Materialien zu.",
            "- Stütze deine Entscheidung auf **alle relevanten Kontextinformationen** aus der ersten Eingabe (z.B. material data, element name, element type, psets)."
        ]

        # Construct static lines
        static_lines_2 = [
            f"**Eingabe 1 (Daten, welche {descriptor_2} beschreiben):**",
            "",
            "```json",
            ifc_string,
            "```",
            "",
            "**Eingabe 2 (Eine Liste mit standardisierten Materialoptionen):**",
            "",
            "```json",
            materials_string,
            "```"
        ]

    # Include optional blocks (with dynamic spacing)
    dynamic_lines = [
        prs,
        concrete_instruct,
        window_instruct,
        cot,
        etr,
        isr,
        output_block,
        exp,
    ]
    dynamic_lines = [line for line in dynamic_lines if line.strip()]

    # Combine lines (this is the only way to control dynamic spacing)
    lines = static_lines_1 + dynamic_lines + static_lines_2

    # Construct actual prompt
    prompt = "\n".join(lines)
    return prompt