from .rules import *


class Page():
    def __init__(self, type: str, rules: list):
        self.type = type
        self.rules = rules

    def check_all_rules(self):
        for rule in self.rules:
            rule.check()


class ServicePage(Page):
    def __init__(self):
        super("service",
              [CommentRule(),
               JavaDocRule(),
               LegacyDirectoryPathRule()
               ]
              )


class ServiceImplPage(Page):
    def __init__(self):
        super("service_impl",
              [CommentRule(),
               JavaDocRule(),
               LegacyDirectoryPathRule(),
               ]
              )


class ControllerPage(Page):
    def __init__(self):
        super("controller",
              [CommentRule(),
               JavaDocRule(),
               IfElseRule(),
               UnderLineRule(),
               RequestMethodRule(),
               MethodNameRule(),
               GenericTypeRule()
               ]
              )
