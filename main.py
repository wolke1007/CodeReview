from packages.pages import *
from packages.utils import *


class main():
    def run(self):
        controller_name = input("input controller file path: ")
        controller_name = controller_name[:-5] if ".java" in controller_name else controller_name
        controller_file_path = get_controller_file_path(controller_name)
        # controller_file_path = "abc.txt"  # debug
        service_names = get_service_names(controller_file_path)
        service_file_paths = get_service_file_paths(service_names)
        ControllerPage(file_path=controller_file_path, controller_name=controller_name).check_all_rules()
        for service_file_path in service_file_paths:
            print(service_file_path)
            ServicePage(file_path=service_file_path).check_all_rules()


if __name__ == "__main__":
    main().run()
