from packages.pages import *
import utils


class main():
    def run(self):
        controller_name = input("input controller file path: ")
        controller_file_path = utils.get_controller_file_path(controller_name)
        # controller_file_path = "abc.txt"  # debug
        service_names = utils.get_service_names(controller_file_path)
        service_file_paths = utils.get_service_file_paths(service_names)
        ControllerPage(file_path=controller_file_path).check_all_rules()
        for service_file_path in service_file_paths:
            print(service_file_path)
            ServicePage(file_path=service_file_path).check_all_rules()
        # ControllerPage().check_all_rules()
        # ServiceImplPage().check_all_rules()


if __name__ == "__main__":
    main().run()
