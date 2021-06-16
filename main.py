from packages import pages as page
from packages import utils as util
from packages import rules as rule
import sys, getopt, re, os


def main(file_path):
    controller_name = input("input controller file path: ") if not file_path else file_path
    controller_name = controller_name[:-5] if ".java" in controller_name else controller_name
    controller_file_path = util.get_controller_file_path(controller_name)
    # 檢查 Controller
    page.ControllerPage(file_path=controller_file_path, controller_name=controller_name).check_all_rules()
    # 檢查 Service
    service_names = util.get_service_names(controller_file_path)
    service_file_paths = util.get_service_file_paths(service_names)
    for service_file_path in service_file_paths:
        page.ServicePage(file_path=service_file_path, controller_name=controller_name).check_all_rules()
    # 檢查 ServiceImpl
    serviceimpl_file_paths = util.get_serviceimpl_file_paths(service_names)
    for serviceimpl_file_path in serviceimpl_file_paths:
        page.ServiceImplPage(file_path=serviceimpl_file_path, controller_name=controller_name).check_all_rules()
    # 檢查 Dao
    dao_names = util.get_dao_names(serviceimpl_file_paths)
    dao_file_paths = util.get_dao_file_paths(dao_names)
    for dao_file_path in dao_file_paths:
        page.DaoPage(file_path=dao_file_path, controller_name=controller_name).check_all_rules()
    # 檢查 JSP
    jsp_file_paths = util.get_jsp_file_paths(controller_name)
    if not jsp_file_paths:
        util.log_message("=== JSP FILE NOT FOUND IN PATH : {}/ ===".format(util.get_jsp_diretory_path() + controller_name[:-10].lower()))
    for jsp_file_path in jsp_file_paths:
        page.JspPage(file_path=jsp_file_path, controller_name=controller_name).check_all_rules()
    collect_all_single_if_else_error_log_lines()


def do_check_with_independent_file_rules(file_path: str):
    p = page.CustomizePage(file_path)
    rules = util.get_independent_file_rules()
    print(rules)
    for rule_dict in rules:
        for rule_name in rule_dict:
            r = getattr(sys.modules[rule.__name__], rule_name)(p)
            for rule_detail in rule_dict.get(rule_name):
                print("set rule:  " + rule_detail)
                r.set_assert_rule(rule_detail)
            p.set_rule(r)
    print("do check all rules.")
    p.check_all_rules()

def collect_all_single_if_else_error_log_lines():
    log_with_lines = ['不要有單行if, for statment  \n請檢查下述之行數並更正，謝謝  \n']
    with open('log.txt', 'r') as file:
        lines = file.readlines()
    for count, line in enumerate(lines, start=0):
        if "if_statement_should_with_bracket_mark" in line:
            log_with_lines.append(lines[count + 1])
    with open('log.txt', 'a') as file:
        file.writelines(log_with_lines)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        with open(util.get_log_path(), 'w') as f:
            f.writelines([])
        if "-h" == sys.argv[1] or "--help" == sys.argv[1]:
            print("usage:\tmain.py\t[-h] [--help] [<controller name>] [<controller file name>] \n"
                "\t\t[--show_rules] [--show] [-s]\n"
                "\n"
                "Commands:\n"
                "  -h  --help  顯示此訊息\n"
                "  <controller name>\n"
                "  <controller file name>  開始檢查該 controller 相關檔案 例如：M300401Controller  or  M300401Controller.java\n"
                "  --show_rules\n"
                "  --show\n"
                "  -s  會顯示出所有 Rule 大項目名稱以及細項名稱\n"
                )
            exit()
        if "--show_rules" == sys.argv[1] or "--show" == sys.argv[1] or "-s" == sys.argv[1]:
            rules = rule.get_all_rules()
            rules_dict = {}
            for r in rules:
                method_names = [method_name for method_name in dir(r)
                        if callable(getattr(r, method_name)) and "__" not in method_name and method_name[0] != "_" and "rule" not in method_name]
                rules_dict[r.__name__] = method_names
            for r in rules_dict:
                print("  - " + r + " :")
                for method_name in rules_dict.get(r):
                    print("    - " + method_name)
            exit()
        if re.search(r"\w*/\w*", sys.argv[1]):
            if sys.argv[1].startswith("src", 0, 3):
                file_path = os.path.join(util.PROJECT_ROOT_PATH, sys.argv[1])
            else:
                file_path = sys.argv[1]
            do_check_with_independent_file_rules(file_path)
        else:
            main(file_path=sys.argv[1])
    elif len(sys.argv) == 1:
        print("no arg") # debug
        main(None)
    elif len(sys.argv) >= 3:
        print('Number of arguments:', len(sys.argv), 'arguments.') # debug
        print('Argument List:', str(sys.argv)) # debug
