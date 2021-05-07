from .rules import *


class Page():
    def __init__(self, rules: list):
        self.type = type(self).__name__
        print(self.type)  # debug
        self.rules = rules

    def check_all_rules(self):
        for rule in self.rules:
            rule.run()


class ServicePage(Page):
    def __init__(self, file_path: str):
        super().__init__([JavaDocRule(file_path= file_path)])

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
