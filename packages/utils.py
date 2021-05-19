import yaml
import re


with open('config.yaml', 'r', encoding='utf-8') as stream:
    config = yaml.safe_load(stream)

PROJECT_ROOT_PATH = config.get('project_root_path')
SERVICE_DIRECTORY_PATH = config.get('service_directory_path')
CONTROLLER_DIRECTORY_PATH = config.get('controller_directory_path')

def get_service_names(controller_file_path: str) -> list:
    with open(controller_file_path, 'r') as file:
        lines = file.readlines()
    service_names = []
    for line in lines:
        match_word = re.search(r"\.S\d*Service", line)
        if match_word:
            service_names.append(match_word.group()[1:]) # 找到的會是 .S0101Service
    return service_names

def get_service_file_paths(service_names: list) -> list:
    paths = []
    for service_name in service_names:
        paths.append("{root}{service_dir_path}/{service_name}.{file_extension}".format(
            root=PROJECT_ROOT_PATH,
            service_dir_path=SERVICE_DIRECTORY_PATH,
            service_name=service_name,
            file_extension="java"))
    return paths

def get_controller_file_path(controller_name: str) -> str:
    return "{root}{controller_dir_path}/{controller_name}.{file_extension}".format(
            root=PROJECT_ROOT_PATH,
            controller_dir_path=CONTROLLER_DIRECTORY_PATH,
            controller_name=controller_name,
            file_extension="java")


if __name__ == "__main__":
    assert get_service_file_paths(["a", "b"]) == ["/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/a.java",
                                                 "/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/b.java"]
    assert get_service_names("abc.txt") == ["S1304Service"]