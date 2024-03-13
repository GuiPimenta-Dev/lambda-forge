from file_service import FileService



class ProjectBuilder(FileService):
    @staticmethod
    def a_project():
        return ProjectBuilder()
    
    def __init__(self):
        self.docs = True
        

    def build(self):
        self.copy_folders("lambda-forge/scaffold/files", "lambda-forge")
        

        

    