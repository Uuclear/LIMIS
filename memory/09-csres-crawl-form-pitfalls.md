# 工标网爬取回填标准表单：常见错误与规避

本文记录「从工标网爬取」后**表单只填了名称、其它字段空或错位**，或与 `scripts/csres_fetch_demo.py` 单独运行结果不一致的问题：**成因**与**规避方法**。

---

## 现象

- 点击「从工标网爬取」后，**只有 `name` 等少数字段**有值；**标准号、发布/实施日期、状态、替代关系**等为空或不对。
- 命令行用同一套解析逻辑演示时字段却正常。

---

## 原因（多因素叠加）

### 1. 业务信封未解包：`code` 类型不一致

接口统一返回 `{ code, message, data }`，爬虫结果在 **`data`** 中。

若网关或中间层把 **`code` 序列化为字符串 `"200"`**，而前端拦截器**只把数字 `200` 视为成功**，则**不会解包 `data`**，后续拿到的不是字段对象 → 回填时大量 `undefined`，只剩偶然能对上的键（如部分路径下仍有 `name`）。

**规避**：在 `frontend/src/utils/request.ts` 中，对 `code` **同时兼容数字与纯数字字符串**（如 `"200"`），成功时再返回内部的 `data`。

### 2. 多层 `data` 嵌套

响应可能是 `data` 再包一层 `data`。若直接把整段响应当一层用，`Object.assign` 会写到错误层级。

**规避**：使用 `frontend/src/utils/apiField.ts` 中的 **`unwrapCrawlPayload`**：按层剥开，直到出现 `standard_no` / `standardNo` / `name` 等，再 **`JSON` 序列化反序列化**成普通对象，避免 Proxy / 不可枚举键导致读不到字段。

### 3. 字段命名：snake_case 与 camelCase

后端 DRF 多为 **snake_case**；若某处变成 **camelCase**，只按一种名字读取会丢字段。

**规避**：回填时用 **`apiField(obj, 'standard_no')`** 这类 helper，**同时尝试** snake 与 camel 形式。

### 4. 爬虫与选条逻辑（后端）

搜索结果需优先 **现行、较新年号**；详情页需解析 **发布/实施日期、替代说明** 等；无结构化行时需有 **锚文本 + 年号** 等兜底。若选条或解析偏弱，即使用户拿到完整 `data`，**业务内容也会偏**。

**规避**：

- 解析与 HTTP 集中在 `backend/apps/standards/csres_parse.py`；`csres_crawl.py` 组装与库表关联。
- 联调前用 **`PYTHONPATH=backend` 运行 `scripts/csres_fetch_demo.py`**，与线上一致，再测页面。

---

## 修改清单（防回归）

| 检查项 | 说明 |
|--------|------|
| 信封 | `code` 为数字或 `"200"` 等字符串时，均能解包出 **`data`**。 |
| 结构 | 回填前 **`unwrapCrawlPayload`** 是否剥到含 `standard_no` / `name` 的平面。 |
| 字段 | **`apiField`** 双读 snake / camel。 |
| 后端 | 演示脚本与 **`crawl_standard_metadata`** 是否同源逻辑。 |

---

## 相关代码位置

- 请求解包：`frontend/src/utils/request.ts`
- 剥 `data` 与字段读取：`frontend/src/utils/apiField.ts`
- 表单回填：`frontend/src/views/standards/StandardList.vue`（`handleCrawl`）
- 抓取与解析：`backend/apps/standards/csres_parse.py`、`csres_crawl.py`
- 演示：`scripts/csres_fetch_demo.py`

---

## 附：接口 502 与「后端未启动」（易混淆）

若前端将 `/api` 代理到 `http://127.0.0.1:8000`，而 **本机未启动 Django**，会出现 **502 / 网络错误**，与「信封未解包」不同：先确认 **8000 有进程**、数据库/Redis 与 `dev` 配置一致，再查业务层。
