from typing import Callable

class Rule():
    def __init__(self, file_path: str, assert_logic: Callable[[str], bool]):
        self.type = type(self).__name__
        print(self.type)  # debug
        self.assert_logic = assert_logic
        self.file = file_path
        self.error_logs = ["=== {name} === \n".format(name=file_path)]
        self.log_path = "./log.txt"

    def run(self):
        self.__check_with_assert_rule()
        # collect all error messages, then log into file
        self.__log_error_line()

    def __check_with_assert_rule(self):
        with open(self.file, 'r') as f:
            lines = f.readlines()
        line_count = 1
        for line in lines:
            exam_pass = self.assert_logic(line)
            if (not exam_pass):
                error_msg = "Fail because violate rule:{rule_name}, line: {position} \n".format(
                    rule_name=self.type,
                    position=str(line_count)
                )
                print(error_msg) # debug
                self.error_logs.append(error_msg)
            line_count += 1

    def __log_error_line(self):
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
    def __init__(self, file_path):
        super().__init__(file_path, self.assert_logic)

    def assert_logic(self, line):
        if ("a" in line): # debug
            return False
        return True


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
