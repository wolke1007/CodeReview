from utils import *
from typing import Callable
from enum import Enum
import re
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class Rule():
    def __init__(self, page):
        self.type = type(self).__name__
        print(self.type)  # debug
        self.assert_logics = []
        self.page = page
        # 需要印出來的 log 全部 append 在這個 list 裡面並在 do_rule_check 最後一次一起印
        self.error_logs = ["=== {name} {time}=== \n".format(
            name=self.page.file_path,
            time=time.strftime("%Y-%m-%d %X", time.localtime()))]
        self.log_path = "./log.txt"
        self.log_template = ("file: {} line: {} violate rule: \"{}\"\n"
                             "code: >>>{}\n")

    def do_rule_check(self):
        self.__check_with_assert_rule()
        # collect all error messages, then log into file
        self._log_error_line_()

    def set_assert_rule(self, assert_rule: Callable):
        self.assert_logics.append(assert_rule)

    def __check_with_assert_rule(self):
        for assert_logic in self.assert_logics:
            assert_logic()

    def _log_error_line_(self):
        with open(self.log_path, 'a') as file:
            file.writelines(self.error_logs)

    def log_error_line(self, count: int, function_name: str, line: str):
        self.error_logs.append(
            self.log_template.format(
                self.page.file_path,
                count + 1,
                function_name,
                line
            ))

    def log_error_message(self, function_name: str, message: str):
        self.error_logs.append(
            self.log_template.format(
                self.page.file_path,
                "None",
                function_name,
                message
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
        self.set_assert_rule(self.java_doc_should_exist)

    def java_doc_should_exist(self):
        '''
        檢查 JavaDoc 註解是否有寫
        '''
        end_of_comment = False
        for count, line in enumerate(self.page.file_lines, start=0):
            if "import" in line or "package" in line:
                continue
            if "*/" in line:
                end_of_comment = True
            if ";" in line and not end_of_comment:
                self.log_error_line(
                    count, self.java_doc_should_exist.__name__, line)
                end_of_comment = False
                continue
            if ";" in line and end_of_comment:
                end_of_comment = False


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
        self.set_assert_rule(self.code_comment_should_not_exist)

    def code_comment_should_not_exist(self):
        '''
        邏輯註解不該留下
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
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
                    chinese_in_line = True  # 有註解，且有中文，判斷為說明邏輯
            if not chinese_in_line:
                self.log_error_line(
                    count, self.code_comment_should_not_exist.__name__, line)

# # 風格


class IfElseRule(Rule):
    """
    - 不要有單行if, for statment
    """

    def __init__(self, page):
        super().__init__(page)
        self.set_assert_rule(self.if_statement_should_with_bracket_mark)

    def if_statement_should_with_bracket_mark(self):
        '''
        搜尋 if 關鍵字，檢查是否同時有 { 跟在後面
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            if ("\tif (" in line or
                " if (" in line or
                "\tif(" in line or
                    " if(" in line) and "{" not in line:
                self.log_error_line(
                    count, self.if_statement_should_with_bracket_mark.__name__, line)


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
        self.set_assert_rule(self.controller_name_should_same_as_do_query_naming)

    def controller_name_should_same_as_do_query_naming(self):
        '''
        用 controller 的檔名去尋找是否存在於 phase-1-data.sql 中
        如果不存在則有兩種可能:
            1. controller 的命名與 update sql 中不一致
            例如: 
                Controller: A010203
                SQL: a0102_03
            2. 撰寫者沒有更新 update sql 導致搜尋不到
        '''
        controller_name = self.page.controller_name[:-10].lower()
        for line in self.page.sql_file_lines:
            if controller_name in line:
                return
            if "_" in controller_name:
                continue  # 如果原來就已經有底線就不用猜測了，如果找完整個檔案都沒有就是沒有
            # 在所有位置加上底線試試看，如果有則回報答案
            for index in range(1, len(controller_name)):
                tmp_list = list(controller_name)
                tmp_list.insert(index, "_")
                controller_name_with_underline = "".join(tmp_list)
                if controller_name_with_underline in line:
                    self.log_error_message(
                        function_name=self.controller_name_should_same_as_do_naming.__name__,
                        message="controller 的命名應為: " + controller_name_with_underline + " 目前叫做: " + controller_name)
                    return
        self.log_error_message(
            function_name=self.controller_name_should_same_as_do_naming.__name__,
            message="controller 的命名: " + controller_name + " 於 update sql 中不存在，請確認 commit 是否有更新此檔案")


# class LegacyDirectoryPathRule(Rule):
#     """
#     - 遷移到 legacy 內的原系統程式碼，應以新系統內之legacy為根目錄之後按照原系統的 package 來擺放
#     - 例如新系統的 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy`
#     - 裡面要放置原系統內的 `/src/com/taifex/r2/web/m03`
#     - 遷移後的路徑會是 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy/src/com/taifex/r2/web/m03`
#     """

    # def __init__(self, page):
    #     super().__init__(page)
    #     self.set_assert_rule(self.todo)

    # def todo(self):
    #     '''
    #     todo
    #     '''
    #     for count, line in enumerate(self.page.file_lines, start=0):
    #         self.log_error_line(
    #             count, self.todo.__name__, line)

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
        self.set_assert_rule(self.should_not_allow_both_get_and_post_method)

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
                    self.log_error_line(
                        count, self.should_not_allow_both_get_and_post_method.__name__, line)
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
        self.set_assert_rule(self.method_should_add_override_annotation)
        self.set_assert_rule(self.method_should_add_transaction_annotation)

    def method_should_add_override_annotation(self):
        '''
        檢查每個方法在定義時前面一行要有 @Override
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            self.log_error_line(
                count, self.todo.__name__, line)

    def method_should_add_transaction_annotation(self):
        '''
        update insert delete 該要有 @Transaction
        檢查每個方法在定義時前一行或前兩行要有 @Transaction
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            self.log_error_line(
                count, self.todo.__name__, line)


class GenericTypeRule(Rule):
    """
    - List 的型別要指定 不要是沒指定或? `List<?>`
    """

    def __init__(self, page):
        super().__init__(page)
        self.set_assert_rule(self.should_not_using_generic_type_in_return)

    def should_not_using_generic_type(self):
        '''
        搜尋所有 <xxxx> 的 pattern 檢查是否有 ? 在裡面
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            angle_bracket = re.search(r'<.*>', line)
            if angle_bracket is not None and "?" in angle_bracket.group():
                self.log_error_line(
                    count, self.should_not_using_generic_type.__name__, line)


class MethodNameRule(Rule):
    """
    - 方法名稱不要大寫開頭
    """

    def __init__(self, page):
        super().__init__(page)
        self.set_assert_rule(self.method_name_initial_should_not_be_capital)
        self.set_assert_rule(
            self.method_name_defination_initial_should_not_be_capital)

    def method_name_initial_should_not_be_capital(self):
        '''
        搜尋所有 xxx.xxx 的 pattern 並把 . 後面的部分當作 method name 做檢查
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            method_name = re.search(r'\w\.\w', line)
            if method_name is not None and method_name.group()[-1].isupper():
                self.log_error_line(
                    count, self.method_name_initial_should_not_be_capital.__name__, line)

    def method_name_defination_initial_should_not_be_capital(self):
        '''
        搜尋所有定義方法的命名部分 {blank}method_name( 用這樣的 pattern 下去找
        '''
        for count, line in enumerate(self.page.file_lines, start=0):
            if re.search(r'\w\.\w', line):
                continue  # 表示是 method_name_initial_should_not_be_capital 的情況，跳過
            if " new " in line:
                continue  # return new ModelAndView(INDEX_VIEW) 的情況
            method_name = re.search(r'\s\w*\(', line)
            if method_name is not None and method_name.group()[1].isupper():
                self.log_error_line(
                    count, self.method_name_defination_initial_should_not_be_capital.__name__, line)


if __name__ == "__main__":
    class TestPage():
        """
        mocking data
        """

        def __init__(self):
            self.type = type(self).__name__
            self.file_path = "abc.txt"
            self.controller_name = "M022388Controller"
            print(self.type)  # debug
            with open(self.file_path, 'r') as f:  # 測試時永遠以 abc.txt 當作對象
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
    UnderLineRule(page).do_rule_check()
    # RequestMethodRule(page).do_rule_check()
    # IfElseRule(page).do_rule_check()
    # GenericTypeRule(page).do_rule_check()
    # MethodNameRule(page).do_rule_check()
    # JavaDocRule(page).do_rule_check()
    # CommentRule(page).do_rule_check()
