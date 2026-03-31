# 标准工标网爬取与字段对齐

本文说明 **从工标网拉取标准元数据** 的后端链路、前端回填注意点，以及与 `.cursor/rules` 中已记录问题的对应关系。

## 1. 功能目标

在「标准规范」维护表单中，按标准号从 **csres.com** 拉取元数据，自动填充标准名称、日期、状态等，减少手工录入。

## 2. 后端链路

| 环节 | 文件 | 说明 |
|------|------|------|
| API 入口 | `backend/apps/standards/views.py` | `StandardViewSet` → `@action` `crawl`，`POST .../crawl/` |
| 编排 | `backend/apps/standards/csres_crawl.py` | `crawl_standard_metadata` |
| 解析 | `backend/apps/standards/csres_parse.py` | `fetch_csres_metadata`（无 Django 依赖，可与脚本共用） |
| 演示脚本 | `scripts/csres_fetch_demo.py` | 单独调试抓取结果应与线上一致 |

**权限**：`lims_action_map` 将 `crawl` 映射为 **`view`**，避免仅有 view/edit 的业务角色无法调用（见 `views.py` 注释）。

**路由前缀**：`/api/v1/standards/`（`backend/limis/urls.py`）；爬取动作为 **`POST .../crawl/`**（`detail=False`）。

## 3. 前端链路

| 环节 | 文件 |
|------|------|
| HTTP 信封 | `frontend/src/utils/request.ts` | 成功时解包 `data`；**兼容 `code` 为数字或字符串 `"200"`** |
| 载荷剥层 | `frontend/src/utils/apiField.ts` | `unwrapCrawlPayload`：处理嵌套 `data`，并 **snake_case / camelCase 双读** |
| 表单 | `frontend/src/views/standards/StandardList.vue`（及关联表单组件） | 「从工标网爬取」按钮逻辑 |

## 4. 字段对齐要点

1. **信封**：接口统一 `{ code, message, data }`；网关若把 `code` 变为字符串，旧逻辑会解包失败 → 仅部分字段偶发有值。
2. **嵌套**：响应可能是 `data.data` 多层，需要 `unwrapCrawlPayload` 剥到含 `standard_no` / `name` 的平面对象。
3. **命名**：后端 DRF 多为 **snake_case**；序列化若出现 camelCase，需 `apiField` 同时读取两种键名。

## 5. 文字流程：爬取与回填

```
用户输入标准号 → 点击爬取
    ↓
POST /api/v1/standards/crawl/
    （路由注册见 backend/apps/standards/urls.py：`router.register('', StandardViewSet)`，避免 /standards/standards/ 重复）
    ↓
crawl_standard_metadata → fetch_csres_metadata
    ↓
返回业务字段对象
    ↓
request 解包 → unwrapCrawlPayload → 合并到表单 model
```

## 6. 风险与回滚

| 风险 | 说明 |
|------|------|
| 外部站点结构变更 | `csres_parse.py` 需同步更新；可用 demo 脚本回归 |
| 频率过高被封 IP | 服务端限流、缓存或人工触发 |
| 解析兜底错误 | 规则中已说明「现行、较新年号」等策略，见解析模块注释 |

**回滚**：前端/后端字段映射回退到上一 Git 版本；数据层一般不写库（crawl 多为 **不落库只回填**，以 `views.py` 说明为准）。

## 7. 调试建议

```bash
cd /opt/limis
PYTHONPATH=backend python scripts/csres_fetch_demo.py
```

（参数以脚本内 `argparse` 为准。）

## 8. 相关路径

- `backend/apps/standards/views.py`
- `backend/apps/standards/csres_crawl.py`
- `backend/apps/standards/csres_parse.py`
- `scripts/csres_fetch_demo.py`
- `frontend/src/utils/request.ts`
- `frontend/src/utils/apiField.ts`
