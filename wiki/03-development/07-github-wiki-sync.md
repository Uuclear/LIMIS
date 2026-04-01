# GitHub Wiki 同步（仓库 `wiki/` → `.wiki.git`）

主仓库中的 **`wiki/`** 目录为知识库正文来源；通过 **GitHub Actions** 在推送到 `main` 且变更涉及 `wiki/**` 时，自动推送到 **GitHub Wiki** 对应的 Git 仓库（`https://github.com/<owner>/<repo>.wiki.git`）。

---

## 工作流位置

- 工作流文件（主仓库）：[`wiki-sync.yml`](https://github.com/Uuclear/limis/blob/main/.github/workflows/wiki-sync.yml)
- 触发条件：
  - 向 **`main`** 分支推送，且变更路径包含 `wiki/**` 或该工作流文件本身
  - 手动运行：**Actions → Sync Wiki → Run workflow**

---

## 所需权限与密钥

GitHub Wiki 与普通仓库分离，推送需有 **写权限** 的凭据。

| 方式 | 说明 |
|------|------|
| **`WIKI_SYNC_TOKEN`（推荐）** | 在仓库 **Settings → Secrets and variables → Actions** 中新建 Secret，值为 **Personal Access Token（classic）**，勾选 **`repo`** 全选或至少能推送 Wiki。 |
| **`GITHUB_TOKEN`（备选）** | 若未配置 `WIKI_SYNC_TOKEN`，工作流会回退使用内置 `GITHUB_TOKEN`。部分组织/仓库策略下可能对 Wiki **无写权限**，此时推送会失败，**请改用 PAT**。 |

失败时请在 Actions 日志中查看 `git push` 错误；常见为 403，需配置 PAT。

---

## 本地与 Wiki 目录约定

- 主仓库 **`wiki/`** 下保持 **相对路径与交叉链接**（如 `[首页](../README.md)`），与 Wiki 网页侧路径一致。
- **`Home.md`** 为 GitHub Wiki **默认首页**；完整索引仍以 **`README.md`** 为主干（见 [知识库首页](../README.md)）。

---

## 变更记录

| 日期 | 版本 | 作者 | 摘要 |
|------|------|------|------|
| 2026-04-01 | 1.0 | Wiki | 初版：说明 CI、密钥与 Home/README 分工 |

返回：[Wiki 首页](../README.md)
