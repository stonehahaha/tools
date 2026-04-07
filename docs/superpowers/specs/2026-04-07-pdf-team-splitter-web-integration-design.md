# PDF Team Splitter Web Integration Design

Date: 2026-04-07

## 1. Goal

在现有 `tools` 前端工具站中新增一个独立工具页，用于上传人员表和行程单 PDF，
由服务端完成 PDF 拆分与打包，最终向用户返回一个可下载的 `zip` 文件。

`zip` 内容包括：

- 每个团队一个整理后的 PDF
- 一个 `match_report.csv`

这是一个内部多人共用、无账号体系、同步处理的工具。

## 2. Scope

### In scope

- 在现有前端站点中新增一个独立路由和页面
- 页面支持上传 roster 文件和 PDF 文件
- 页面支持填写可选参数：
  - `sheet`
  - `name_column`
  - `team_column`
  - `fuzzy_threshold`
- 新增 Python API 服务，复用已有 PDF 处理逻辑
- API 接收上传文件，处理后直接返回 `zip`
- 使用 Nginx / 1Panel 做统一反向代理
- 使用公网访问密码保护整个工具站

### Out of scope

- 用户账号和权限系统
- 异步任务队列
- 任务历史记录
- 数据库存储
- 浏览器端本地 PDF 解析与合并
- 在线预览生成后的 PDF

## 3. Product Constraints

- 结果交付方式固定为单个 `zip` 下载
- 首版为同步处理：用户点击按钮后等待结果直接返回
- 服务端是可信环境，可运行 Python
- 访问控制不在前端实现，而由 Nginx / 1Panel 统一处理
- 前端继续保持“工具集”模式，PDF 功能作为独立工具，不与现有文本整理页混合

## 4. User Experience

### 4.1 Navigation

- 保留现有 `文本整理` 工具
- 新增一个侧边栏入口，例如 `PDF 行程整理`
- 用户点击后进入独立页面

### 4.2 Page structure

页面采用两栏布局：

- 左侧主工作区
  - 工具说明
  - 人员表上传
  - PDF 上传
  - 可选参数表单
  - 开始处理按钮
  - 处理中状态
  - 错误提示区域
- 右侧说明区
  - 输入要求
  - 支持格式
  - 输出说明
  - 使用步骤

### 4.3 Interaction flow

1. 用户选择人员表文件
2. 用户选择 PDF 文件
3. 用户按需填写可选参数
4. 点击“开始整理”
5. 页面进入 loading，并禁止重复提交
6. 前端发起 `multipart/form-data` 请求
7. 服务端完成处理并返回 `zip`
8. 浏览器自动下载结果文件
9. 如果失败，页面展示明确错误信息

## 5. System Architecture

推荐架构：

1. `tools` 前端
   - Vue 3 + Vite 构建为静态资源
2. `Python API` 服务
   - 单独提供上传和处理接口
   - 直接调用现有 PDF 拆分逻辑
3. `Nginx / 1Panel`
   - 对外提供统一入口
   - 反向代理前端和 API
   - 负责访问密码保护

部署路由建议：

- `/` -> 前端静态站
- `/api/*` -> Python API

## 6. Backend Design

### 6.1 API

主接口：

- `POST /api/pdf-team-split`

请求类型：

- `multipart/form-data`

请求字段：

- `roster`: 必填，人员表文件，支持 `xlsx/xls/csv`
- `pdf`: 必填，源 PDF
- `sheet`: 可选
- `name_column`: 可选，默认 `姓名`
- `team_column`: 可选，默认 `团队`
- `fuzzy_threshold`: 可选，默认 `90`

### 6.2 Processing flow

1. 校验请求内容
2. 将上传文件写入本次请求的临时目录
3. 调用已有 PDF 处理逻辑
4. 在临时输出目录生成：
   - 各团队 PDF
   - `match_report.csv`
5. 将输出目录打包为 `zip`
6. 返回 `application/zip`
7. 清理临时目录和中间文件

### 6.3 Error handling

成功：

- HTTP `200`
- 响应体为 `zip` 文件流

失败：

- HTTP `4xx/5xx`
- 响应体为 JSON
- 至少包含：
  - `message`
  - `detail`（可选）

### 6.4 Output naming

下载包文件名建议：

- `pdf-team-split-YYYYMMDD-HHMMSS.zip`

## 7. Reuse Strategy

服务端不应通过字符串拼接再去调用 CLI。

推荐做法：

- 将现有 `pdftool` 逻辑整理为可导入的 Python 模块
- Web API 直接调用模块函数

这样可以避免：

- 命令行参数拼接错误
- 路径转义问题
- 子进程错误处理分散

## 8. Frontend Design

### 8.1 Form fields

必填项：

- roster 文件
- PDF 文件

可选项：

- sheet
- name_column
- team_column
- fuzzy_threshold

### 8.2 Request behavior

- 使用 `FormData`
- 通过 `fetch` 或统一 API 封装提交到 `/api/pdf-team-split`
- 成功响应后将 `blob` 转为下载

### 8.3 UI states

- 初始态：可选择文件和参数
- 提交中：按钮 loading，禁止重复点击
- 成功态：自动下载，可提示“处理完成”
- 失败态：展示服务端错误

## 9. Access Control

本项目不实现前端登录页，也不实现用户系统。

访问控制由 Nginx / 1Panel 统一完成，推荐：

- Basic Auth
  或
- 1Panel 提供的统一访问密码能力

这样可以：

- 降低前端复杂度
- 避免在浏览器代码中维护密码逻辑
- 统一保护前端页面和后端接口

## 10. Deployment

### 10.1 Frontend

- 在 `tools` 仓库中继续开发和构建
- 产物为静态文件

### 10.2 Backend

- 新增 Python 服务目录，例如：
  - `server/`
  或独立仓库
- 服务运行所需 Python 依赖由该服务单独维护

### 10.3 Reverse proxy

Nginx / 1Panel 配置建议：

- 静态站点处理 `/`
- Python API 处理 `/api/`
- 全站开启统一密码访问
- 控制上传大小上限，避免过小导致 PDF 无法上传

## 11. Security and Operations

首版需要满足：

- 上传文件只保存在临时目录
- 请求完成后清理临时文件
- 不保存原始上传记录
- 不保存处理历史
- 限制单次请求的上传大小
- 限制单次请求处理时长，避免服务长期阻塞

## 12. Testing Scope

前端至少覆盖：

- 页面路由可访问
- 必填项缺失时不可提交
- 提交时进入 loading
- 成功时触发下载
- 失败时展示错误

后端至少覆盖：

- 正常上传并返回 `zip`
- roster 缺失时报错
- PDF 缺失时报错
- 参数透传到 PDF 处理模块
- 临时目录会被清理
- 输出 `zip` 中包含团队 PDF 和 `match_report.csv`

## 13. Recommended Next Step

在此设计确认后，编写实现计划，拆成：

1. 前端路由与页面集成
2. Python API 服务封装
3. 前后端联调与部署配置
