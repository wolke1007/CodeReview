import os, sys; 
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from rules import *
from utils import *

class Page():
    def __init__(self, file_path: str, controller_name: str):
        self.type = type(self).__name__
        self.controller_name = controller_name
        self.file_path = file_path
        # print(self.type)  # debug
        with open(self.file_path, 'r') as f:
            self.file_lines = f.readlines()
        self.rules = []

    def set_rules(self, rules: list):
        self.rules = rules

    def check_all_rules(self):
        for rule in self.rules:
            rule.do_rule_check()


class ServicePage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path= file_path, controller_name= controller_name)
        self.set_rules([JavaDocRule(self),
                        CommentRule(self),
                        LegacyDirectoryPathRule(self),
                        GenericTypeRule(self),
                        MethodNameRule(self)
                        ])


class ControllerPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path= file_path, controller_name= controller_name)
        self.set_rules([CommentRule(self),
                        IfElseRule(self),
                        UnderLineRule(self),
                        LegacyDirectoryPathRule(self),
                        RequestMethodRule(self),
                        GenericTypeRule(self),
                        MethodNameRule(self)
                        ])
        self.sql_file_path = get_sql_file_path()
        with open(self.sql_file_path, 'r') as f:
            self.sql_file_lines = f.readlines()


class ServiceImplPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path= file_path, controller_name= controller_name)
        self.set_rules([CommentRule(self),
                        LegacyDirectoryPathRule(self),
                        ServiceImplAnnotationRule(self),
                        GenericTypeRule(self),
                        MethodNameRule(self)
                        ])


if __name__ == "__main__":
    pass
