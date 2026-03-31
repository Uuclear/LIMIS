# Bug预计与排查

本文档详细介绍系统潜在问题的排查方法，帮助用户和技术人员快速定位和解决问题。

---

## 一、并发操作冲突

### 1.1 编号生成冲突

**问题描述**：
在高并发场景下，多个用户同时创建数据时，可能出现编号重复或编号不连续的问题。

**潜在风险场景**：
- 多人同时创建委托单
- 多人同时登记样品
- 批量导入数据时生成编号

**排查方法**：

1. **检查编号重复**
   ```sql
   -- 查询重复编号
   SELECT commission_no, COUNT(*) as cnt 
   FROM commissions 
   GROUP BY commission_no 
   HAVING COUNT(*) > 1;
   ```

2. **检查编号连续性**
   ```sql
   -- 查询编号缺口
   SELECT a.id + 1 as missing_start, 
          MIN(b.id) - 1 as missing_end
   FROM commissions a 
   LEFT JOIN commissions b ON a.id + 1 = b.id
   WHERE b.id IS NULL AND a.id < (SELECT MAX(id) FROM commissions);
   ```

3. **检查编号生成日志**
   - 路径：系统管理 → 系统日志 → 编号日志
   - 查看编号生成时间和请求来源

**解决方案**：

| 方案 | 说明 | 适用场景 |
|------|------|----------|
| 数据库唯一约束 | 数据库层防止重复 | 所有场景 |
| 分布式锁 | 使用Redis锁控制并发 | 高并发场景 |
| 预生成编号池 | 提前生成编号供使用 | 批量导入场景 |
| 重试机制 | 编号冲突时自动重试 | 所有场景 |

**临时处理**：
```sql
-- 修正重复编号
UPDATE commissions 
SET commission_no = CONCAT('WT', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(id, 4, '0'))
WHERE id IN (重复编号的记录ID);
```

---

### 1.2 库存扣减冲突

**问题描述**：
在耗材出库、样品处置等场景下，并发操作可能导致库存数据不一致。

**潜在风险场景**：
- 多人同时领用同一耗材
- 样品处置与流转同时进行
- 批量操作时库存计算错误

**排查方法**：

1. **检查库存一致性**
   ```sql
   -- 检查库存是否为负数
   SELECT * FROM consumables WHERE stock < 0;
   
   -- 检查库存与流水是否一致
   SELECT c.id, c.name, c.stock, 
          COALESCE(SUM(CASE WHEN io.type = 'in' THEN io.quantity ELSE -io.quantity END), 0) as calculated_stock
   FROM consumables c
   LEFT JOIN inventory_orders io ON c.id = io.consumable_id
   GROUP BY c.id, c.name, c.stock
   HAVING c.stock != calculated_stock;
   ```

2. **检查出入库记录**
   - 查看同一时间段的出入库记录
   - 检查是否有重复记录
   - 核对操作时间和操作人

3. **检查操作日志**
   - 路径：系统管理 → 操作日志
   - 筛选相关操作记录
   - 查看并发操作情况

**解决方案**：

| 方案 | 说明 |
|------|------|
| 乐观锁 | 使用版本号控制并发 |
| 悲观锁 | 操作时锁定记录 |
| 队列处理 | 异步处理库存变更 |
| 事务控制 | 使用数据库事务保证一致性 |

**临时处理**：
```sql
-- 根据出入库记录重新计算库存
UPDATE consumables c
SET stock = (
    SELECT COALESCE(SUM(CASE WHEN io.type = 'in' THEN io.quantity ELSE -io.quantity END), 0)
    FROM inventory_orders io
    WHERE io.consumable_id = c.id
);
```

---

### 1.3 状态同步冲突

**问题描述**：
多人同时操作同一数据时，状态可能不一致。

**潜在风险场景**：
- 审批流程中多人同时审批
- 样品流转时状态更新
- 报告签发时状态变更

**排查方法**：

1. **检查状态变更日志**
   ```sql
   -- 查看状态变更历史
   SELECT * FROM status_logs 
   WHERE object_type = 'commission' AND object_id = ?
   ORDER BY created_at DESC;
   ```

2. **检查并发操作**
   - 查看同一时间段的操作记录
   - 分析操作顺序和结果

3. **验证当前状态**
   - 对比数据表状态和日志记录
   - 检查是否有遗漏的状态变更

**解决方案**：

| 方案 | 说明 |
|------|------|
| 状态机控制 | 严格的状态流转规则 |
| 操作锁 | 编辑时锁定数据 |
| 版本控制 | 使用版本号检测冲突 |
| 流程控制 | 审批流程互斥 |

---

## 二、数据一致性

### 2.1 级联删除问题

**问题描述**：
删除主数据时，关联数据可能未正确处理，导致数据不一致。

**潜在风险场景**：
- 删除委托单时样品未删除
- 删除样品时检测任务未处理
- 删除检测项目时原始记录未处理

**排查方法**：

1. **检查孤立数据**
   ```sql
   -- 检查没有委托的样品
   SELECT s.* FROM samples s
   LEFT JOIN commissions c ON s.commission_id = c.id
   WHERE c.id IS NULL;
   
   -- 检查没有样品的检测任务
   SELECT t.* FROM test_tasks t
   LEFT JOIN samples s ON t.sample_id = s.id
   WHERE s.id IS NULL;
   ```

2. **检查外键约束**
   ```sql
   -- 查看外键约束
   SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
   FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
   WHERE REFERENCED_TABLE_SCHEMA = 'limis';
   ```

3. **检查删除日志**
   - 查看删除操作记录
   - 确认是否有关联数据

**解决方案**：

| 方案 | 说明 |
|------|------|
| 软删除 | 使用deleted_at字段标记删除 |
| 级联删除 | 数据库设置ON DELETE CASCADE |
| 业务删除 | 代码中处理关联数据 |
| 删除检查 | 删除前检查关联数据 |

**临时处理**：
```sql
-- 清理孤立数据（谨慎操作）
DELETE FROM samples WHERE commission_id NOT IN (SELECT id FROM commissions);
```

---

### 2.2 数据同步问题

**问题描述**：
多个数据表之间的数据可能不同步。

**潜在风险场景**：
- 样品数量与委托不一致
- 检测结果与原始记录不一致
- 报告数据与检测数据不一致

**排查方法**：

1. **数据对比检查**
   ```sql
   -- 检查委托样品数量
   SELECT c.id, c.commission_no, c.sample_count,
          (SELECT COUNT(*) FROM samples WHERE commission_id = c.id) as actual_count
   FROM commissions c
   WHERE c.sample_count != (SELECT COUNT(*) FROM samples WHERE commission_id = c.id);
   
   -- 检查报告检测结果
   SELECT r.id, r.report_no,
          (SELECT COUNT(*) FROM test_results WHERE report_id = r.id) as result_count,
          (SELECT COUNT(*) FROM report_items WHERE report_id = r.id) as item_count
   FROM reports r
   WHERE (SELECT COUNT(*) FROM test_results WHERE report_id = r.id) != 
         (SELECT COUNT(*) FROM report_items WHERE report_id = r.id);
   ```

2. **检查同步任务**
   - 查看定时任务执行日志
   - 检查同步任务是否有错误

3. **检查数据变更日志**
   - 查看数据变更记录
   - 分析变更顺序

**解决方案**：

| 方案 | 说明 |
|------|------|
| 事务控制 | 使用数据库事务保证一致性 |
| 触发器 | 数据变更时自动同步 |
| 定时校验 | 定时检查并修复不一致 |
| 事件驱动 | 数据变更时发送事件通知 |

---

### 2.3 数据完整性问题

**问题描述**：
数据可能存在缺失、重复或格式错误。

**排查方法**：

1. **检查必填字段**
   ```sql
   -- 检查必填字段是否为空
   SELECT * FROM commissions WHERE client_name IS NULL OR client_name = '';
   SELECT * FROM samples WHERE sample_name IS NULL OR sample_name = '';
   ```

2. **检查数据格式**
   ```sql
   -- 检查日期格式
   SELECT * FROM commissions WHERE created_at > NOW();
   
   -- 检查数值范围
   SELECT * FROM test_results WHERE value < 0;
   ```

3. **检查重复数据**
   ```sql
   -- 检查重复记录
   SELECT commission_no, COUNT(*) FROM commissions GROUP BY commission_no HAVING COUNT(*) > 1;
   ```

**解决方案**：

| 方案 | 说明 |
|------|------|
| 数据库约束 | NOT NULL、UNIQUE、CHECK约束 |
| 应用验证 | 代码层验证数据完整性 |
| 定期检查 | 定时任务检查数据完整性 |
| 数据修复 | 发现问题及时修复 |

---

## 三、权限边界

### 3.1 越权访问

**问题描述**：
用户可能通过某种方式访问到不应该访问的数据或功能。

**潜在风险场景**：
- 直接通过URL访问无权限的页面
- 通过API访问其他用户的数据
- 修改请求参数访问其他数据

**排查方法**：

1. **检查访问日志**
   ```sql
   -- 查看用户访问记录
   SELECT * FROM access_logs 
   WHERE user_id = ? AND resource LIKE '%敏感资源%'
   ORDER BY created_at DESC;
   ```

2. **权限测试**
   - 使用低权限账号测试高权限功能
   - 尝试直接访问URL
   - 尝试修改请求参数

3. **代码审计**
   - 检查API是否有权限验证
   - 检查数据查询是否过滤用户权限
   - 检查是否有硬编码的权限判断

**解决方案**：

| 方案 | 说明 |
|------|------|
| RBAC权限控制 | 基于角色的访问控制 |
| 数据权限过滤 | 查询时自动过滤权限范围 |
| API权限验证 | 每个API都验证权限 |
| 前端权限控制 | 按钮级权限控制 |

**安全检查清单**：

- [ ] 所有API都有权限验证
- [ ] 数据查询都有用户过滤
- [ ] 敏感操作都有审计日志
- [ ] 前端按钮都有权限控制
- [ ] URL访问都有权限检查

---

### 3.2 数据泄露

**问题描述**：
敏感数据可能被未授权的用户查看或导出。

**潜在风险场景**：
- 列表查询返回了不该返回的数据
- 导出功能导出了敏感数据
- 日志中记录了敏感信息

**排查方法**：

1. **检查数据权限**
   ```sql
   -- 检查用户数据权限配置
   SELECT u.username, r.name as role, p.resource, p.action
   FROM users u
   JOIN user_roles ur ON u.id = ur.user_id
   JOIN roles r ON ur.role_id = r.id
   JOIN role_permissions rp ON r.id = rp.role_id
   JOIN permissions p ON rp.permission_id = p.id
   WHERE u.id = ?;
   ```

2. **检查查询结果**
   - 使用不同角色账号测试
   - 检查返回的数据范围
   - 验证数据过滤是否正确

3. **检查日志脱敏**
   - 查看日志是否包含敏感信息
   - 检查密码、身份证等是否脱敏

**解决方案**：

| 方案 | 说明 |
|------|------|
| 数据脱敏 | 敏感字段显示时脱敏 |
| 权限过滤 | 查询时自动过滤权限 |
| 日志脱敏 | 日志中不记录敏感信息 |
| 导出控制 | 导出时检查权限 |

**敏感数据清单**：

| 数据类型 | 字段 | 脱敏规则 |
|----------|------|----------|
| 手机号 | mobile | 138****1234 |
| 身份证 | id_card | 310***********1234 |
| 银行卡 | bank_card | 6222****1234 |
| 密码 | password | 不显示 |
| 地址 | address | 部分隐藏 |

---

### 3.3 操作审计

**问题描述**：
需要追踪用户的操作行为，发现异常操作。

**排查方法**：

1. **查看操作日志**
   - 路径：系统管理 → 审计日志
   - 可按用户、时间、操作类型筛选

2. **分析异常操作**
   ```sql
   -- 查看异常登录
   SELECT * FROM login_logs 
   WHERE status = 'failed' AND created_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
   ORDER BY created_at DESC;
   
   -- 查看批量操作
   SELECT user_id, operation, COUNT(*) as cnt
   FROM operation_logs
   WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
   GROUP BY user_id, operation
   HAVING cnt > 50;
   ```

3. **检查敏感操作**
   - 查看删除操作记录
   - 查看权限变更记录
   - 查看数据导出记录

**审计日志内容**：

| 字段 | 说明 |
|------|------|
| 操作时间 | 操作发生的时间 |
| 操作人 | 执行操作的用户 |
| 操作类型 | 新增/修改/删除/查看 |
| 操作对象 | 操作的数据对象 |
| 操作详情 | 具体操作内容 |
| IP地址 | 操作来源IP |
| 浏览器 | 使用的浏览器 |

---

## 四、性能瓶颈

### 4.1 大数据查询性能

**问题描述**：
数据量大时查询响应慢，影响用户体验。

**潜在风险场景**：
- 委托列表查询
- 样品列表查询
- 报告列表查询
- 统计报表查询

**排查方法**：

1. **分析慢查询日志**
   ```sql
   -- MySQL慢查询日志
   -- 查看慢查询配置
   SHOW VARIABLES LIKE 'slow_query%';
   SHOW VARIABLES LIKE 'long_query_time';
   
   -- 分析慢查询
   mysqldumpslow -s t /var/log/mysql/mysql-slow.log
   ```

2. **使用EXPLAIN分析**
   ```sql
   -- 分析查询执行计划
   EXPLAIN SELECT * FROM commissions WHERE ...;
   
   -- 关注以下指标：
   -- type: ALL表示全表扫描，需要优化
   -- key: 使用的索引
   -- rows: 扫描的行数
   -- Extra: 额外信息
   ```

3. **检查索引使用**
   ```sql
   -- 查看表索引
   SHOW INDEX FROM commissions;
   
   -- 查看索引使用情况
   SELECT * FROM sys.schema_index_statistics 
   WHERE table_schema = 'limis';
   ```

**解决方案**：

| 方案 | 说明 |
|------|------|
| 添加索引 | 为常用查询条件添加索引 |
| 优化SQL | 避免全表扫描，使用索引 |
| 分页查询 | 使用LIMIT分页 |
| 缓存结果 | 缓存常用查询结果 |
| 读写分离 | 查询走从库 |

**索引优化建议**：

```sql
-- 常用查询索引
CREATE INDEX idx_commission_status ON commissions(status);
CREATE INDEX idx_commission_created ON commissions(created_at);
CREATE INDEX idx_commission_client ON commissions(client_id);
CREATE INDEX idx_sample_commission ON samples(commission_id);
CREATE INDEX idx_sample_status ON samples(status);

-- 组合索引
CREATE INDEX idx_commission_status_date ON commissions(status, created_at);
```

---

### 4.2 文件上传性能

**问题描述**：
大文件上传慢，上传失败率高。

**排查方法**：

1. **检查服务器配置**
   ```nginx
   # Nginx配置检查
   client_max_body_size 50M;  # 最大上传大小
   client_body_timeout 60s;   # 超时时间
   ```

2. **检查网络带宽**
   ```bash
   # 测试网络速度
   speedtest-cli
   ```

3. **检查存储性能**
   ```bash
   # 测试磁盘IO
   dd if=/dev/zero of=test bs=1M count=1024 conv=fdatasync
   ```

**解决方案**：

| 方案 | 说明 |
|------|------|
| 分片上传 | 大文件分片上传 |
| 断点续传 | 支持断点续传 |
| 压缩上传 | 上传前压缩文件 |
| CDN加速 | 使用CDN加速上传 |
| 异步处理 | 上传后异步处理 |

---

### 4.3 并发性能

**问题描述**：
高并发时系统响应慢，甚至出现错误。

**排查方法**：

1. **检查服务器资源**
   ```bash
   # CPU使用率
   top -bn1 | head -20
   
   # 内存使用
   free -m
   
   # 磁盘IO
   iostat -x 1
   
   # 网络连接
   netstat -an | grep ESTABLISHED | wc -l
   ```

2. **检查应用服务**
   ```bash
   # 查看进程数
   ps aux | grep gunicorn | wc -l
   
   # 查看请求队列
   # Nginx状态
   curl http://localhost/nginx_status
   ```

3. **检查数据库连接**
   ```sql
   -- 查看连接数
   SHOW STATUS LIKE 'Threads_connected';
   SHOW VARIABLES LIKE 'max_connections';
   
   -- 查看活跃连接
   SHOW PROCESSLIST;
   ```

**解决方案**：

| 方案 | 说明 |
|------|------|
| 增加服务器资源 | CPU、内存、带宽 |
| 负载均衡 | 多服务器分担压力 |
| 连接池 | 数据库连接池 |
| 缓存 | Redis缓存热点数据 |
| 异步处理 | 耗时操作异步处理 |

---

## 五、浏览器兼容性

### 5.1 兼容性测试清单

**测试浏览器**：

| 浏览器 | 版本 | 测试内容 |
|--------|------|----------|
| Chrome | 最新版 | 全功能测试 |
| Firefox | 最新版 | 全功能测试 |
| Edge | 最新版 | 全功能测试 |
| Safari | 最新版 | 基础功能测试 |
| IE | 不支持 | 提示更换浏览器 |

**测试项目**：

- [ ] 登录功能
- [ ] 列表展示
- [ ] 表单提交
- [ ] 文件上传
- [ ] 文件下载
- [ ] 打印功能
- [ ] 导出功能
- [ ] 日期选择
- [ ] 下拉选择
- [ ] 弹窗显示
- [ ] 表格滚动
- [ ] 响应式布局

---

### 5.2 常见兼容性问题

**问题1：CSS样式不一致**

**排查方法**：
```javascript
// 使用浏览器开发者工具
// F12 → Elements → Computed
// 查看计算后的样式
```

**解决方案**：
- 使用CSS Reset
- 添加浏览器前缀
- 使用兼容性写法

**问题2：JavaScript API不兼容**

**排查方法**：
```javascript
// 检查API是否支持
if (!Array.prototype.includes) {
    console.log('Array.includes not supported');
}
```

**解决方案**：
- 使用Polyfill
- 使用Babel转译
- 避免使用新API

**问题3：日期格式不一致**

**排查方法**：
```javascript
// 测试日期解析
new Date('2024-01-01');  // 不同浏览器结果可能不同
new Date('2024/01/01');  // 更兼容的格式
```

**解决方案**：
- 使用统一的日期格式
- 使用moment.js或dayjs处理日期
- 后端返回时间戳

---

### 5.3 移动端适配

**测试设备**：

| 设备 | 尺寸 | 测试内容 |
|------|------|----------|
| iPhone | 375×667 | 基础功能 |
| iPad | 768×1024 | 全功能 |
| Android | 360×640 | 基础功能 |

**常见问题**：

| 问题 | 解决方案 |
|------|----------|
| 点击延迟 | 使用fastclick |
| 输入框聚焦 | 防止键盘弹出 |
| 滚动卡顿 | 使用-webkit-overflow-scrolling |
| 1px边框 | 使用transform缩放 |

---

## 六、排查方法和工具

### 6.1 前端排查

**浏览器开发者工具**：

1. **Console面板**
   - 查看JavaScript错误
   - 查看网络请求错误
   - 查看console.log输出

2. **Network面板**
   - 查看请求状态
   - 查看请求时间
   - 查看请求和响应内容

3. **Elements面板**
   - 查看DOM结构
   - 查看CSS样式
   - 调试布局问题

4. **Application面板**
   - 查看Cookie
   - 查看LocalStorage
   - 查看SessionStorage

**常用调试命令**：

```javascript
// 查看Vue组件
$vm0  // 选中组件后可用

// 查看路由
window.$router

// 查看状态
window.$store.state

// 查看API请求
// Network面板 → XHR/Fetch
```

---

### 6.2 后端排查

**日志查看**：

```bash
# 应用日志
tail -f /var/log/limis/app.log

# 错误日志
tail -f /var/log/limis/error.log

# 访问日志
tail -f /var/log/nginx/access.log

# 实时查看错误
tail -f /var/log/limis/error.log | grep ERROR
```

**数据库排查**：

```sql
-- 查看当前连接
SHOW PROCESSLIST;

-- 查看锁等待
SHOW ENGINE INNODB STATUS;

-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;

-- 查看表状态
SHOW TABLE STATUS LIKE 'commissions';

-- 分析表
ANALYZE TABLE commissions;
```

**系统资源排查**：

```bash
# CPU使用
top -p $(pgrep -d',' gunicorn)

# 内存使用
ps aux --sort=-%mem | head

# 磁盘使用
df -h

# 网络连接
netstat -tlnp
```

---

### 6.3 日志查看方法

**日志位置**：

| 日志类型 | 路径 | 说明 |
|----------|------|------|
| 应用日志 | /var/log/limis/app.log | 应用运行日志 |
| 错误日志 | /var/log/limis/error.log | 错误日志 |
| 访问日志 | /var/log/nginx/access.log | Nginx访问日志 |
| 慢查询日志 | /var/log/mysql/mysql-slow.log | 数据库慢查询 |

**日志级别**：

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 一般信息 |
| WARNING | 警告信息 |
| ERROR | 错误信息 |
| CRITICAL | 严重错误 |

**日志查看命令**：

```bash
# 实时查看
tail -f /var/log/limis/app.log

# 查看最近100行
tail -100 /var/log/limis/app.log

# 搜索关键词
grep "ERROR" /var/log/limis/app.log

# 按时间筛选
grep "2024-01-01" /var/log/limis/app.log

# 统计错误数量
grep -c "ERROR" /var/log/limis/app.log

# 多条件筛选
grep "ERROR" /var/log/limis/app.log | grep "commission"
```

---

## 七、错误码对照表

### 7.1 通用错误码

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 200 | 成功 | 请求成功 | - |
| 400 | 请求参数错误 | 参数格式不正确 | 检查请求参数 |
| 401 | 未授权 | 未登录或登录过期 | 重新登录 |
| 403 | 禁止访问 | 无权限访问 | 申请权限 |
| 404 | 资源不存在 | 请求的资源不存在 | 检查请求路径 |
| 405 | 方法不允许 | 请求方法错误 | 检查请求方法 |
| 408 | 请求超时 | 请求处理超时 | 重试或减少数据量 |
| 429 | 请求过于频繁 | 触发限流 | 稍后重试 |
| 500 | 服务器内部错误 | 服务器异常 | 联系管理员 |
| 502 | 网关错误 | 上游服务异常 | 稍后重试 |
| 503 | 服务不可用 | 服务维护中 | 稍后重试 |
| 504 | 网关超时 | 上游服务超时 | 稍后重试 |

### 7.2 业务错误码

#### 用户相关 (1xxx)

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 1001 | 用户名或密码错误 | 登录信息不正确 | 检查用户名密码 |
| 1002 | 账号已被锁定 | 账号被锁定 | 联系管理员解锁 |
| 1003 | 账号已过期 | 账号超过有效期 | 联系管理员续期 |
| 1004 | 密码已过期 | 密码超过有效期 | 修改密码 |
| 1005 | 密码不符合规则 | 密码强度不够 | 使用更强的密码 |
| 1006 | 新密码不能与旧密码相同 | 密码重复 | 使用不同的密码 |
| 1007 | 验证码错误 | 验证码不正确 | 重新输入验证码 |
| 1008 | 验证码已过期 | 验证码超时 | 获取新验证码 |
| 1009 | 用户已存在 | 用户名已注册 | 使用其他用户名 |
| 1010 | 邮箱已存在 | 邮箱已注册 | 使用其他邮箱 |

#### 权限相关 (2xxx)

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 2001 | 无权限访问 | 没有访问权限 | 申请相应权限 |
| 2002 | 无权限操作 | 没有操作权限 | 申请相应权限 |
| 2003 | 角色不存在 | 角色已被删除 | 联系管理员 |
| 2004 | 权限不足 | 权限级别不够 | 申请更高权限 |
| 2005 | 数据权限不足 | 无权访问该数据 | 申请数据权限 |

#### 数据相关 (3xxx)

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 3001 | 数据不存在 | 请求的数据不存在 | 检查数据ID |
| 3002 | 数据已存在 | 数据重复 | 检查数据唯一性 |
| 3003 | 数据已被删除 | 数据已删除 | 检查数据状态 |
| 3004 | 数据状态不允许操作 | 当前状态不可操作 | 检查数据状态 |
| 3005 | 数据被锁定 | 数据正在被编辑 | 等待解锁 |
| 3006 | 数据验证失败 | 数据格式不正确 | 检查数据格式 |
| 3007 | 关联数据存在 | 存在关联数据 | 先删除关联数据 |
| 3008 | 编号已存在 | 编号重复 | 系统自动重新生成 |

#### 文件相关 (4xxx)

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 4001 | 文件不存在 | 文件已被删除 | 重新上传文件 |
| 4002 | 文件大小超限 | 文件超过限制 | 压缩或分割文件 |
| 4003 | 文件格式不支持 | 文件类型不允许 | 转换文件格式 |
| 4004 | 文件上传失败 | 上传过程出错 | 重试上传 |
| 4005 | 文件下载失败 | 下载过程出错 | 重试下载 |
| 4006 | 文件名包含非法字符 | 文件名有特殊字符 | 重命名文件 |

#### 业务相关 (5xxx)

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 5001 | 委托不存在 | 委托已删除 | 检查委托ID |
| 5002 | 委托状态不允许操作 | 委托状态错误 | 检查委托状态 |
| 5003 | 样品不存在 | 样品已删除 | 检查样品ID |
| 5004 | 样品状态不允许操作 | 样品状态错误 | 检查样品状态 |
| 5005 | 检测任务不存在 | 任务已删除 | 检查任务ID |
| 5006 | 检测任务已分配 | 任务已分配给他人 | 检查任务状态 |
| 5007 | 报告不存在 | 报告已删除 | 检查报告ID |
| 5008 | 报告状态不允许操作 | 报告状态错误 | 检查报告状态 |
| 5009 | 设备校准已过期 | 设备不可使用 | 先校准设备 |
| 5010 | 人员资质已过期 | 人员不可操作 | 先更新资质 |

---

## 八、问题排查流程

### 8.1 标准排查流程

```
┌─────────────────────────────────────────────────────────────┐
│                       问题排查流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 问题确认                                                 │
│     ├── 确认问题现象                                         │
│     ├── 确认问题发生时间                                     │
│     ├── 确认问题影响范围                                     │
│     └── 确认问题复现步骤                                     │
│                                                             │
│  2. 信息收集                                                 │
│     ├── 收集错误信息                                         │
│     ├── 收集用户信息                                         │
│     ├── 收集环境信息                                         │
│     └── 收集操作日志                                         │
│                                                             │
│  3. 问题定位                                                 │
│     ├── 前端问题排查                                         │
│     ├── 后端问题排查                                         │
│     ├── 数据库问题排查                                       │
│     └── 网络问题排查                                         │
│                                                             │
│  4. 问题解决                                                 │
│     ├── 临时解决方案                                         │
│     ├── 根本解决方案                                         │
│     └── 验证解决方案                                         │
│                                                             │
│  5. 问题记录                                                 │
│     ├── 记录问题描述                                         │
│     ├── 记录解决方案                                         │
│     └── 更新知识库                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 问题排查清单

**前端排查**：

- [ ] 清除浏览器缓存重试
- [ ] 更换浏览器重试
- [ ] 检查Console错误
- [ ] 检查Network请求
- [ ] 检查Cookie和LocalStorage

**后端排查**：

- [ ] 查看应用日志
- [ ] 查看错误日志
- [ ] 检查服务状态
- [ ] 检查资源使用

**数据库排查**：

- [ ] 检查连接数
- [ ] 检查慢查询
- [ ] 检查锁等待
- [ ] 检查数据一致性

**网络排查**：

- [ ] 检查网络连接
- [ ] 检查DNS解析
- [ ] 检查防火墙
- [ ] 检查代理设置

---

*文档版本: v1.0.0*
*最后更新: 2024年*