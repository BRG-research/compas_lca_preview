import yaml
import time

class Project:
    def __init__(self, ifc_input_file=None, project_path=None, llm_api_key=None, master_config_path=None):
        self.ifc_input_file = ifc_input_file
        self.project_path = project_path
        self.llm_api_key = llm_api_key
        self.master_config_path = master_config_path
        # Load master config if path provided
        if master_config_path:
            with open(master_config_path, 'r') as f:
                master_config = yaml.safe_load(f)

            # Update attributes from config
            if 'project_config' in master_config:
                project_config = master_config['project_config']
                if not self.ifc_input_file:
                    self.ifc_input_file = project_config.get('input_ifc_file')
                if not self.project_path:
                    self.project_path = project_config.get('project_path')

    def run(self, module_name):

        start = time.time()

        print(f"Running module {module_name}...")

        if module_name == "01a":
            from .modules.step_01_data_extraction.step_01a_extract_all.run import extract_all
            extract_all(ifc_input_file=self.ifc_input_file, project_path=self.project_path, master_config_path=self.master_config_path)
        elif module_name == "01b":
            from .modules.step_01_data_extraction.step_01b_aggregate_elements.run import aggregate_elements
            aggregate_elements(project_path=self.project_path)
        elif module_name == "01c":
            from .modules.step_01_data_extraction.step_01c_dissect_layers.run import dissect_layers
            dissect_layers(project_path=self.project_path)
        elif module_name == "01d":
            from .modules.step_01_data_extraction.step_01d_filter_data.run import filter_data_sheets
            filter_data_sheets(project_path=self.project_path, master_config_path=self.master_config_path)
        
        elif module_name == "02a":
            from .modules.step_02_material_matching.step_02a_inference.run import material_matcher
            material_matcher(project_path=self.project_path, llm_api_key=self.llm_api_key, master_config_path=self.master_config_path)
        elif module_name == "02b":
            from .modules.step_02_material_matching.step_02b_bookkeeping.run import bookkeeper
            bookkeeper(project_path=self.project_path, master_config_path=self.master_config_path)

        elif module_name == "03a":
            from .modules.step_03_lca_calculation.step_03a_specific_indicators.run import append_indicators
            append_indicators(project_path=self.project_path, master_config_path=self.master_config_path)

        elif module_name == "03b":
            from .modules.step_03_lca_calculation.step_03b_gross_emissions.run import gross_emissions
            gross_emissions(project_path=self.project_path, master_config_path=self.master_config_path)

        elif module_name == "04":
            from .modules.step_04_lca_report.run import create_report
            create_report(project_path=self.project_path, master_config_path=self.master_config_path)

        else:
            raise ValueError(f"Module {module_name} not found")
        
        print(f"Module {module_name} completed in {time.time() - start:.2f} seconds")
    
    def list_modules(self):
        MODULES = [
            {"key": "p1", "name": "     Preview Category Inference Prompt", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/preview_category_prompt.py", "main": False},
            {"key": "p2", "name": "     Preview Material Inference Prompt", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/preview_material_prompt.py", "main": False},
            {"key": "01", "name": "     MODULE 01 → Data Extraction", "main": True},
            {"key": "01a", "name": "    Submodule 01a → Extract All Data from IFC model", "path": "lca_pipeline/step_01_data_extraction/step_01a_extract_all/run.py", "main": False},
            {"key": "01b", "name": "    Submodule 01b → Aggregate Data", "path": "lca_pipeline/step_01_data_extraction/step_01b_aggregate_elements/run.py", "main": False},
            {"key": "01c", "name": "    Submodule 01c → Dissect Layers", "path": "lca_pipeline/step_01_data_extraction/step_01c_dissect_layers/run.py", "main": False},
            {"key": "01d", "name": "    Submodule 01d → Filter JSON Data sheets", "path": "lca_pipeline/step_01_data_extraction/step_01d_filter_data/run.py", "main": False},
            {"key": "02", "name": "     MODULE 02 → LLM-based material matching", "main": True},
            {"key": "02a", "name": "    Submodule 02a → LLM inference of all JSON instances", "path": "lca_pipeline/step_02_material_matching/step_02a_inference/run.py", "main": False},
            {"key": "02b", "name": "    Submodule 02b → Combine LLM inference outputs", "path": "lca_pipeline/step_02_material_matching/step_02b_bookkeeping/run.py", "main": False},
            {"key": "03", "name": "     MODULE 03 → LCA Calculation", "main": True},
            {"key": "03a", "name": "    Submodule 03a → Append specific indicators to elements", "path": "lca_pipeline/step_03_lca_calculation/step_03a_specific_indicators/run.py", "main": False},
            {"key": "03b", "name": "    Submodule 03b → Calculate gross emissions", "path": "lca_pipeline/step_03_lca_calculation/step_03b_gross_emissions/run.py", "main": False},
            {"key": "04", "name": "     MODULE 04 → Create LCA report", "path": "lca_pipeline/step_04_lca_report/run.py", "main": False},
        ]
        
        print("\n==========================")
        print("♻️  COMPAS_LCA PIPELINE ♻️")
        print("==========================\n")
        print("Execute the pipeline sequentially!")
        print("Call project.run(MODULE_NAME) to execute each module:\n")

        for mod in MODULES:
            print(f"  {mod['key'].upper()}. {mod['name']}")

            if mod["key"].lower() == "p2":
                print("")
            
            if mod["key"].lower() == "01d":
                print("")

            if mod["key"].lower() == "02b":
                print("")
            if mod["key"].lower() == "03b":
                print("")
            if mod["key"].lower() == "04":
                print("")

if __name__ == "__main__":
    project = Project(ifc_input_file="data/Duplex.ifc", project_path="temp/duplex")
    project.list_modules()
    project.run("01a")
    # project.run("01b")
    # project.run("01c")
    # project.run("01d")

    # project = Project(project_path="temp/SBE")
    # project.run("02a")
    # project.run("02b")
    # project.run("03a")
    # project.run("03b")
    # project.run("04")