import os

from scaffold.file_service import FileService



class ProjectBuilder(FileService):
    @staticmethod
    def a_project(function_name, description):
        return ProjectBuilder(function_name, description)
    
    def __init__(self):
        self.docs = True
        

    def build(self):
        if self.belongs:
           folder_path = self.join("functions", self.belongs, self.function_name)
           self.make_dir(folder_path)
           self.make_dir(f"functions/{self.belongs}/utils")
           self.make_file(folder_path, "__init__.py")
           self.make_file(f"functions/{self.belongs}/utils", "__init__.py")
        else:
            folder_path = os.path.join("functions", self.function_name)
            self.make_dir(folder_path)
            self.make_file(folder_path, "__init__.py")

        self.make_file(folder_path, "config.py", self.config)
        self.make_file(folder_path, "main.py", self.main)
        self.make_file(folder_path, "unit.py", self.unit)
        self.write_lines("infra/stacks/lambda_stack.py", self.lambda_stack)
        if self.integration:
            self.make_file(folder_path, "integration.py", self.integration)
        

        

    