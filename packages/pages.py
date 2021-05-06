from .rules import *


class Page():
    def __init__(self, rules: list):
        self.type = type(self).__name__
        self.rules = rules

    def check_all_rules(self):
        print(self.type) # debug
        for rule in self.rules:
            rule.check()


class ServicePage(Page):
    def __init__(self):
        super().__init__([CommentRule(),
                          JavaDocRule(),
                          LegacyDirectoryPathRule()
                          ]
                         )


class ServiceImplPage(Page):
    def __init__(self):
        super().__init__([CommentRule(),
               JavaDocRule(),
               LegacyDirectoryPathRule(),
               ]
              )


class ControllerPage(Page):
    def __init__(self):
        super().__init__([CommentRule(),
               JavaDocRule(),
               IfElseRule(),
               UnderLineRule(),
               RequestMethodRule(),
               MethodNameRule(),
               GenericTypeRule()
               ]
              )
