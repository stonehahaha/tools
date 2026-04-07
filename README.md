# Private Tools

这个仓库包含一个 `Vue 3 + Vite` 前端工具站，以及一个用于 PDF 团队行程整理的 `FastAPI` 后端。

## 工具列表

### 文本整理

- 浏览器本地提取旅客信息
- 从旅客订单文本中提取姓名与乘客号
- 输出可直接复制到 Excel 的制表符格式

### PDF 行程整理

- 上传人员表和 PDF
- 服务端按团队拆分行程单
- 返回一个 `zip`，其中包含团队 PDF 和 `match_report.csv`

## 本地开发

### 前端

```bash
npm install
npm run dev
```

### 后端

```bash
py -3.12 -m pip install -r server/requirements.txt
py -3.12 -m uvicorn server.app:app --host 127.0.0.1 --port 8001
```

前端开发代理会把 `/api` 请求转发到 `http://127.0.0.1:8001`。

## 验证命令

```bash
py -3.12 -m pytest server/tests -v
npm run test
npm run type-check
npm run build
```
