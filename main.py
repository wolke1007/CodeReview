from packages.pages import *


class main():
    def run(self):
        ServicePage().check_all_rules()
        ControllerPage().check_all_rules()
        ServiceImplPage().check_all_rules()


if __name__ == "__main__":
    main().run()
