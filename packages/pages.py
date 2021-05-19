from .rules import *


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
