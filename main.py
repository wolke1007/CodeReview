from packages import pages as page
from packages import utils as util
from packages import rules as rule
import sys
import getopt
import re
import os


def main(file_path):
    controller_name = input(
        "input controller file path: ") if not file_path else file_path
    controller_name = controller_name[:-
                                      5] if ".java" in controller_name else controller_name
    paths = get_file_paths_by_controller_name(controller_name)
    # 檢查 Controller
    controller_check(paths, controller_name)
    # 檢查 Service
    service_check(paths, controller_name)
    # 檢查 ServiceImpl
    service_impl_check(paths, controller_name)
    # 檢查 Dao
    dao_check(paths, controller_name)
    # 檢查 JSP
    jsp_file_paths = util.get_jsp_file_paths(controller_name)
    if not jsp_file_paths:
        util.log_message("=== JSP FILE NOT FOUND IN PATH : {}/ ===".format(util.get_jsp_diretory_path() +
                         util.get_request_name(util.get_controller_file_path(controller_name))))
    for jsp_file_path in jsp_file_paths:
        page.JspPage(file_path=jsp_file_path,
                     controller_name=controller_name).check_all_rules()
    collect_all_single_if_else_error_log_lines()


def get_file_paths_by_controller_name(controller_name: str) -> dict:
    '''
    return controller_file_path, service_file_paths, serviceimpl_file_paths, dao_file_paths
    '''
    controller_file_path = util.get_controller_file_path(controller_name)
    service_names = util.get_service_names(controller_file_path)
    service_file_paths = util.get_service_file_paths(service_names)
    serviceimpl_file_paths = util.get_serviceimpl_file_paths(service_names)
    dao_names = util.get_dao_names(serviceimpl_file_paths)
    dao_file_paths = util.get_dao_file_paths(dao_names)
    paths = {"controller_file_path": controller_file_path,
             "service_file_paths": service_file_paths,
             "serviceimpl_file_paths": serviceimpl_file_paths,
             "dao_file_paths": dao_file_paths}
    return paths


def get_file_paths_by_legacy_controller_path(legacy_controller_path: str) -> dict:
    '''
    return controller_file_path, service_file_paths, serviceimpl_file_paths, dao_file_paths
    '''
    controller_file_path = util.get_project_root_path() + "/" + legacy_controller_path
    print(controller_file_path)
    service_names = util.get_service_names(controller_file_path)
    service_file_paths = util.get_service_file_paths(service_names)
    serviceimpl_file_paths = util.get_serviceimpl_file_paths(service_names)
    dao_names = util.get_dao_names(serviceimpl_file_paths)
    dao_file_paths = util.get_dao_file_paths(dao_names)
    paths = {"controller_file_path": controller_file_path,
             "service_file_paths": service_file_paths,
             "serviceimpl_file_paths": serviceimpl_file_paths,
             "dao_file_paths": dao_file_paths}
    return paths


def controller_check(paths: dict, controller_name=None):
    page.ControllerPage(file_path=paths.get("controller_file_path"),
                        controller_name=controller_name).check_all_rules()
                        

def service_check(paths: dict, controller_name=None):
    for service_file_path in paths.get("service_file_paths"):
        page.ServicePage(file_path=service_file_path,
                         controller_name=controller_name).check_all_rules()


def service_impl_check(paths: dict, controller_name=None):
    for serviceimpl_file_path in paths.get("serviceimpl_file_paths"):
        page.ServiceImplPage(file_path=serviceimpl_file_path,
                             controller_name=controller_name).check_all_rules()


def dao_check(paths: dict, controller_name=None):
    for dao_file_path in paths.get("dao_file_paths"):
        page.DaoPage(file_path=dao_file_path,
                     controller_name=controller_name).check_all_rules()


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
    with open(util.get_log_path(), 'w') as f:
        f.writelines([])
    if len(sys.argv) == 2:
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
    if len(sys.argv) == 3:
        page_pool = {"ControllerPage": {"obj": page.ControllerPage, "next": [service_check, service_impl_check, dao_check]},
                     "ServicePage": {"obj": page.ServicePage, "next": [service_impl_check, dao_check]},
                     "ServiceImplPage": {"obj": page.ServiceImplPage, "next": [dao_check]},
                     "DaoPage": {"obj": page.DaoPage, "next": None},
                     "JspPage": {"obj": page.JspPage, "next": None}
                     }
        page_meta = page_pool.get(sys.argv[2])
        if page_meta is None:
            print("沒有此種類型的 page: " + str(sys.argv[2]))
            exit()
        project_root_path = util.get_project_root_path()
        if re.search("/\w*Controller\.java", sys.argv[1]):
            controller_name = re.search("/\w*Controller\.java", sys.argv[1]).group()[1:-5]
            if re.search("controller/legacy", sys.argv[1]): # 若為 legacy controller 的情境
                paths = get_file_paths_by_legacy_controller_path(sys.argv[1])
            else:
                paths = get_file_paths_by_controller_name(controller_name)
        else:
            controller_name = None
            # TODO 這邊要解決若是非 controller 頁面時如何取得 paths 的問題
        page_obj = page_meta.get("obj")(project_root_path + "/" + sys.argv[1], controller_name)
        page_obj.check_all_rules()
        for check_func in page_meta.get("next"):
            check_func(paths)
    elif len(sys.argv) == 1:
        print("no arg")  # debug
        main(None)
    elif len(sys.argv) >= 3:
        print('Number of arguments:', len(sys.argv), 'arguments.')  # debug
        print('Argument List:', str(sys.argv))  # debug
