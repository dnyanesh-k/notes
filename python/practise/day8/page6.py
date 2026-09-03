# multiple inheritance
# - one child class having multiple parent classes
# e.g 
# 1. Teacher is faculty as well as lab assistant
# 2. Employee is developer as well as tester

class Teacher:
    def __init__(self, name, subject):
        self._name = name
        self._subject = subject
        print("==T==")

class LabAssistant:
    def __init__(self, name, lab):
        self._name = name
        self._lab = lab
        print("==LA==")

class TeacherLabAssistant(Teacher, LabAssistant):
    def __init__(self, name, subject, lab, address):
        Teacher.__init__(self, name, subject)
        LabAssistant.__init__(self, name, lab)
        self._address = address
        print("==TLA==")

tla = TeacherLabAssistant('tla1', 'math', 'math', 'germany')
        

                
        