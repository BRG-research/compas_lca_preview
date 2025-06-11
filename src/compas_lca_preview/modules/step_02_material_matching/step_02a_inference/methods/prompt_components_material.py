material_prompt_components = {


# ===================================
# === TASK FRAMING ==================
# ===================================

    "task_fr_low_1": "- Identify all 'Material Options' that are **viable matches**",
    "task_fr_low_2": "- Viable matches may include **reasonable approximations**; exact semantic alignment is not required.",
    "task_fr_mid_1": "- Identify all 'Material Options' that are **viable and contextually appropriate** matches",
    "task_fr_mid_2": "- Prioritize materials that share **core characteristics** with the described IFC data, but **limited approximations** are acceptable if well-justified.",
    "task_fr_high_1": "- Identify only those 'Material Options' that are **clear and direct matches**",
    "task_fr_high_2": "- Matches must demonstrate a **high degree of semantic or functional alignment** with the described IFC data.",
    "prio_sustainability": "- Prioritize options that are assessed as **particularly sustainable** based on their environmental impacts.",

# ===================================
# === PROMPT REASONING STRATEGIES ===
# ===================================

    # Should the LLM be instructed to think "step-by-step"
    "chain_of_thought": "- Include Chain-of-Thought Reasoning. Analyze all possible material options and think step by step before making your decision.",

    # Should the LLM identify and summarize the key information for material inference first?
    "extract_then_reason": '''
**Extract Key Information First**
- In the first input that describes the IFC data, there is a lot of information that might not be relevant for category inference.
- Before matching material options, extract the key information that could be relevant for material inference. 
- Write the a concise summary of the key information in the "Key Information Summary" field in the required output format.
''',

    # Should the LLM give a preliminary answer first, and then evaluate it / improve upon its answer?
    "iterative_self_refinement": '''
**Iterative Self Refinement**
- First, produce an output in the "Preliminary Selection" field.
- Then analyze your own output critically.
- Finally, revise your answer into a final improved version in the "Matched Materials" field.
''',

# ================================
# === PROMPT CONTEXTUALIZATION ===
# ================================

    # CONTEXT-AWARE EXAMPLES
    # Anstrichstoffe, Beschichtungen
    "examples_anstrichstoffe": '''
**Matching Example**    
- Material Name in the IFC data says "Anstrich", but has no further constraints, following material options are matched:
"Matched Materials": ["Anstrich, lösemittelverdünnbar, 2 Anstriche", "Anstrich, wasserverdünnbar, 2 Anstriche"]

**True Negative Example**
- Material Name in the IFC data says "Acrylfarbe". There is no match in the "material_options". No material is assigned:
"Matched Materials": []
''',

    # Beton
    "examples_beton": '''
**Example 1: Ambivalent data**
- Material Name in the IFC data says "Ortbeton", and it is a generic load-bearing slab, which doesn't need special high-performing concrete.
- This indicates that EVERY "Hochbaubeton" and "Beton" entry in the "material_options" is assigned, but with a CEM mix of 300kg or less.

**Example 2: Specific data**
- Material Name indicates that it is screed. This means only a lean concrete mixes are viable.
- In this case, both "Magerbeton" entries from the "material_options" are assigned.

**Example 3: Specific data**
- The Metadata indicates that it is a foundation slab, or some form of similar subterranean concrete.
- Accordingly, only concrete mixes with a CEM mix of 300kg or more are assigned, and Tiefbaubeton is chosen.
- For foundations, Hochbaubeton is not appropriate.
''',

    # Bodenbeläge
    "examples_bodenbelaege": '''
**Example 1: Specific data**
- Material Name says "Laminat". There is only one entry in "material_options" that matches the descriptor.
- Only the entry "Laminat, 8.5 mm" is matched in the output. 

**Example 2: Ambivalent data**
- Material Name in the IFC data says "Natursteinplatte", and there is no indication of how it was processed.
- Then all entries with "Natursteinplatte" are matched.
''',

    # Dichtungsbahnen, Schutzfolien
    "examples_dichtungsbahnen": '''
**Example: Ambivalent data**
- Material Name says "Dichtungsbahn". There are three entries in "material_options" with the word Dichtungsbahn.
- All of those options are matched.
''',

    # Fenster, Sonnenschutz, Fassadenplatten
    "examples_fenster": '''
**Example 1: Ambivalent data**
- The Element "Type" is IfcWindow. There is no indication about glazing and U-value.
- ALL entries with "Isolierverglasung" are matched

**Example 2: Specific data**
- The Element "Type" is IfcWindow. There is an indication that it is triple-glazed and there is a strong emphasis on fire-safety.
- Only the entries with "Isolierverglasung" and an appropriate "Ug-Wert" are matched.
''',

    # Holz und Holzwerkstoffe
    "examples_holz": '''
**Example 1: Ambivalent data**
- The Material Name says "Massivholz". The element's load-bearing pset is True.
- Softwood (Fichte / Tanne / Lärche) are used for structural "Massivholz". All of the softwood entries are matched.

**Example 2: Specific data**
- The Material Name mentions Brettschichtholz. There are only two entries in "material_options" with that descriptor.
- Only those two entries are matched.
''',

    # Klebstoffe Fugendichtungsmassen
    "examples_klebstoffe": "",

    # Kunststoffe
    "examples_kunststoffe": '''
**Example: Specific data**
- The material name says "Plexiglas". The only entry in the "material_options" that matches that name is chosen.
''',

    # Mauersteine
    "examples_mauersteine": '''
**Example 1: Ambivalent data**
- The Material Name says "Leichtzementstein". There are no further specifications in the IFC data.
- All three entries in the "material_options" with the name "Leichtzementstein" are matched.

**Example 2: Specific data**
- The Material Name says "Backstein". But there is no indication of it being insulating. So the "perlitgefüllt" entry in "material_options" is ignored.
- Only the "material_options" entry "Backstein" is matched.
''',

    # Metallbaustoffe
    "examples_metallbaustoffe": '''
**Example 1: Ambivalent data**
- The Element name indicates "Blech". The element is external, so it needs to be resistant to corrosion.
- All "material_options" entries with the name "blech" that are resistant to corrosion are matched.

**Example 2: Specific data**
- The Material Name says "Stahl" and the psets indicate that the element is load-bearing.
- "Stahlprofil, blank" is the only loadbearing entry in "material_options"
''',

    # Mineralische Platten Schüttungen Steine und Ziegel
    "examples_platten": '''
**Example 1: Ambivalent data**
- The Material Name says "Gipsplatte", and the IFC data indicates no further constraints (i.e., usage / function, etc.) 
- There are multiple "material_options" entries with "gips" and "platte" in the name. All of them are matched.

**Example 2: Specific data**
- The Material Name says "Sand". There is only one material options entry with the name "sand" in it.
''',

    # Mörtel und Putze
    "examples_moertel": '''
**Example: Ambivalent data**
- The Material Name says "Putz". The psets indicate that the layer is on the outside.
- All "Putz" entries in "material_options" that are suitable for exterior use are matched.
''',

    # Türen
    "examples_tueren": '''
**Example 1: Ambivalent data**
- The Element Type is IfcDoor, and the psets indicate that it is external. But there is no information about any materials.
- Then we match all of the "Aussentür" entries in the "material_options"

**Example 2: Specific data**
- There is a strong emphasis on fire resistance, and the door is internal.
- The only viable matches are the "Funktionstüren" entries
''',

    # Wärmedämsstoffe
    "examples_waermedaemstoffe": '''
**Example 1: Ambivalent data**
- The Material Descriptor says "Dämmung - Weich". No further constraints. This means we match ALL soft insulation materials
found in the "material_options".

**Example 2: Specific data**
- The material descriptor says "Mineral Wool". There's two types of mineral wool in the "material_options". Steinwolle and Glaswolle.
- For those two, there are multiple entries. All "Steinwolle" and "Glaswolle" "material_options" entries are matched.
''',

 
# ======================
# === OUTPUT FORMATS ===
# ======================

    # Output Format Baseline
    "output_format_baseline": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
If no viable matches are found, return an **empty list** in JSON format: 
```json
{{
"Matched Materials": []
}}
```
''',

    # Output Format extract_then_reason== True
    "output_format_etr": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
If no viable matches are found, return an **empty list** in JSON format: 
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Matched Materials": []
}}
```
''',

    # Output Format Iterative Self Refinement == True
    "output_format_irs": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Preliminary Selection": ["<Option 1>", "<Option 2>", ...],
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
If no viable matches are found, return an **empty list** in JSON format: 
```json
{{
"Preliminary Selection": [],
"Matched Materials": []
}}
```
''',

    # Output Format etr AND isr == True
    "output_format_etr_isr": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Preliminary Selection": ["<Option 1>", "<Option 2>", ...],
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
If no viable matches are found, return an **empty list** in JSON format: 
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Preliminary Selection": [],
"Matched Materials": []
}}
```
'''
}


# ===================================
# ===================================
# ===================================
# ===================================
# ======     GERMAN         =========
# ===================================
# ===================================
# ===================================
# ===================================
# ===================================


material_prompt_components_ger = {

# ===================================
# === TASK FRAMING ==================
# ===================================

    "task_fr_low_1": "- Identifiziere alle 'material_options', die **geeignete Entsprechungen**",
    "task_fr_low_2": "- Geeignete Entsprechungen können **plausible Annäherungen** einschließen; eine exakte semantische Übereinstimmung ist nicht erforderlich.",
    "task_fr_mid_1": "- Identifiziere alle 'Materialoptionen', die **kontextuell angemessen und grundsätzlich passend**",
    "task_fr_mid_2": "- Bevorzuge Materialien mit **ähnlicher Zusammensetzung, Funktion oder Dichte**. Moderate Annäherungen sind erlaubt, wenn sie nachvollziehbar begründet werden können.",
    "task_fr_high_1": "- Identifiziere nur solche 'Materialoptionen', die eine **eindeutige und direkte Übereinstimmung**",
    "task_fr_high_2": "- Die Übereinstimmung muss eine **hohe semantische, funktionale oder stoffliche Ähnlichkeit** zeigen. Annäherungen sollen nur erfolgen, wenn sie ausdrücklich durch die Beschreibung der IFC-Daten gerechtfertigt sind.",
    "prio_sustainability": "- Priorisiere Optionen, die auf Grundlage ihrer Umweltwirkungen als **besonders nachhaltig** eingeschätzt werden.",


# ===================================
# === PROMPT REASONING STRATEGIES ===
# ===================================

    # Should the LLM be instructed to think "step-by-step"
    "chain_of_thought": "- Wende eine 'Chain-of-Thought'Begründungsstrategie an. Analysiere alle möglichen Materialoptionen und denke schrittweise, bevor du deine Entscheidung triffst.",

    # Should the LLM identify and summarize the key information for material inference first?
    "extract_then_reason": '''
**Zuerst Schlüsselinformationen extrahieren**
- In der ersten Eingabe, die die IFC-Daten beschreibt, gibt es viele Informationen, die für die Materialzuodrnung nicht relevant sein könnten.
- Bevor Materialoptionen zugeordnet werden, extrahiere die Schlüsselinformationen, die für die Materialzuordnung relevant sein könnten.
- Schreibe eine kurze Zusammenfassung der Schlüsselinformationen in das Feld "Key Information Summary" im geforderten Ausgabeformat.
''',

    # Should the LLM give a preliminary answer first, and then evaluate it / improve upon its answer?
    "iterative_self_refinement": '''
**Iterative Selbstverbesserung**
- Erstelle zuerst eine Ausgabe im Feld "Preliminary Selection".
- Analysiere dann deine eigene Ausgabe kritisch.
- Überarbeite abschließend deine Antwort zu einer verbesserten Endversion im Feld "Matched Materials".
''',

# ================================
# === PROMPT CONTEXTUALIZATION ===
# ================================

    # CONTEXT-AWARE EXAMPLES
    # Anstrichstoffe, Beschichtungen
    "examples_anstrichstoffe": '''
**Zuordnungs-Beispiel**    
- Materialname in der IFC-Datei lautet "Anstrich", es gibt jedoch keine weiteren Einschränkungen. Die folgenden Materialoptionen werden zugeordnet:
"Matched Materials": ["Anstrich, lösemittelverdünnbar, 2 Anstriche", "Anstrich, wasserverdünnbar, 2 Anstriche"]

**Negativbeispiel (korrekte Nicht-Zuordnung)**
- Materialname in der IFC-Datei lautet "Acrylfarbe". Es gibt keine Übereinstimmung in den "material_options". Kein Material wird zugeordnet:
"Matched Materials": []
''',

    # Beton
    "examples_beton": '''
**Beispiel 1: Uneindeutige Daten**
- Materialname in der IFC-Datei lautet "Ortbeton", und es handelt sich um eine generische, tragende Decke.
- Dies bedeutet, dass JEDE „Hochbaubeton“- und „Beton“-Eintragung in den "material_options" zugeordnet wird, jedoch nur mit einer CEM-Mischung von 300 oder weniger.

**Beispiel 2: Genaue Daten**
- Der Materialname gibt an, dass es sich um Estrich handelt. Das bedeutet, dass nur magere Betone in Frage kommen.
- In diesem Fall werden beide „Magerbeton“-Einträge aus den "material_options" zugeordnet.

**Beispiel 3: Genaue Daten**
- Die Metadaten geben an, dass es sich um ein Fundament handelt oder um eine ähnliche unterirdische Betonschicht.
- Dementsprechend werden nur Betone mit einer CEM-Mischung von 300 oder mehr zugeordnet, und Tiefbaubeton wird gewählt.
- Für Fundamente ist Hochbaubeton nicht geeignet.
''',

    # Bodenbeläge
    "examples_bodenbelaege": '''
**Beispiel 1: Genaue Daten**
- Der Materialname lautet „Laminat“. Es gibt nur einen Eintrag in den "material_options", der zum Begriff passt.
- Nur der Eintrag „Laminat, 8.5 mm“ wird im Ergebnis zugeordnet.

**Beispiel 2: Uneindeutige Daten**
- Der Materialname in der IFC-Datei lautet „Natursteinplatte“, und es gibt keinen Hinweis darauf, wie sie verarbeitet wurde.
- Dann werden alle Einträge mit „Natursteinplatte“ zugeordnet.
''',

    # Dichtungsbahnen, Schutzfolien
    "examples_dichtungsbahnen": '''
**Beispiel: Uneindeutige Daten**
- Der Materialname lautet „Dichtungsbahn“. Es gibt drei Einträge in den "material_options" mit dem Wort Dichtungsbahn.
- Alle diese Optionen werden zugeordnet.
''',

    # Fenster, Sonnenschutz, Fassadenplatten
    "examples_fenster": '''
**Beispiel 1: Uneindeutige Daten**
- Der Elementtyp ist IfcWindow. Es gibt keine Angaben zur Verglasung oder zum U-Wert.
- ALLE Einträge mit „Isolierverglasung“ werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Der Elementtyp ist IfcWindow. Es wird angegeben, dass es sich um Dreifachverglasung handelt und besonderer Brandschutz erforderlich ist.
- Nur die Einträge mit „Isolierverglasung“ und einem passenden „Ug-Wert“ werden zugeordnet.
''',

    # Holz und Holzwerkstoffe
    "examples_holz": '''
**Beispiel 1: Uneindeutige Daten**
- Der Materialname lautet „Massivholz“. Das Element ist laut Pset tragend.
- Nadelhölzer (Fichte / Tanne / Lärche) werden für tragendes Massivholz verwendet. Alle entsprechenden Nadelholz-Einträge werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Der Materialname nennt „Brettschichtholz“. Es gibt nur zwei Einträge in den "material_options", die diesen Begriff enthalten.
- Nur diese beiden Einträge werden zugeordnet.
''',

    # Klebstoffe Fugendichtungsmassen
    "examples_klebstoffe": "",

    # Kunststoffe
    "examples_kunststoffe": '''
**Beispiel: Genaue Daten**
- Der Materialname lautet „Plexiglas“. Der einzige Eintrag in den "material_options", der diesen Namen enthält, wird ausgewählt.
''',

    # Mauersteine
    "examples_mauersteine": '''
**Beispiel 1: Uneindeutige Daten**
- Der Materialname lautet „Leichtzementstein“. Es gibt keine weiteren Angaben in den IFC-Daten.
- Alle drei Einträge mit dem Namen „Leichtzementstein“ in den "material_options" werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Der Materialname lautet „Backstein“. Es gibt aber keinen Hinweis darauf, dass er dämmend ist. Der „perlitgefüllt“-Eintrag in den "material_options" wird ignoriert.
- Nur der „Backstein“-Eintrag wird zugeordnet.
''',

    # Metallbaustoffe
    "examples_metallbaustoffe": '''
**Beispiel 1: Uneindeutige Daten**
- Der Elementname weist auf „Blech“ hin. Das Element ist außenliegend, daher muss es korrosionsbeständig sein.
- Alle „material_options“-Einträge mit dem Namen „Blech“, die korrosionsbeständig sind, werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Der Materialname lautet „Stahl“ und die Psets zeigen an, dass das Element tragend ist.
- „Stahlprofil, blank“ ist der einzige tragende Eintrag in den "material_options".
''',

    # Mineralische Platten Schüttungen Steine und Ziegel
    "examples_platten": '''
**Beispiel 1: Uneindeutige Daten**
- Der Materialname lautet „Gipsplatte“, und die IFC-Daten enthalten keine weiteren Einschränkungen (z. B. Nutzung / Funktion etc.)
- Es gibt mehrere Einträge in den "material_options", die „Gips“ und „Platte“ im Namen haben. Alle diese werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Der Materialname lautet „Sand“. Es gibt nur einen Eintrag in den "material_options", der „Sand“ im Namen hat.
''',

    # Mörtel und Putze
    "examples_moertel": '''
**Beispiel: Uneindeutige Daten**
- Der Materialname lautet „Putz“. Die Psets geben an, dass die Schicht außen liegt.
- Alle „Putz“-Einträge in den "material_options", die für den Außenbereich geeignet sind, werden zugeordnet.
''',

    # Türen
    "examples_tueren": '''
**Beispiel 1: Uneindeutige Daten**
- Der Elementtyp ist IfcDoor und laut Psets ist die Tür außenliegend. Es gibt jedoch keine Informationen zu verwendeten Materialien.
- Dann werden alle „Aussentür“-Einträge in den "material_options" zugeordnet.

**Beispiel 2: Genaue Daten**
- Es besteht ein besonderer Fokus auf Brandschutz, und die Tür ist innenliegend.
- Nur die „Funktionstüren“-Einträge sind passende Zuordnungen.
''',

    # Wärmedämsstoffe
    "examples_waermedaemstoffe": '''
**Beispiel 1: Uneindeutige Daten**
- Die Materialbeschreibung lautet „Dämmung - Weich“. Keine weiteren Einschränkungen. Das bedeutet, ALLE weichen Dämmstoffe aus den "material_options" werden zugeordnet.

**Beispiel 2: Genaue Daten**
- Die Materialbeschreibung lautet „Mineralwolle“. In den "material_options" gibt es zwei Arten: Steinwolle und Glaswolle.
- Für beide gibt es mehrere Einträge. Alle Einträge mit „Steinwolle“ und „Glaswolle“ in den "material_options" werden zugeordnet.
''',
 
# ======================
# === OUTPUT FORMATS ===
# ======================

    # Output Format Baseline
    "output_format_baseline": '''
### **Erforderliches JSON-Ausgabeformat:**
**KEINE** zusätzliche Erklärungen, Kommentare, oder Markdown-Formatierungen
Antworte ausschliesslich mit **gültigem JSON**, und zwar **genau im unten gezeigten Format*:
```json
{{
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
Wenn keine geeigneten Entsprechungen gefunden werden, gib eine **leere Liste** im JSON-Format zurück:
```json
{{
"Matched Materials": []
}}
```
''',

    # Output Format extract_then_reason== True
    "output_format_etr": '''
### **Erforderliches JSON-Ausgabeformat:**
**KEINE** zusätzliche Erklärungen, Kommentare, oder Markdown-Formatierungen
Antworte ausschliesslich mit **gültigem JSON**, und zwar **genau im unten gezeigten Format*:
```json
{{
"Key Information Summary": "<Kurze Zusammenfassung der Schlüsselinformationen>",
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
Wenn keine geeigneten Entsprechungen gefunden werden, gib eine **leere Liste** im JSON-Format zurück:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Matched Materials": []
}}
```
''',

    # Output Format Iterative Self Refinement == True
    "output_format_irs": '''
### **Erforderliches JSON-Ausgabeformat:**
**KEINE** zusätzliche Erklärungen, Kommentare, oder Markdown-Formatierungen
Antworte ausschliesslich mit **gültigem JSON**, und zwar **genau im unten gezeigten Format*:
```json
{{
"Preliminary Selection": ["<Option 1>", "<Option 2>", ...],
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
Wenn keine geeigneten Entsprechungen gefunden werden, gib eine **leere Liste** im JSON-Format zurück:
```json
{{
"Preliminary Selection": [],
"Matched Materials": []
}}
```
''',

    # Output Format etr AND isr == True
    "output_format_etr_isr": '''
### **Erforderliches JSON-Ausgabeformat:**
**KEINE** zusätzliche Erklärungen, Kommentare, oder Markdown-Formatierungen
Antworte ausschliesslich mit **gültigem JSON**, und zwar **genau im unten gezeigten Format*:
```json
{{
"Key Information Summary": "<Kurze Zusammenfassung der Schlüsselinformationen>",
"Preliminary Selection": ["<Option 1>", "<Option 2>", ...],
"Matched Materials": ["<Option 1>", "<Option 2>", ...]
}}
```
Wenn keine geeigneten Entsprechungen gefunden werden, gib eine **leere Liste** im JSON-Format zurück:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Preliminary Selection": [],
"Matched Materials": []
}}
```
'''
}