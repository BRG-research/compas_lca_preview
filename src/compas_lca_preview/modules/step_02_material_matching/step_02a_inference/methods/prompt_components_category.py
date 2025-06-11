category_prompt_components = {

# ===================================
# === PROMPT REASONING STRATEGIES ===
# ===================================

    # VARIABLE 3: Chain of Thought Reasoning
    # Should the LLM be instructed to think "step-by-step"
    "chain_of_thought": "- Include Chain-of-Thought Reasoning. Analyze all possible categories and think step by step before making your decision.",

    # VARIABLE 4: Extract-Then-Reason
    # Should the LLM identify and summarize the key information for material inference first?
    "extract_then_reason": '''
**Extract Key Information First**
- In the first input that describes the IFC data, there is a lot of information that might not be relevant for category inference.
- Before matching a category, extract the key information that could be relevant for category inference. 
- Write the a concise summary of the key information in the "Key Information Summary" field in the required output format.
''',

    # VARIBLE 5: Iterative Self-Refinement
    # Should the LLM give a preliminary answer first, and then evaluate it / improve upon its answer?
    "iterative_self_refinement": '''
**Iterative Self Refinement**
- First, produce an output in the "Preliminary Selection" field.
- Then analyze your own output critically.
- Finally, revise your answer into a final improved version in the "Matched Category" field.
''',

# ================================
# === PROMPT CONTEXTUALIZATION ===
# ================================

    # VARIABLE 6
    # EXAMPLES
    "examples": '''
**Example 1: Clear Match**    
- If the Material Descriptor or Element Name in the IFC data mentions "Concrete", "Insulation", "Wood", "Brick", etc., then match the corresponding category.

**Example 2: Implicit Match**
- If the IFC input is somewhat vague, and it can be deduced that it is for instance a "floor covering" without specifically mentioning it, then the corresponding category is still matched.
- Same applies for other types of IFC inputs. If there is enough data such that only one category could be potentially matched, then that category should be matched.

**Example 3: True Negative**
- If the IFC input specifies the entity IfcSlab, IfcWall, etc. but there is no indication in the material data or metadata for the type of construction or material, then no category should be matched.
- In general, if the IFC input has too little data to classify it reliably into a category, then no category should be matched.
''',
 
# ======================
# === OUTPUT FORMATS ===
# ======================
# Slightly redundant to write all of them down
# But this is the best workaround with reagards to modular and nested strings

    # Output Format Baseline
    "output_format_baseline": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Matched Category": "<Chosen Category>"
}}
```
If no viable match is found, return "None" for the "Matched Category" key:
```json
{{
"Matched Category": "None"
}}
```
''',

    # Output Format extract_then_reason == True
    "output_format_etr": '''
### **Required JSON Output Format:**
**DO NOT** include explanations, commentary, or markdown formatting.
Respond with **valid JSON only**, in the **exact format shown below**:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Matched Category": "<Chosen Category>"
}}
```
If no viable match is found, return "None" for the "Matched Category" key:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Matched Category": "None"
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
"Preliminary Selection": "<Preliminary Category Choice>",
"Matched Category": "<Final Category Choice>"
}}
```
If no viable match is found, return "None" for the "Matched Category" key:
```json
{{
"Preliminary Selection": "<Preliminary Category Choice | None>",
"Matched Category": "None"
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
"Preliminary Selection": "<Preliminary Category Choice>",
"Matched Category": "<Final Category Choice>"
}}
```
If no viable match is found, return "None" for the "Matched Category" key:
```json
{{
"Key Information Summary": "<Short summary of Key Information>",
"Preliminary Selection": "<Preliminary Category Choice | None>",
"Matched Category": "None"
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



category_prompt_components_ger = {

# ===================================
# === PROMPT REASONING STRATEGIES ===
# ===================================

    # Should the LLM be instructed to think "step-by-step"
    "chain_of_thought": "- Wende eine 'Chain-of-Thought'Begründungsstrategie an. Analysiere alle möglichen Kategorien der Liste und denke schrittweise, bevor du deine Entscheidung triffst.",

    # Should the LLM identify and summarize the key information for material inference first?
    "extract_then_reason": '''
**Zuerst Schlüsselinformationen extrahieren**
- In der ersten Eingabe, die die IFC-Daten beschreibt, gibt es viele Informationen, die für die Klassifizierung nicht relevant sein könnten.
- Bevor eine Kategorie zugeordnet wird, extrahiere die Schlüsselinformationen, die für die Zuweisung relevant sein könnten.
- Schreibe eine kurze Zusammenfassung der Schlüsselinformationen in das Feld "Key Information Summary" im geforderten Ausgabeformat.
''',

    # Should the LLM give a preliminary answer first, and then evaluate it / improve upon its answer?
    "iterative_self_refinement": '''
**Iterative Selbstverbesserung**
- Erstelle zuerst eine Ausgabe im Feld "Preliminary Selection".
- Analysiere dann deine eigene Ausgabe kritisch.
- Überarbeite abschließend deine Antwort zu einer verbesserten Endversion im Feld "Matched Category".
''',

# ================================
# === PROMPT CONTEXTUALIZATION ===
# ================================

    # EXAMPLES
    "examples": '''
**Beispiel 1: Klare Zuweisung**    
- Wenn der Material-Name oder der Elementname in den IFC-Daten Begriffe wie "Beton", "Dämmung", "Holz" usw. enthält, dann ist die entsprechende Kategorie zuzuordnen.

**Beispiel 2: Implizite Übereinstimmung** 
- Wenn die IFC-Eingabe etwas vage ist, aber z. B. abgeleitet werden kann, dass es sich um einen "Bodenbelag" handelt, auch wenn dies nicht explizit genannt wird, soll dennoch die entsprechende Kategorie zugewiesen werden.  
- Gleiches gilt für andere Arten von IFC-Eingaben. Wenn genügend Daten vorhanden sind, sodass nur eine Kategorie infrage kommt, soll diese Kategorie zugewiesen werden.

**Beispiel 3: Echte Negativ-Zuordnung**  
- Wenn die IFC-Eingabe z. B. IfcSlab, IfcWall usw. als Entität angibt, aber keine Hinweise in den Materialdaten oder Metadaten auf die Bauweise oder das Material enthalten sind, soll keine Kategorie zugewiesen werden.  
- Allgemein gilt: Wenn die IFC-Eingabe zu wenige Informationen enthält, um sie zuverlässig einer Kategorie zuordnen zu können, soll keine Kategorie zugewiesen werden.
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
"Matched Category": "<Gewählte Kategorie>"
}}
```
Falls keine geeignete Kategorie gefunden wurde, gib "None" für den Schlüssel "Matched Category" zurück:
```json
{{
"Matched Category": "None"
}}
```
''',

    # Output Format extract_then_reason == True
    "output_format_etr": '''
### **Erforderliches JSON-Ausgabeformat:**
**KEINE** zusätzliche Erklärungen, Kommentare, oder Markdown-Formatierungen
Antworte ausschliesslich mit **gültigem JSON**, und zwar **genau im unten gezeigten Format*:
```json
{{
"Key Information Summary": "<Kurze Zusammenfassung der Schlüsselinformationen>",
"Matched Category": "<Gewählte Kategorie>"
}}
```
Falls keine geeignete Kategorie gefunden wurde, gib "None" für den Schlüssel "Matched Category" zurück:
```json
{{
"Key Information Summary": "<Kurze Zusammenfassung der Schlüsselinformationen>",
"Matched Category": "None"
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
"Preliminary Selection": "<Vorläufige Kategorieauswahl>",
"Matched Category": "<Gewählte Kategorie>"
}}
```
Falls keine geeignete Kategorie gefunden wurde, gib "None" für den Schlüssel "Matched Category" zurück:
```json
{{
"Preliminary Selection": "<Vorläufige Kategorieauswahl | None>",
"Matched Category": "None"
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
"Preliminary Selection": "<Vorläufige Kategorieauswahl | None>",
"Matched Category": "<Gewählte Kategorie>"
}}
```
Falls keine geeignete Kategorie gefunden wurde, gib "None" für den Schlüssel "Matched Category" zurück:
```json
{{
"Key Information Summary": "<Kurze Zusammenfassung der Schlüsselinformationen>",
"Preliminary Selection": "<Vorläufige Kategorieauswahl | None>",
"Matched Category": "None"
}}
```
'''
}