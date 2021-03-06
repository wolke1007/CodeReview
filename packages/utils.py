import yaml
import re
import os
import pandas as pd
import subprocess


with open('config.yaml', 'r', encoding='utf-8') as stream:
    config = yaml.safe_load(stream)

PROJECT_ROOT_PATH = config.get('project_root_path')
OLD_PROJECT_ROOT_PATH = config.get('old_project_root_path')
REPOSITORY_DIRECTORY_PATH = config.get('repository_path')
SERVICE_DIRECTORY_PATH = config.get('service_directory_path')
SERVICEIMPL_DIRECTORY_PATH = config.get('serviceimpl_directory_path')
CONTROLLER_DIRECTORY_PATH = config.get('controller_directory_path')
DAO_DIRETORY_PATH = config.get('dao_directory_path')
SQL_DIRECTORY_PATH = config.get('sql_directory_path')
JSP_DIRETORY_PATH = config.get('jsp_directory_path')
JS_DIRETORY_PATH = config.get('js_directory_path')
CSV_FILE_PATH = config.get('csv_file_path')
LOG_PATH = config.get('log_path')
ignore_files = config.get('ignore_file_path_list')
independent_file_rules = config.get('independent_file_rules')


def get_project_root_path() -> str:
    return PROJECT_ROOT_PATH 


def get_service_names(file_path: str) -> list:
    with open(file_path, 'r') as file:
        lines = file.readlines()
    service_names = []
    check_service_name = False
    for line in lines:
        if not line:
            pass
        if "@Autowired" in line:
            check_service_name = True
            continue
        if check_service_name:
            check_service_name = False
            match_word = re.search(r"\w*\s\w*;", line)
            if match_word:
                service_names.append(match_word.group().split(';')[0].split(
                    ' ')[0])  # 找到的可能會是 ContactForCbcM mgr;//comment word
    return service_names


def get_service_file_paths(service_names: list) -> list:
    paths = []
    for service_name in service_names:
        if ignore_files and (service_name + ".java") in ignore_files:
            continue
        command = 'find {root}{service_dir_path} -name {file_name}.java'.format(
            root=PROJECT_ROOT_PATH,
            service_dir_path=SERVICE_DIRECTORY_PATH,
            file_name=service_name)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        path = str(p.stdout.readline())[2:-3]
        if path:
            paths.append(path)
        else:
            print("service file " + service_name + ".java not found")
    for path in paths:
        service_names = get_service_names(path)
        if service_names:
            inner_file_paths = get_service_file_paths(service_names)
            paths += inner_file_paths
    paths = list(set(paths))
    return paths


def get_serviceimpl_file_paths(service_names: list) -> list:
    paths = []
    for service_name in service_names:
        if ignore_files and (service_name + "Impl" + ".java") in ignore_files:
            continue
        command = 'find {root}{service_dir_path} -name {file_name}.java'.format(
            root=PROJECT_ROOT_PATH,
            service_dir_path=SERVICE_DIRECTORY_PATH,
            file_name=service_name + "Impl")
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        path = str(p.stdout.readline())[2:-3]
        if path:
            paths.append(path)
        else:
            print("serviceImpl file " + service_name + "Impl.java not found")
    return paths


def get_controller_file_path(controller_name: str) -> str:
    '''
    controller_name 需帶入 XXXController
    例: M3025Controller
    '''
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
        check_dao_name = False
        for line in lines:
            if not line:
                pass
            if "@Autowired" in line:
                check_dao_name = True
                continue
            if check_dao_name:
                check_dao_name = False
                match_word = re.search(r"\w*\s*\w*;", line)
                if match_word:
                    dao_names.append(match_word.group().split(';')[0].split(
                        ' ')[0])  # 找到的可能會是 ContactForCbcM mgr;//comment word
    return dao_names


def get_dao_file_paths(dao_names: list) -> list:
    dao_file_paths = []
    for dao_name in dao_names:
        if ignore_files and (dao_name + ".java") in ignore_files:
            continue
        command = 'find {root}{dao_dir} -name {file_name}.java'.format(
            root=PROJECT_ROOT_PATH,
            dao_dir=REPOSITORY_DIRECTORY_PATH,
            file_name=dao_name)
        p = subprocess.Popen(command, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        path = str(p.stdout.readline())[2:-3]
        if path:
            dao_file_paths.append(path)
        else:
            print("dao file " + dao_name + ".java not found")
    return dao_file_paths


def get_dao_file_root_path() -> str:
    return PROJECT_ROOT_PATH + DAO_DIRETORY_PATH


def get_function_number(function_name: str) -> str:
    '''
    回傳 010200 這種格式的 function number
    因為有讀取 CSV 所以有效率問題，不建議頻繁使用
    '''
    df = pd.read_csv(CSV_FILE_PATH)
    pattern = (df["Function Name"] == function_name)
    try:
        function_number = str(int(df[pattern]["Function Number"].values[0]))
    except IndexError:
        return None
    except ValueError:
        return None  # cannot convert float NaN to integer
    if len(function_number) < 6:
        return "0"+function_number
    return function_number


def get_request_name(controller_file_path: str) -> str:
    if not controller_file_path or not os.path.isfile(controller_file_path):
        return None
    with open(controller_file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if "@RequestMapping(" in line:
            match = re.search(r'/\w*', line)  # match.group() => /m2213
            return match.group()[1:] if match else None
    return None


def get_jsp_file_paths(controller_name: str) -> list:
    result = []
    jsp_directory_path = get_jsp_diretory_path()
    jsp_file_directory_full_path = jsp_directory_path + \
        get_request_name(get_controller_file_path(controller_name))
    for _, _, jsp_file_names in os.walk(jsp_file_directory_full_path):
        jsp_file_full_paths = [jsp_file_directory_full_path +
                               '/'+file_name for file_name in jsp_file_names]
        result += jsp_file_full_paths
    return result


def get_log_path():
    return LOG_PATH


def log_message(message: str):
    log_message = "{message}".format(message=message)
    with open(get_log_path(), 'a') as file:
        file.writelines([log_message])


def get_independent_file_rules() -> list:
    return independent_file_rules


def is_chinese_text_exist(text: str) -> bool:
    for ch in text:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


if __name__ == "__main__":
    assert get_project_root_path() == "/Users/cloud.chen/code/taifex-fdms-cms"
    assert get_service_file_paths(["a", "b"]) == ["/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/a.java",
                                                  "/Users/cloud.chen/code/taifex-fdms-cms/src/main/java/com/mitake/infra/repository/app/service/b.java"]
    assert get_service_names("abc.java") == ["S1304Service"]
    assert get_function_number("a01sz05") == "010200"
    assert get_jsp_file_paths("A01sz05Controller") == ['/Users/cloud.chen/code/taifex-fdms-cms/src/main/webapp/WEB-INF/jsp/a01sz05/report.jsp',
                                                       '/Users/cloud.chen/code/taifex-fdms-cms/src/main/webapp/WEB-INF/jsp/a01sz05/index.jsp']
    assert get_log_path() == "./log.txt"
    log_message("1234")
