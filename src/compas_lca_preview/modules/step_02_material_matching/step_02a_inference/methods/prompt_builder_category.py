import json
from .prompt_components_category import category_prompt_components, category_prompt_components_ger

# Build dynamic prompt
def build_category_prompt(bim_element, category_entries, mode, config):

    # Load the inputs of the current element as strings
    ifc_string = json.dumps(bim_element, indent=2, ensure_ascii=False)

    # Corresponding material entries list
    categories_string = json.dumps(category_entries, indent=2, ensure_ascii=False)

    # Get config values
    category_prompt_variables = config.get("category_prompt_variables", {})
    lng = category_prompt_variables.get("language")
    cot_bool = category_prompt_variables.get("chain_of_thought")
    etr_bool = category_prompt_variables.get("extract_then_reason")
    isr_bool = category_prompt_variables.get("iterative_self_refinement")
    exp_bool = category_prompt_variables.get("include_examples")

    # ============================================
    # English Prompt Lines
    # ============================================

    if lng == "en":

        # assign blocks based on bools
        cot = category_prompt_components["chain_of_thought"] if cot_bool else ""
        etr = category_prompt_components["extract_then_reason"] if etr_bool else ""
        isr = category_prompt_components["iterative_self_refinement"] if isr_bool else ""
        exp = category_prompt_components["examples"] if exp_bool else ""

        # construct dynamic output block
        output_format_map = {
            (False, False): category_prompt_components["output_format_baseline"],
            (True,  False): category_prompt_components["output_format_etr"],
            (False, True):  category_prompt_components["output_format_irs"],
            (True,  True):  category_prompt_components["output_format_etr_isr"],
        }
        output_block = output_format_map.get((etr_bool, isr_bool), category_prompt_components["output_format_baseline"])

        # Distinguish descriptor of first JSON file
        if mode == "target_layer":
            descriptor_1 = "a **Target Layer** of an IfcBuildingElement"
            descriptor_2 = "'Target Layer of Material Inference'"
        else:
            descriptor_1 = "an **IfcBuildingElement**"
            descriptor_2 = "IfcBuildingElement"

        # Construct static lines
        static_lines_1 = [
            "You are an expert in classifying BIM elements to life cycle assessment (LCA) categories.",
            "Please complete the following task.",
            "",
            "**Category Inference Task**",
            "- You will receive two inputs:",
            f"  1. The first input describes {descriptor_1}.",
            "  2. The second input file contains a list of 'Categories' from an LCA database.",
            f"- Identify the most accurate category for the {descriptor_2} from the first file.",
            f"- You must match a category where you anticipate finding viable material entries for the {descriptor_2}.",
            "- If there is no exact semantic match, find a reasonable approximation!"
            "- If there is no material descriptor, base your decision on **all other relevant contextual clues** in the first input (e.g., element name, element type, psets)."
        ]
        # Construct static lines
        static_lines_2 = [
            f"**Input 1 (Data describing {descriptor_2}):**",
            "",
            "```json",
            ifc_string,
            "```",
            "",
            "**Input 2 (A list containing categories for an LCA database):**",
            "",
            "```json",
            categories_string,
            "```"
        ]

    # ============================================
    # German Prompt Lines
    # ============================================

    else:

        # assign blocks based on bools
        cot = category_prompt_components_ger["chain_of_thought"] if cot_bool else ""
        etr = category_prompt_components_ger["extract_then_reason"] if etr_bool else ""
        isr = category_prompt_components_ger["iterative_self_refinement"] if isr_bool else ""
        exp = category_prompt_components_ger["examples"] if exp_bool else ""

        # construct dynamic output block
        output_format_map = {
            (False, False): category_prompt_components_ger["output_format_baseline"],
            (True,  False): category_prompt_components_ger["output_format_etr"],
            (False, True):  category_prompt_components_ger["output_format_irs"],
            (True,  True):  category_prompt_components_ger["output_format_etr_isr"],
        }
        output_block = output_format_map.get((etr_bool, isr_bool), category_prompt_components_ger["output_format_baseline"])

        # Distinguish descriptor of first JSON file
        if mode == "target_layer":
            descriptor_1 = "ein **Target Layer** von einem IfcBuildingElement"
            descriptor_2 = "die 'Target Layer of Material Inference'"
        else:
            descriptor_1 = "ein **IfcBuildingElement**"
            descriptor_2 = "das IfcBuildingElement"

        # Construct static lines
        static_lines_1 = [
            "Du bist ein Experte darin, BIM-Elemente in Kategorien einer Lebenszyklusanalyse (LCA) Datanbank einzuordnen.",
            "Bitte führe die folgende Aufgabe aus.",
            "",
            "**Aufgabe zur Kategoriezuordnung**",
            "- Du erhälst zwei Eingaben:",
            f"  1. Die erste Eingabe beschreibt {descriptor_1}.",
            "  2. Die zweite Eingabe beschreibt eine Liste von Kategorien von einer LCA Datenbank.",
            f"- Identifiziere die genaueste Kategorie für {descriptor_2} aus der ersten Datei.",
            f"- Du musst eine Kategorie auswählen, bei der du passende Materialeinträge für {descriptor_2} erwartest.",
            "- Die Kategorie muss nicht semantisch perfekt sein. Eine Annäherung ist auch akzeptabel."
            "- Wenn kein Materialname vorhanden ist, dann basiere deine Entscheidungen auf **allen anderen relevanten Kontextinformationen** aus der ersten Eingabe (z.B. Elementname, Elementtyp, Psets)."
        ]    
        # Construct static lines
        static_lines_2 = [
            f"**Eingabe 1 (Daten, welche {descriptor_2} beschreibt):**",
            "",
            "```json",
            ifc_string,
            "```",
            "",
            "**Eingabe 2 (Eine Liste mit Kategorien einer LCA Datenbank):**",
            "",
            "```json",
            categories_string,
            "```"
        ]


    # Include optional blocks (with dynamic spacing)
    dynamic_lines = [
        cot,
        etr,
        isr,
        output_block,
        exp,
    ]
    dynamic_lines = [line for line in dynamic_lines if line.strip()]

    # Combine lines to build prompt
    lines = static_lines_1 + dynamic_lines + static_lines_2

    # Construct actual prompt
    prompt = "\n".join(lines)
    return prompt