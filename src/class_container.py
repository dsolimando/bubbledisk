class class_container:
    projects = []
    __current_project = 0
    
    def add_project (self,project):
        self.projects.append (project)
    
    def set_current_project (self,num):
        self.__current_project = num
    
    def get_current_project (self):
        return self.__current_project
        