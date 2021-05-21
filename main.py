from packages.pages import *
from packages.utils import *


class main():
    def run(self):
        with open("log.txt", 'w') as f:
            f.writelines([])
        controller_name = input("input controller file path: ")
        controller_name = controller_name[:-5] if ".java" in controller_name else controller_name
        controller_file_path = get_controller_file_path(controller_name)
        # 檢查 Controller
        ControllerPage(file_path=controller_file_path, controller_name=controller_name).check_all_rules()
        # 檢查 Service
        service_names = get_service_names(controller_file_path)
        service_file_paths = get_service_file_paths(service_names)
        for service_file_path in service_file_paths:
            ServicePage(file_path=service_file_path, controller_name=controller_name).check_all_rules()
        # 檢查 ServiceImpl
        serviceimpl_file_paths = get_serviceimpl_file_paths(service_names)
        for serviceimpl_file_path in serviceimpl_file_paths:
            ServiceImplPage(file_path=serviceimpl_file_path, controller_name=controller_name).check_all_rules()
        # 檢查 Dao
        dao_names = get_dao_names(serviceimpl_file_paths)
        dao_file_paths = get_dao_file_paths(dao_names)
        for dao_file_path in dao_file_paths:
            DaoPage(file_path=dao_file_path, controller_name=controller_name).check_all_rules()

if __name__ == "__main__":
    main().run()
