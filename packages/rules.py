from typing import Callable
from enum import Enum


class Rule():
    def __init__(self, page):
        self.type = type(self).__name__
        print(self.type)  # debug
        self.assert_logics = []
        self.page = page
        # 需要印出來的 log 全部 append 在這個 list 裡面並在 do_rule_check 最後一次一起印
        self.error_logs = ["=== {name} === \n".format(
            name=self.page.file_path)]
        self.log_path = "./log.txt"
        self.log_template = "file: {} line:, {} violate rule: \"{}\"\n"

    def do_rule_check(self):
        self.__check_with_assert_rule()
        # collect all error messages, then log into file
        self.log_error_line()

    def set_assert_rule(self, assert_rule: Callable):
        self.assert_logics.append(assert_rule)

    def __check_with_assert_rule(self):
        for assert_logic in self.assert_logics:
            assert_logic()

    def log_error_line(self):
        with open(self.log_path, 'a') as file:
            file.writelines(self.error_logs)


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

    def _log_error_line_(self, count: int, function_name: str):
        self.error_logs.append(
            self.log_template.format(
                self.page.file_path,
                count + 1,
                function_name
            ))

    def java_doc_should_exist(self):
        '''
        檢查 JavaDoc 註解是否有寫
        '''
        end_of_comment = False
        for count, line in enumerate(self.page.file_lines, start=0):
            if "*/" in line:
                end_of_comment = True
            if ";" in line and not end_of_comment:
                self._log_error_line_(count, self.java_doc_should_exist.__name__)
                end_of_comment = False
                continue
            if ";" in line and end_of_comment:
                end_of_comment = False


# class CommentRule(Rule):
#     """
#     - 方法內的註解分為2種
#         - 說明註解: 用來說明使用
#         - 邏輯註解: 程式邏輯
#     - 說明註解留下
#     - 邏輯註解移除
#     """

#     def check(self):
#         print(self.type)

# # 風格


# class IfElseRule(Rule):
#     """
#     - 不要有單行if, for statment
#     """

#     def check(self):
#         print(self.type)


# class UnderLineRule(Rule):
#     """
#     - 保留原專案之下底線
#     - 假設原系統的功能連結為 `a01sr08_13.do`
#     - sql應為 `UPDATE SMS.dbo.MENULINK SET NEW_LINK = '/a01sr08_13/index' , USE_NEW_LINK = 'Y' WHERE Link = 'a01sr08_13.do?method=query';`
#     - Controller Name 應為 A01sr08_13Controller
#     - Controller 之 RequestMapping 應為 `@RequestMapping("/a01sr08_13")`
#     - 收納該功能 jsp 及 js 檔案的資料夾應為 `a01sr08_13`
#     """

#     def check(self):
#         print(self.type)


# class LegacyDirectoryPathRule(Rule):
#     """
#     - 遷移到 legacy 內的原系統程式碼，應以新系統內之legacy為根目錄之後按照原系統的 package 來擺放
#     - 例如新系統的 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy`
#     - 裡面要放置原系統內的 `/src/com/taifex/r2/web/m03`
#     - 遷移後的路徑會是 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy/src/com/taifex/r2/web/m03`
#     """

#     def check(self):
#         print(self.type)

# # 程式碼


# class RequestMethodRule(Rule):
#     """
#     - Controller內的進入點，接受的Get Post 要把關，不要同時接受 Get 及 Post 的，如果有要問開發者否有必要
#     - 原則上是進度功能首頁會是走Get，其他行為都用Post

#     // 推薦的寫法，GET POST 他只能設定一種方式
#     @GetMapping(value = "/index/doQuery")
#     或
#     @PostMapping(value = "/index/doQuery")
#     public ModelAndView doQuery(HttpServletRequest request, HttpServletResponse response, HttpSession session,
#             RedirectAttributes redirectAttrs) {

#     // 另外這個寫法可以使用
#     // 只是不要是GET POST都支援的作法
#     @RequestMapping(value = "/index/doQuery", method = { RequestMethod.GET, RequestMethod.POST })
#     public ModelAndView toQuery(HttpServletRequest request, HttpServletResponse response, HttpSession session) {
#     """

#     def check(self):
#         print(self.type)


# class ServiceImplAnnotationRule(Rule):
#     """
#     - ServiceImpl內的方法，從介面實作的請都記得標上 `@Override`
#     - 要是裡面的方法是 insert update delete 需要加上 @Transactional
#     @Transactional
#         @Override
#         public int deleteA01ar(String userId) {
#                 return a01arDao.deleteA01ar(userId);
#         }
#     """

#     def check(self):
#         print(self.type)


# class GenericTypeRule(Rule):
#     """
#     - List 的型別要指定 不要是沒指定或? `List<?>`
#     """

#     def check(self):
#         print(self.type)


# class MethodNameRule(Rule):
#     """
#     - 方法名稱不要大寫開頭
#     """

#     def check(self):
#         print(self.type)
