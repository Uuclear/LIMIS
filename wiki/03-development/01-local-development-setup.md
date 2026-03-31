# 本地开发环境搭建

## 后端

1. Python 虚拟环境：`python -m venv .venv && source .venv/bin/activate`
2. 安装依赖：`pip install -r backend/requirements.txt`（路径以仓库为准）
3. 配置环境变量与 `DATABASES`（可用 SQLite 做快速试验）
4. `python manage.py migrate && python manage.py runserver`

## 前端

1. `cd frontend && npm install`（或 `pnpm`）
2. 配置 API 基地址（`.env.development`）
3. `npm run dev`

## 调试爬虫/元数据

后端脚本常需 `PYTHONPATH=backend` 与仓库内演示脚本一致（见 [标准爬取](../08-security-compliance/04-standards-crawl-metadata.md)）。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版 |

返回：[Wiki 首页](../README.md)
