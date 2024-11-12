import os
import importlib

def load_modules():
    modules = {}
    # Correct the path to the modules directory
    modules_dir = os.path.dirname(__file__)
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = filename[:-3]
            module = importlib.import_module(f'modules.{module_name}')
            modules[module_name] = module
            print(f"Loaded module: {module_name}")
    return modules

def find_and_execute_module(modules, data, provider):
    
    print("Finding and executing module for data:", data)
    finalData = ""
    for module_name, module in modules.items():
        print(f"Executing module: {module_name}")
        # Execute the module, adding to the string with the name of the module and the returned data as a result of the run. is this the best way to inject content and manipulate the responses? absolutely not use langchain for that or something else. this is a placeholder for basic action/response injection before more complex things like that. rudimentary.
        finalData += f"{module.ingest(data, provider)}\n"
          
    return finalData

def ingestToAllModules(data, provider):
    print("Ingesting data to all modules:", data)
    modules = load_modules()
    overallData = ""
    for module_name, module in modules.items():
        print(f"Executing module: {module_name}")
        moduleResult = module.ingest(data, provider)
        # now add it to the overall data, as in a larger overall list
        overallData += moduleResult
    return overallData

def ingest(data, provider):
    print("module loader self trigger")
    return ""