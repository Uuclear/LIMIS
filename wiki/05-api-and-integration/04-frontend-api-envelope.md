# 前端请求信封与字段兼容

## 统一响应

接口常返回 `{ code, message, data }`。成功时 `code` 应为 **200**（数字或字符串需兼容）。

## 解包与嵌套 data

避免 `data.data` 未展开；使用 `unwrapCrawlPayload` 等工具剥到含业务字段的平面对象。

## snake_case / camelCase

`apiField` 等辅助应 **同时读取** `standard_no` 与 `standardNo`，避免回填丢失。

工作区规则与爬虫对齐：见 [标准爬取](../08-security-compliance/04-standards-crawl-metadata.md)。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
