from typing import overload

# 註解
class JavaDocRule():
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
    def check():
        pass

class CommentRule():
    """
    - 方法內的註解分為2種
        - 說明註解: 用來說明使用
        - 邏輯註解: 程式邏輯
    - 說明註解留下
    - 邏輯註解移除
    """
    def __init__(self):
        pass

# 風格
class IfElseRule():
    """
    - 不要有單行if, for statment
    """
    def __init__(self):
        pass

class UnderLineRule():
    """
    - 保留原專案之下底線
    - 假設原系統的功能連結為 `a01sr08_13.do`
    - sql應為 `UPDATE SMS.dbo.MENULINK SET NEW_LINK = '/a01sr08_13/index' , USE_NEW_LINK = 'Y' WHERE Link = 'a01sr08_13.do?method=query';`
    - Controller Name 應為 A01sr08_13Controller
    - Controller 之 RequestMapping 應為 `@RequestMapping("/a01sr08_13")`
    - 收納該功能 jsp 及 js 檔案的資料夾應為 `a01sr08_13`
    """
    def __init__(self):
        pass

class LegacyDirectoryPathRule():
    """
    - 遷移到 legacy 內的原系統程式碼，應以新系統內之legacy為根目錄之後按照原系統的 package 來擺放
    - 例如新系統的 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy`
    - 裡面要放置原系統內的 `/src/com/taifex/r2/web/m03`
    - 遷移後的路徑會是 `/FCM/src/main/java/com/mitake/infra/repository/app/service/legacy/src/com/taifex/r2/web/m03`
    """
    def __init__(self):
        pass

#程式碼
class RequestMethodRule():
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
    def __init__(self):
        pass

class ServiceImplAnnotationRule():
    """
    - ServiceImpl內的方法，從介面實作的請都記得標上 `@Override`
    - 要是裡面的方法是 insert update delete 需要加上 @Transactional
    @Transactional
	@Override
	public int deleteA01ar(String userId) {
		return a01arDao.deleteA01ar(userId);
	}
    """
    def __init__(self):
        pass

class GenericTypeRule():
    """
    - List 的型別要指定 不要是沒指定或? `List<?>`
    """
    def __init__(self):
        pass

class MethodNameRule():
    """
    - 方法名稱不要大寫開頭
    """
    def __init__(self):
        pass
