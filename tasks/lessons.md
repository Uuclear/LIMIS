# Lessons Learned

- 模型重构（`TestMethod` -> `TestParameter`）后，管理命令与清理脚本必须同步升级，否则会在环境准备阶段失效。
- `--clear` 路径属于高风险回归点，应纳入最小自动化回归（至少一次完整 seed + 核心 API 冒烟）。
