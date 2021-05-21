from utils import *
from typing import Callable
from enum import Enum
import re
import time
import os
import sys
import abc
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class Rule(abc.ABC):
    def __init__(self, page):
        self.type = type(self).__name__
        # print(self.type)  # debug
        self.assert_logics = []
        self.page = page
        # 需要印出來的 log 全部 append 在這個 list 裡面並在 do_rule_check 最後一次一起印
        self.error_logs = ["=== {name} {rule} === \n".format(
            name=self.page.file_path.split("/")[-1], rule=self.__class__.__name__)]
        self.log_path = "./log.txt"
        self.log_template = ("------------------------------------------------------\n"
                             "violate rule: \"{rule}\"\n"
                             "line: {line} \n"
                             "file: {file} \n"
                             "code: >>>{code}\n"
                             "recommend: {recommend}\n"
                             "------------------------------------------------------\n\n")

    def set_all_rules_to_check(self):
        method_names = [method_name for method_name in dir(self)
                        if callable(getattr(self, method_name)) and "__" not in method_name and method_name[0] != "_" and "rule" not in method_name]
        for method_name in method_names:
            self.set_assert_rule(method_name)
        return self

    def do_rule_check(self):
        self.__check_with_assert_rule()
        # collect all error messages, then log into file
        self.__log_error_line()

    def set_assert_rule(self, assert_rule_name: str):
        self.assert_logics.append(getattr(self, assert_rule_name))
        return self

    def __check_with_assert_rule(self):
        for assert_logic in self.assert_logics:
            assert_logic()

    def __log_error_line(self):
        with open(self.log_path, 'a') as file:
            file.writelines(self.error_logs)

    def _log_error_line(self, count: int, function_name: str, line: str, recommend: str):
        self.error_logs.append(
            self.log_template.format(
                file=self.page.file_path.split("/")[-1],
                line=count + 1,
                rule=function_name,
                code=line,
                recommend=recommend
            ))

    def _log_error_message(self, function_name: str, message: str, recommend: str):
        self.error_logs.append(
            self.log_template.format(
                file=self.page.file_path.split("/")[-1],
                line="None",
                rule=function_name,
                code=message,
                recommend=recommend
            ))

# 註解


class JavaDocRule(Rule):
    """
    - JavaDoc註解是否有寫
        - 主要是 Interface Service 內的方法說明 以及 Dao內的方法說明
    - 註解格式是否正確
    - 註解參數是否正確
    ex.
        /**
         * 查詢 A02_DEADLINE_AS
         * @param deaasKind
         * @param deaasId
         * @param deaasDate
         * @return
         */
        public List<Map<String, Object>> findA02DeadlineAsData(String deaasKind, String deaasId, int deaasDate) {
        .
        .
        .
    }
    """

    def __init__(self, page):
        super().__init__(page)

    def java_doc_should_exist(self):
        '''
        檢查 JavaDoc 註解是否有寫
        '''
        # FIXME 這邊先 hardcode 寫死判斷依據，等有好想法再來改寫
        # 可能出現的bug是，如果回傳型態不在清單裡面的話則會判斷不到
        return_types = ["List<Map<String, Object>>",
                        "int", "boolean",
                        "List<List<Map<String, Object>>>",
                        "Map<String, Object>",
                        "String"]
        for count, line in enumerate(self.page.file_lines, start=0):
            for return_type in return_types:
                pattern = return_type + r'\s\w*\('
                match = re.search(pattern, line)
                if match:
                    if "*/" not in self.page.file_lines[count - 1] and "*/" not in self.page.file_lines[count - 2]:
                        self._log_error_line(
                            count, self.java_doc_should_exist.__name__, line,
                            "目前 java doc 的規範為 : Interface Service 內的方法說明以及 Dao 內的方法需寫上 java doc")

    # TODO 註解格式是否正確
    # TODO 註解參數是否正確


class CommentRule(Rule):
    """
    - 方法內的註解分為2種
        - 說明註解: 用來說明使用
        - 邏輯註解: 程式邏輯
    - 說明註解留下
    - 邏輯註解移除
    """

    def __init__(self, page):
        super().__init__(page)

    def code_comment_should_not_exist(self):
        '''
        程式的 "邏輯註解" 不該留下，商業邏輯類的 "說明註解" 則留下以利後續程式維護
        目前只能辨識出有中文的則代表是說明註解
        其他的則標記出來做人工審查
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            # 這兩個檔案不做驗證，裡面龍蛇混雜不好自動化處理
            if "NativeQueryDao" in line or "NativeQueryDao2" in line:
                break
            if "//" not in line:
                continue
            chinese_in_line = False
            comment_start = False
            for ch in line:
                if ch == "/":
                    comment_start = True
                if not comment_start:
                    continue
                if u'\u4e00' <= ch <= u'\u9fff':
                    chinese_in_line = True  # 註解後有中文，判斷為說明邏輯
                    break
            if chinese_in_line:
                continue
            code_pattern1 = '.*//.*\(.*\)'
            code_pattern2 = '.*//.*\=.*'
            match_parentheses = re.search(code_pattern1, line)
            match_equal_mark = re.search(code_pattern2, line)
            if match_parentheses or match_equal_mark:
                self._log_error_line(
                    count, self.code_comment_should_not_exist.__name__, line,
                    '程式的 "邏輯註解" 不該留下，商業邏輯類的 "說明註解" 則留下以利後續程式維護')

# # 風格


class IfElseRule(Rule):
    """
    - 不要有單行if, for statment
    """

    def __init__(self, page):
        super().__init__(page)

    def if_statement_should_with_bracket_mark(self):
        '''
        搜尋 if 關鍵字，檢查是否同時有 { 跟在後面
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            # 這兩個檔案不做驗證，因為裡面龍蛇混雜
            if "NativeQueryDao" in line or "NativeQueryDao2" in line:
                break
            if ("\tif (" in line or
                " if (" in line or
                "\tif(" in line or
                    " if(" in line) and "{" not in line and "{" not in self.page.file_lines[count + 1]:
                self._log_error_line(
                    count, self.if_statement_should_with_bracket_mark.__name__, line,
                    recommend='不要有單行if, for statment')
            if ("\tfor (" in line or
                " for (" in line or
                "\tfor(" in line or
                    " for(" in line) and "{" not in line and "{" not in self.page.file_lines[count + 1]:
                self._log_error_line(
                    count, self.if_statement_should_with_bracket_mark.__name__, line,
                    recommend='不要有單行if, for statment')


class UnderLineRule(Rule):
    """
    - 保留原專案之下底線
    - 假設原系統的功能連結為 `a01sr08_13.do`
    - sql應為 `UPDATE SMS.dbo.MENULINK SET NEW_LINK = '/a01sr08_13/index' , USE_NEW_LINK = 'Y' WHERE Link = 'a01sr08_13.do?method=query';`
    - Controller Name 應為 A01sr08_13Controller
    - Controller 之 RequestMapping 應為 `@RequestMapping("/a01sr08_13")`
    - 收納該功能 jsp 及 js 檔案的資料夾應為 `a01sr08_13`
    """

    def __init__(self, page):
        super().__init__(page)

    def controller_name_should_same_as_do_query_naming(self) -> bool:
        '''
        用 controller 的檔名去尋找是否存在於 phase-1-data.sql 中
        如果不存在則有兩種可能:
            1. controller 的命名與 update sql 中不一致
            例如: 
                Controller: A010203
                SQL: a0102_03
            2. 撰寫者沒有更新 update sql 導致搜尋不到
        '''
        controller_name = self.page.controller_name[:-
                                                    10][0].lower() + self.page.controller_name[:-10][1:]
        for line in self.page.sql_file_lines:
            pattern = '\/' + controller_name + '\/'
            # sql 裡面有可能是大寫或小寫開頭，故要 ignorecase
            match = re.search(pattern, line, re.IGNORECASE)
            if match is not None:
                return True
            if "_" in controller_name:
                continue  # 如果原來就已經有底線就不用猜測了，如果找完整個檔案都沒有就是沒有
            # 在所有位置加上底線試試看，如果有則回報答案
            find_guess_name = self._guess_name_with_underline_(
                line, controller_name)
            # 不一樣代表有找到
            if controller_name != find_guess_name:
                message = "controller 的命名應為: " + \
                    find_guess_name[0].upper() + find_guess_name[1:] + \
                    " 目前叫做: " + controller_name
                self._log_error_message(
                    function_name=self.controller_name_should_same_as_do_query_naming.__name__,
                    message=message,
                    recommend='保留原專案之下底線，'+message)
                return False
        message = "controller 的命名: " + controller_name + \
            " 於 update sql 中不存在，請確認 commit 是否有更新此檔案"
        self._log_error_message(
            function_name=self.controller_name_should_same_as_do_query_naming.__name__,
            message=message,
            recommend=message)
        return False

    def requestmapping_name_should_same_as_do_query_naming(self) -> bool:
        '''
        若 do action 的 query 原來有底線
        則 RequestMapping 也需要有底線
        例：
            do action:  a01sr08_33
            RequestMapping: @RequestMapping("/a01sr08_33")
        '''
        request_name = ""
        for line in self.page.file_lines:
            if "@RequestMapping" not in line:
                continue
            match = re.search(r'/\w*', line, re.IGNORECASE)
            if match is not None:
                request_name = match.group()[1:]
                for line in self.page.sql_file_lines:
                    if request_name in line:
                        return True  # 用原來的名字就找到了
                    if "_" in request_name:
                        continue
                        # 如果原來就已經有底線就不用猜測了，如果找完整個檔案都沒有就是沒有
                    find_guess_name = self._guess_name_with_underline_(
                        line, request_name)
                    # 不一樣代表有找到
                    if request_name != find_guess_name:
                        self._log_error_message(
                            function_name=self.requestmapping_name_should_same_as_do_query_naming.__name__,
                            message="request 的命名應為: " + find_guess_name + " 目前叫做: " + request_name,
                            recommend='若 do action 的 query 原來有底線則 RequestMapping 也需要有底線')
                        return False
        message = "request 的命名: " + request_name + \
            " 於 update sql 中不存在，請確認 commit 是否有更新此檔案"
        self._log_error_message(
            function_name=self.requestmapping_name_should_same_as_do_query_naming.__name__,
            message=message,
            recommend=message)
        return False

    def jsp_directory_name_should_same_as_do_query_naming(self):
        '''
        若 do action 的 query 原來有底線
        則 jsp 資料夾也需要有底線
        例：
            do action: a01sr08_33
            jsp folder path: /Users/cloud.chen/code/taifex-fdms-cms/src/main/webapp/WEB-INF/jsp/a01sr08_33
        '''
        controller_name = self.page.controller_name[:-10]
        jsp_dir_name = controller_name

        # 先看 controller name 有沒有在 sql file 中
        for line in self.page.sql_file_lines:
            pattern = '\/' + controller_name + '\/'
            # sql 裡面有可能是大寫或小寫開頭，故要 ignorecase
            match = re.search(pattern, line, re.IGNORECASE)
            if match is not None:
                jsp_dir_name = match.group()[1:-1]
                break
        else:
            message = "在 sql file 裡找不到 controller name: {}".format(
                controller_name)
            self._log_error_message(
                function_name=self.jsp_directory_name_should_same_as_do_query_naming.__name__,
                message=message,
                recommend=message)
            return
        full_jsp_diretory_path = get_jsp_diretory_path() + jsp_dir_name
        if not os.path.isdir(full_jsp_diretory_path):
            # 如果有在 sql file 中但沒找到則報錯
            message = "\n{}\njsp 資料夾名稱: {} 在對應路徑找不到資料夾".format(
                full_jsp_diretory_path, jsp_dir_name)
            self._log_error_message(
                function_name=self.jsp_directory_name_should_same_as_do_query_naming.__name__,
                message=message,
                recommend=message)
            return

    def js_directory_name_should_same_as_do_query_naming(self):
        '''
        若 do action 的 query 原來有底線
        則 js 資料夾也需要有底線
        例：
            do action: a01sr08_33
            js folder path: /Users/cloud.chen/code/taifex-fdms-cms/src/main/resources/static/js/a01sr08_33
        '''
        controller_name = self.page.controller_name[:-10]
        js_dir_name = controller_name

        # 先看 controller name 有沒有在 sql file 中
        for line in self.page.sql_file_lines:
            pattern = '\/' + controller_name + '\/'
            # sql 裡面有可能是大寫或小寫開頭，故要 ignorecase
            match = re.search(pattern, line, re.IGNORECASE)
            if match is not None:
                js_dir_name = match.group()[1:-1]
                break
        else:
            message = "在 sql file 裡找不到 controller name: {}".format(
                controller_name)
            self._log_error_message(
                function_name=self.js_directory_name_should_same_as_do_query_naming.__name__,
                message=message,
                recommend=message)
            return
        full_js_diretory_path = get_js_diretory_path() + js_dir_name
        if not os.path.isdir(full_js_diretory_path):
            # 如果有在 sql file 中但沒找到則報錯
            message = "\n{}\njs 資料夾名稱: {} 在對應路徑找不到資料夾".format(
                full_js_diretory_path, js_dir_name)
            self._log_error_message(
                function_name=self.js_directory_name_should_same_as_do_query_naming.__name__,
                message=message,
                recommend=message)
            return

    def _guess_name_with_underline_(self, line: str, name: str) -> str:
        '''
        在所有位置加上底線試試看，如果有則回報答案
        '''
        name = name[0].lower() + name[1:]
        for index in range(len(name), 0, -1):
            tmp_list = list(name)
            tmp_list.insert(index, "_")
            controller_name_with_underline = "".join(tmp_list)
            pattern = '\/' + controller_name_with_underline + '\/'
            # sql 裡面有可能是大寫或小寫開頭，故要 ignorecase
            match = re.search(pattern, line, re.IGNORECASE)
            if match is not None:
                return controller_name_with_underline
        return name


class LegacyDirectoryPathRule(Rule):
    """
    - 遷移到 legacy 內的原系統程式碼，應以新系統內之legacy為根目錄之後按照原系統的 package 來擺放
    - 例如新系統的 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy`
    - 裡面要放置原系統內的 `/src/com/taifex/r2/web/m03`
    - 遷移後的路徑會是 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy/src/com/taifex/r2/web/m03`
    """

    def __init__(self, page):
        super().__init__(page)

    def legacy_file_name_and_path_should_be_same_as_old_project(self):
        '''
        檢查 import 中的 package 路徑，若有 legacy 字串檢查是否於專案有一樣的路徑
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            if "import" not in line:
                continue
            package_name = line.split(" ")[1]
            if "legacy" in package_name:
                # 已知 MultipartDispatch 系列都沒有依照對應路徑擺放，故略過
                if "MultipartDispatch" in line:
                    continue
                # +7 是代表從 legacy 之後開始，-1 則是為了要避免擷取到看不到的換行符號
                old_file_path = package_name[package_name.index(
                    "legacy")+7:-1].replace(".", "/").replace(";", ".java")
                old_file_path = get_old_project_file_path(old_file_path)
                if not os.path.isfile(old_file_path):
                    self._log_error_line(
                        count, self.legacy_file_name_and_path_should_be_same_as_old_project.__name__, line,
                        '檢查 import 中的 package 路徑，若為 legacy 檢查是否使用與舊專案一樣的路徑')

# # 程式碼


class RequestMethodRule(Rule):
    """
    - Controller內的進入點，接受的Get Post 要把關，不要同時接受 Get 及 Post 的，如果有要問開發者否有必要
    - 原則上是進度功能首頁會是走Get，其他行為都用Post

    // 推薦的寫法，GET POST 他只能設定一種方式
    @GetMapping(value = "/index/doQuery")
    或
    @PostMapping(value = "/index/doQuery")
    public ModelAndView doQuery(HttpServletRequest request, HttpServletResponse response, HttpSession session,
            RedirectAttributes redirectAttrs) {

    // 另外這個寫法可以使用
    // 只是不要是GET POST都支援的作法
    @RequestMapping(value = "/index/doQuery", method = { RequestMethod.GET, RequestMethod.POST })
    public ModelAndView toQuery(HttpServletRequest request, HttpServletResponse response, HttpSession session) {
    """

    def __init__(self, page):
        super().__init__(page)

    def should_not_allow_both_get_and_post_method(self):
        '''
        檢查是否同時有 RequestMethod.GET 與 RequestMethod.POST
        '''
        new_method = False
        request_get = False
        request_post = False
        for count, line in enumerate(self.page.file_lines, start=0):
            if "@RequestMapping(" in line:
                new_method = True
            if new_method:
                if "RequestMethod.GET" in line:
                    request_get = True
                if "RequestMethod.POST" in line:
                    request_post = True
                if request_get and request_post:
                    self._log_error_line(
                        count, self.should_not_allow_both_get_and_post_method.__name__, line,
                        recommend="目前撰寫規範不允許同時有 RequestMethod.GET 與 RequestMethod.POST，除非有特殊需求還請提出解釋")
                if ")" in line:
                    new_method = False
                    request_get = False
                    request_post = False


class ServiceImplAnnotationRule(Rule):
    """
    - ServiceImpl內的方法，從介面實作的請都記得標上 `@Override`
    - 要是裡面的方法是 insert update delete 需要加上 @Transactional
    @Transactional
        @Override
        public int deleteA01ar(String userId) {
                return a01arDao.deleteA01ar(userId);
        }
    """

    def __init__(self, page):
        super().__init__(page)

    def method_should_add_override_annotation(self):
        '''
        檢查每個方法在定義時前面一行要有 @Override
        預期每個方法都是用 public 宣告
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            if "implements" in line:
                continue
            if "public" in line:
                # 前一行或前兩行至少要有 @Override annotation 否則報錯
                if "@Override" not in self.page.file_lines[count - 1] and "@Override" not in self.page.file_lines[count - 2]:
                    self._log_error_line(
                        count, self.method_should_add_override_annotation.__name__, line,
                        '檢查每個方法在定義時前面要有 @Override')

    def method_should_add_transaction_annotation(self):
        '''
        update insert delete 該要有 @Transaction
        檢查每個方法在定義時前一行或前兩行要有 @Transaction
        '''
        transactional_method_types = ["update", "insert", "delete"]
        for count, line in enumerate(self.page.file_lines, start=0):
            if "implements" in line:
                continue
            if "public" in line:
                for transactional_method_type in transactional_method_types:
                    if transactional_method_type in line:
                        # 前一行或前兩行至少要有 @Override annotation 否則報錯
                        if "@Transaction" not in self.page.file_lines[count - 1] and "@Transaction" not in self.page.file_lines[count - 2]:
                            self._log_error_line(
                                count, self.method_should_add_transaction_annotation.__name__, line,
                                'update insert delete 該要有 @Transaction')

    def method_should_using_restricted_name(self):
        '''
        檢查每個方法使用限制的動詞當做名稱 "update", "insert", "delete", "find", "get", "query", "select"
        '''
        restrict_method_types = ["update", "insert",
                                 "delete", "find", "get", "query", "select"]
        for count, line in enumerate(self.page.file_lines, start=0):
            if "implements" in line:
                continue
            if "public" in line:
                using_properly_name = False
                for restrict_method_type in restrict_method_types:
                    if restrict_method_type in line:
                        using_properly_name = True
                        break
                if not using_properly_name:
                    self._log_error_message(
                        function_name=self.method_should_using_restricted_name.__name__,
                        message='dao 方法的命名應使用: "find", "get", "query", "select" "update", "insert", "delete"，目前叫做: ' + line,
                        recommend='dao 方法的命名應使用: "find", "get", "query", "select" "update", "insert", "delete"')


class GenericTypeRule(Rule):
    """
    - List 的型別要指定 不要是沒指定或? `List<?>`
    """

    def __init__(self, page):
        super().__init__(page)

    def should_not_using_generic_type(self):
        '''
        搜尋所有 <xxxx> 的 pattern 檢查是否有 ? 在裡面
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            angle_bracket = re.search(r'<.*>', line)
            if angle_bracket is not None and "?" in angle_bracket.group():
                self._log_error_line(
                    count, self.should_not_using_generic_type.__name__, line,
                    recommend="目前撰寫規範為若已知回傳型態，則不允許使用 ? 這種泛型回傳型態")


class MethodNameRule(Rule):
    """
    - 方法名稱不要大寫開頭
    """

    def __init__(self, page):
        super().__init__(page)

    def method_name_initial_should_not_be_capital(self):
        '''
        搜尋所有 xxx.xxx 的 pattern 並把 . 後面的部分當作 method name 做檢查
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            # 這兩個檔案不做驗證，因為裡面有 SQL 語法存在
            if "NativeQueryDao" in line or "NativeQueryDao2" in line:
                break
            if "RequestMethod.GET" in line or "RequestMethod.POST" in line:
                continue
            if "package " in line or "import " in line:
                continue
            method_name = re.search(r'\w\.\w*', line)
            # 若整個是大寫，有可能是 BigDecimal.ZERO 的 ZERO 這種情境
            method_name_all_isupper = True
            if method_name is not None:
                print(method_name.group())
                for char in method_name.group()[2:]:
                    if char.islower():
                        method_name_all_isupper = False
                        break
            if method_name is not None and method_name.group()[2].isupper() and not method_name_all_isupper :
                self._log_error_line(
                    count, self.method_name_initial_should_not_be_capital.__name__, line,
                    recommend='方法名稱不要大寫開頭')

    def method_name_defination_initial_should_not_be_capital(self):
        '''
        搜尋所有定義方法的命名部分 {blank}method_name( 用這樣的 pattern 下去找
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            # if re.search(r'\w\.\w', line):
            # continue  # 表示是 method_name_initial_should_not_be_capital 的情況，跳過
            if " new " in line:
                continue  # return new ModelAndView(INDEX_VIEW) 的情況
            public_method = re.search(r'public\s\w*\s\w*\(', line)
            public_method_name_is_upper = None if public_method is None else public_method.group(
            ).split(" ")[-1][0].isupper()
            private_method = re.search(r'private\s\w*\s\w*\(', line)
            private_method_name_is_upper = None if private_method is None else private_method.group(
            ).split(" ")[-1][0].isupper()
            proteted_method = re.search(r'protected\s\w*\s\w*\(', line)
            proteted_method_name_is_upper = None if proteted_method is None else proteted_method.group(
            ).split(" ")[-1][0].isupper()
            if public_method_name_is_upper or private_method_name_is_upper or proteted_method_name_is_upper:
                self._log_error_line(
                    count, self.method_name_defination_initial_should_not_be_capital.__name__, line,
                    recommend='方法名稱不要大寫開頭')


if __name__ == "__main__":
    class TestPage():
        """
        mocking data
        """

        def __init__(self):
            self.type = type(self).__name__
            self.file_path = "abc.java"
            self.controller_name = "A01sr0833Controller"
            # print(self.type)  # debug
            with open(self.file_path, 'r') as f:  # 測試時永遠以 abc.java 當作對象
                self.file_lines = f.readlines()
            self.rules = []
            self.sql_file_path = get_sql_file_path()
            with open(self.sql_file_path, 'r') as f:
                self.sql_file_lines = f.readlines()

        def set_rules(self, rules: list):
            self.rules = rules

        def check_all_rules(self):
            for rule in self.rules:
                rule.do_rule_check()
    page = TestPage()
    with open("log.txt", 'w') as f:
        f.writelines([])
    LegacyDirectoryPathRule(page).set_all_rules_to_check().do_rule_check()
    UnderLineRule(page).set_all_rules_to_check().do_rule_check()
    RequestMethodRule(page).set_all_rules_to_check().do_rule_check()
    IfElseRule(page).set_all_rules_to_check().do_rule_check()
    GenericTypeRule(page).set_all_rules_to_check().do_rule_check()
    MethodNameRule(page).set_all_rules_to_check().do_rule_check()
    CommentRule(page).set_all_rules_to_check().do_rule_check()
    # JavaDocRule(page).do_rule_check()  # 這個要獨立測試
