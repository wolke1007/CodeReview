import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from utils import *
from rules import *


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
        '''
        如果要執行全部的 Rule
        例: set_rules([JavaDocRule(self).set_all_rules_to_check()]

        如果只要執行部分 Rule
        例: set_rules([JavaDocRule(self).]
        '''
        self.rules = rules

    def check_all_rules(self):
        for rule in self.rules:
            rule.do_rule_check()


class CustomizePage():
    def __init__(self, file_path: str):
        self.type = type(self).__name__
        self.file_path = file_path
        # print(self.type)  # debug
        with open(self.file_path, 'r') as f:
            self.file_lines = f.readlines()
        self.rules = []

    def set_rules(self, rules: list):
        '''
        如果要執行全部的 Rule
        例: set_rules([JavaDocRule(self).set_all_rules_to_check()]

        如果只要執行部分 Rule
        例: set_rules([JavaDocRule(self).set_assert_rule("rule_name")]
        '''
        self.rules = rules

    def set_rule(self, rule):
        '''
        如果要執行全部的 Rule
        例: set_rules([JavaDocRule(self).set_all_rules_to_check()]

        如果只要執行部分 Rule
        例: set_rule(JavaDocRule(self).set_assert_rule("rule_name"))
        '''
        self.rules.append(rule)

    def check_all_rules(self):
        for rule in self.rules:
            rule.do_rule_check()


class ServicePage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path=file_path, controller_name=controller_name)
        self.set_rules([JavaDocRule(self).set_all_rules_to_check(),
                        CommentRule(self).set_all_rules_to_check(),
                        LegacyDirectoryPathRule(self).set_all_rules_to_check(),
                        GenericTypeRule(self).set_all_rules_to_check(),
                        MethodNameRule(self).set_assert_rule(
                            "method_name_initial_should_not_be_capital").set_assert_rule(
                            "method_name_defination_initial_should_not_be_capital")
                        ])


class ControllerPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path=file_path, controller_name=controller_name)
        self.set_rules([CommentRule(self).set_all_rules_to_check(),
                        IfElseRule(self).set_all_rules_to_check(),
                        UnderLineRule(self).set_all_rules_to_check(),
                        LegacyDirectoryPathRule(self).set_all_rules_to_check(),
                        RequestMethodRule(self).set_all_rules_to_check(),
                        GenericTypeRule(self).set_all_rules_to_check(),
                        MethodNameRule(self).set_assert_rule(
                            "method_name_initial_should_not_be_capital").set_assert_rule(
                            "method_name_defination_initial_should_not_be_capital")
                        ])
        self.sql_file_path = get_sql_file_path()
        with open(self.sql_file_path, 'r') as f:
            self.sql_file_lines = f.readlines()


class DaoPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path=file_path, controller_name=controller_name)
        is_orm = False
        for line in self.file_lines:
            if 'extends BaseDao<' in line:
                is_orm = True
        rules = [JavaDocRule(self).set_all_rules_to_check(),
                 CommentRule(self).set_all_rules_to_check(),
                 IfElseRule(self).set_all_rules_to_check(),
                 GenericTypeRule(self).set_all_rules_to_check(),
                 MethodNameRule(self).set_all_rules_to_check()
                 ]
        if is_orm:
            rules.append(OrmRule(self).set_all_rules_to_check())
        self.set_rules(rules)
        self.sql_file_path = get_sql_file_path()
        with open(self.sql_file_path, 'r') as f:
            self.sql_file_lines = f.readlines()


class ServiceImplPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path=file_path, controller_name=controller_name)
        self.set_rules([CommentRule(self).set_all_rules_to_check(),
                        LegacyDirectoryPathRule(self).set_all_rules_to_check(),
                        AnnotationRule(self).set_all_rules_to_check(),
                        GenericTypeRule(self).set_all_rules_to_check(),
                        MethodNameRule(self).set_assert_rule(
                            "method_name_initial_should_not_be_capital").set_assert_rule(
                            "method_name_defination_initial_should_not_be_capital")
                        ])


class JspPage(Page):
    def __init__(self, file_path: str, controller_name: str):
        super().__init__(file_path=file_path, controller_name=controller_name)
        self.function_number = get_function_number(
            function_name=get_request_name(controller_name))
        if not self.function_number:
            log_message("=== JspPage ===\n"
                        "------------------------------------------------------\n"
                        "function number not found in csv, skip this file\n"
                        + file_path+"\n"
                        "------------------------------------------------------\n")
            return
        self.set_rules([JspRule(self).set_all_rules_to_check()])


if __name__ == "__main__":
    pass
