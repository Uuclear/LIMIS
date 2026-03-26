# 技术栈决策

## 后端

| 组件 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 语言 | Python | 3.12+ | 开发效率高，检测行业数据处理方便 |
| Web框架 | Django | 5.x | 内置ORM、Admin、Auth，企业级成熟 |
| API框架 | Django REST Framework | 3.15+ | RESTful API标准方案 |
| API文档 | drf-spectacular | latest | OpenAPI 3.0自动生成 |
| 数据库 | PostgreSQL | 16 | JSONB支持动态表单，企业级可靠 |
| 缓存/消息 | Redis | 7.x | 缓存、Celery Broker、会话 |
| 任务队列 | Celery | 5.x | 定时任务、异步报告生成、数据采集 |
| 文件存储 | MinIO | latest | S3兼容，本地部署，存储报告/照片/附件 |
| 报告引擎 | python-docx + WeasyPrint | - | Word模板填充 + PDF生成 |
| 二维码 | qrcode + Pillow | - | 样品标签、报告防伪码 |

## 前端

| 组件 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 框架 | Vue | 3.x | 组合式API，TypeScript支持好 |
| 语言 | TypeScript | 5.x | 类型安全，大型项目必备 |
| 构建工具 | Vite | 6.x | 极速HMR |
| UI库 | Element Plus | latest | 企业级组件库，中文生态好 |
| 状态管理 | Pinia | latest | Vue 3官方推荐 |
| 路由 | Vue Router | 4.x | - |
| HTTP客户端 | Axios | latest | 拦截器、取消请求 |
| 图表 | ECharts | 5.x | 统计看板 |
| 打印 | Print.js | - | 报告/标签打印 |

## 部署

| 组件 | 选型 | 说明 |
|------|------|------|
| 容器化 | Docker + Docker Compose | 一键部署，便于工地现场迁移 |
| Web服务器 | Nginx | 静态资源 + 反向代理 |
| 进程管理 | Gunicorn | Django WSGI服务器 |
| 离线支持 | PWA + 本地Docker | 工地网络不稳定场景 |

## 关键Python依赖

```
Django>=5.0
djangorestframework>=3.15
djangorestframework-simplejwt
drf-spectacular
django-filter
django-cors-headers
django-extensions
celery>=5.3
redis>=5.0
psycopg[binary]>=3.1
python-docx
WeasyPrint
qrcode[pil]
Pillow
minio
gunicorn
```

## 关键前端依赖

```
vue@3
typescript
vite
element-plus
@element-plus/icons-vue
pinia
vue-router@4
axios
echarts
vue-echarts
print-js
@vueuse/core
```
