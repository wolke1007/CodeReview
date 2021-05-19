import os, sys; 
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from rules import *
from utils import *

class Page():
    def __init__(self, file_path: str):
        self.type = type(self).__name__
        self.file_path = file_path
        print(self.type)  # debug
        with open(self.file_path, 'r') as f:
            self.file_lines = f.readlines()
        self.rules = []

    def set_rules(self, rules: list):
        self.rules = rules

    def check_all_rules(self):
        for rule in self.rules:
            rule.do_rule_check()


class ServicePage(Page):
    def __init__(self, file_path: str):
        super().__init__(file_path= file_path)
        self.set_rules([JavaDocRule(self)])


class ControllerPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path= file_path)
        self.controller_name = controller_name
        self.set_rules([CommentRule(self)])
        self.sql_file_path = get_sql_file_path()
        with open(self.sql_file_path, 'r') as f:
            self.sql_file_lines = f.readlines()
        

# class ServicePage(Page):
#     def __init__(self):
#         super().__init__([CommentRule(),
#                           JavaDocRule(),
#                           LegacyDirectoryPathRule()
#                           ]
#                          )


# class ServiceImplPage(Page):
#     def __init__(self):
#         super().__init__([CommentRule(),
#                JavaDocRule(),
#                LegacyDirectoryPathRule(),
#                ]
#               )


# class ControllerPage(Page):
#     def __init__(self):
#         super().__init__([CommentRule(),
#                JavaDocRule(),
#                IfElseRule(),
#                UnderLineRule(),
#                RequestMethodRule(),
#                MethodNameRule(),
#                GenericTypeRule()
#                ]
#               )

if __name__ == "__main__":
    pass
