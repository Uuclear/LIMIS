# Wiki同步说明

本文档说明如何将 `/wiki` 目录的文档同步到 GitHub Wiki。

---

## 方法一：GitHub Actions 自动同步（推荐）

已配置 `.github/workflows/sync-wiki.yml`，当 `limis-ali` 分支的 `wiki/` 目录有更改时，会自动同步到 GitHub Wiki。

### 配置步骤

1. **生成 Personal Access Token (PAT)**
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择以下权限:
     - `repo` - 访问仓库
     - `workflow` - 更新 GitHub Actions 工作流
   - 生成后复制 Token

2. **添加 Secrets 到仓库**
   - 访问: https://github.com/Uuclear/limis/settings/secrets/actions
   - 点击 "New repository secret"
   - Name: `WIKI_TOKEN`
   - Value: 你的 PAT Token
   - 点击 "Add secret"

3. **修改 workflow 使用 WIKI_TOKEN**
   
   编辑 `.github/workflows/sync-wiki.yml`，将:
   ```yaml
   token: ${{ secrets.GITHUB_TOKEN }}
   ```
   
   改为:
   ```yaml
   token: ${{ secrets.WIKI_TOKEN }}
   ```

4. **触发同步**
   - 修改 `wiki/` 目录下的任何文件
   - 推送到 `limis-ali` 分支
   - GitHub Actions 会自动运行并同步到 Wiki

---

## 方法二：手动同步

使用提供的脚本手动同步。

### 使用步骤

1. **生成 Personal Access Token (PAT)**
   - 同上，访问 https://github.com/settings/tokens
   - 生成带有 `repo` 权限的 Token

2. **运行同步脚本**
   ```bash
   cd /opt/limis
   ./sync-wiki-manual.sh <你的GitHub用户名> <你的PAT令牌>
   ```

   示例:
   ```bash
   ./sync-wiki-manual.sh Uuclear ghp_xxxxxxxxxxxx
   ```

---

## Wiki 结构

同步后的 GitHub Wiki 结构:

```
Home.md                          # 首页（来自 README.md）
系统简介.md
快速开始.md
术语定义.md
系统概述/
  ├── 系统简介.md
  ├── 快速开始.md
  └── 术语定义.md
用户指南/
  ├── 角色权限说明.md
  ├── 委托管理.md
  ├── 样品管理.md
  ├── 检测任务.md
  ├── 原始记录.md
  ├── 检测报告.md
  └── 个人中心.md
管理员指南/
  ├── 系统配置.md
  ├── 用户管理.md
  ├── 项目管理.md
  ├── 设备管理.md
  ├── 人员管理.md
  ├── 标准库管理.md
  ├── 模板管理.md
  ├── 质量管理.md
  ├── 耗材管理.md
  ├── 环境监控.md
  └── 审计日志.md
功能详解/
  ├── 状态机流转.md
  ├── 电子签名.md
  ├── 盲样管理.md
  ├── 自动计算.md
  ├── 龄期管理.md
  ├── 设备预警.md
  ├── 实时监控.md
  └── 数据导出.md
API文档/
  ├── API概述.md
  ├── 系统模块API.md
  ├── 业务模块API.md
  └── 支撑模块API.md
扩展开发/
  ├── 开发环境搭建.md
  ├── 后端开发指南.md
  ├── 前端开发指南.md
  ├── 新增检测类型.md
  └── 自定义报表.md
常见问题/
  ├── 常见问题FAQ.md
  ├── 已知问题.md
  └── Bug预计与排查.md
```

---

## 注意事项

1. **文件名处理**: 同步时会自动移除文件名中的序号前缀（如 `01-`、`02-`），使 URL 更友好

2. **目录结构**: GitHub Wiki 不支持真正的目录结构，但支持使用 `/` 的页面名称来模拟目录

3. **首页**: `README.md` 会被复制为 `Home.md`，作为 Wiki 首页

4. **链接**: 文档中的相对链接在同步后可能需要调整

5. **图片**: GitHub Wiki 不支持直接上传图片，建议使用外部图床或 GitHub 仓库的 raw 链接

---

## 访问 Wiki

同步完成后，访问:
- **Wiki 首页**: https://github.com/Uuclear/limis/wiki
- **Home 页面**: https://github.com/Uuclear/limis/wiki/Home

---

## 故障排查

### GitHub Actions 失败

1. 检查 Secrets 是否正确配置
2. 检查 Token 是否有 `repo` 权限
3. 查看 Actions 日志: https://github.com/Uuclear/limis/actions

### 手动同步失败

1. 检查用户名和 Token 是否正确
2. 检查网络连接
3. 检查是否有仓库写入权限

---

## 参考文档

- [GitHub Wiki 文档](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Personal Access Token 文档](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)