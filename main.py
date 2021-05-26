from packages import pages as page
from packages import utils as util
import sys, getopt


def main(file_path):
    with open(util.get_log_path(), 'w') as f:
        f.writelines([])
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
        util.log_message("=== JSP FILE NOT FOUND IN PATH : {}/===".format(util.get_jsp_diretory_path() + controller_name[:-10].lower()))
    for jsp_file_path in jsp_file_paths:
        page.JspPage(file_path=jsp_file_path, controller_name=controller_name).check_all_rules()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(file_path=sys.argv[1])
    elif len(sys.argv) == 1:
        print("no arg") # debug
        main(None)
    elif len(sys.argv) >= 3:
        print('Number of arguments:', len(sys.argv), 'arguments.') # debug
        print('Argument List:', str(sys.argv)) # debug
