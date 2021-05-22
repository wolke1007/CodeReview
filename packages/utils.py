import yaml
import re
import pandas as pd


with open('config.yaml', 'r', encoding='utf-8') as stream:
    config = yaml.safe_load(stream)

PROJECT_ROOT_PATH = config.get('project_root_path')
OLD_PROJECT_ROOT_PATH = config.get('old_project_root_path')
SERVICE_DIRECTORY_PATH = config.get('service_directory_path')
SERVICEIMPL_DIRECTORY_PATH = config.get('serviceimpl_directory_path')
CONTROLLER_DIRECTORY_PATH = config.get('controller_directory_path')
DAO_DIRETORY_PATH = config.get('dao_directory_path')
SQL_DIRECTORY_PATH = config.get('sql_directory_path')
JSP_DIRETORY_PATH = config.get('jsp_directory_path')
JS_DIRETORY_PATH = config.get('js_directory_path')
CSV_FILE_PATH = config.get('csv_file_path')


def get_service_names(controller_file_path: str) -> list:
    with open(controller_file_path, 'r') as file:
        lines = file.readlines()
    service_names = []
    for line in lines:
        match_word = re.search(r"\.S\d*Service", line)
        if match_word:
            service_names.append(match_word.group()[1:])  # 找到的會是 .S0101Service
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


def get_serviceimpl_file_paths(service_names: list) -> list:
    paths = []
    for service_name in service_names:
        paths.append("{root}{serviceimpl_dir_path}/{serviceimpl_name}.{file_extension}".format(
            root=PROJECT_ROOT_PATH,
            serviceimpl_dir_path=SERVICEIMPL_DIRECTORY_PATH,
            serviceimpl_name=service_name + "Impl",
            file_extension="java"))
    return paths


def get_controller_file_path(controller_name: str) -> str:
    return "{root}{controller_dir_path}/{controller_name}.{file_extension}".format(
        root=PROJECT_ROOT_PATH,
        controller_dir_path=CONTROLLER_DIRECTORY_PATH,
        controller_name=controller_name,
        file_extension="java")


def get_sql_file_path() -> str:
    return "{root}{sql_directory_path}".format(
        root=PROJECT_ROOT_PATH,
        sql_directory_path=SQL_DIRECTORY_PATH)


def get_old_project_file_path(file_path: str) -> str:
    return OLD_PROJECT_ROOT_PATH + "/" + file_path


def get_jsp_diretory_path() -> str:
    return PROJECT_ROOT_PATH + JSP_DIRETORY_PATH


def get_js_diretory_path() -> str:
    return PROJECT_ROOT_PATH + JS_DIRETORY_PATH


def get_dao_names(serviceimpl_file_paths: list) -> list:
    dao_names = []
    for serviceimpl_file_path in serviceimpl_file_paths:
        with open(serviceimpl_file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            match_word = re.search(r"\s\w*Dao\s", line)
            if match_word:
                # 找到的會是 " A01arDao "
                dao_names.append(match_word.group()[1:-1])
    return dao_names


def get_dao_file_paths(dao_names: list) -> list:
    dao_file_paths = []
    for dao_name in dao_names:
        dao_path = "{root}{dao_dir}/{dao_name}.{file_ext}".format(
            root=PROJECT_ROOT_PATH, dao_dir=DAO_DIRETORY_PATH, dao_name=dao_name, file_ext="java")
        dao_file_paths.append(dao_path)
    return dao_file_paths


def get_function_number(controller_name: str) -> str:
    '''
    回傳 010200 這種格式的 function number
    '''
    df = pd.read_csv(CSV_FILE_PATH)
    pattern = (df["Function Name"] == controller_name.lower())
    function_number = str(int(df[pattern]["Function Number"].values[0]))
    if len(function_number) < 6:
        return "0"+function_number
    return function_number

if __name__ == "__main__":
    assert get_service_file_paths(["a", "b"]) == ["/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/a.java",
                                                  "/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/b.java"]
    assert get_service_names("abc.java") == ["S1304Service"]
    assert get_function_number("a01sz05") == "010200"
