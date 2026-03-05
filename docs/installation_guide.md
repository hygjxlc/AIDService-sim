# AID-Service 安装与配置手册

## 目录

1. [环境要求](#1-环境要求)
2. [目录结构](#2-目录结构)
3. [安装步骤](#3-安装步骤)
4. [配置文件说明](#4-配置文件说明)
5. [日志配置](#5-日志配置)
6. [启动服务](#6-启动服务)
7. [验证服务](#7-验证服务)
8. [常见问题](#8-常见问题)

---

## 1. 环境要求

| 组件 | 版本要求 | 说明 |
|-----|---------|------|
| Python | 3.9+ | 运行时环境 |
| pip | 最新版 | 依赖管理 |
| 操作系统 | Windows 10+ / Linux / macOS | 均支持 |

> **注意**：无需 Docker，无需独立数据库（内置 SQLite）。

---

## 2. 目录结构

```
AID-service/
├── app_config.yaml       # 主配置文件（重要）
├── requirements.txt      # Python 依赖列表
├── start.bat             # Windows 启动脚本
├── start.sh              # Linux/macOS 启动脚本
├── src/                  # 源代码
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置加载模块
│   ├── api/              # API 路由
│   ├── services/         # 业务服务
│   ├── database/         # 数据库操作
│   ├── models/           # 数据模型
│   └── utils/
│       └── logger.py     # 日志配置模块
├── data/                 # 运行时数据（自动创建）
│   ├── aid_service.db    # SQLite 数据库
│   └── aid/              # 文件存储目录
├── logs/                 # 日志目录（自动创建）
│   └── aid-service-YYYY-MM-DD.log
└── backups/              # 数据库备份（自动创建）
```

---

## 3. 安装步骤

### 3.1 克隆代码

```bash
git clone <仓库地址>
cd AID-service
```

### 3.2 安装 Python 依赖

```bash
pip install -r requirements.txt
```

主要依赖包：

| 包名 | 版本 | 用途 |
|-----|-----|------|
| fastapi | >=0.100.0 | Web 框架 |
| uvicorn[standard] | >=0.23.0 | ASGI 服务器 |
| sqlalchemy | >=2.0.0 | ORM 数据库 |
| pyyaml | >=6.0 | 配置文件解析 |
| loguru | >=0.7.0 | 日志库 |
| httpx | >=0.24.0 | HTTP 客户端 |
| aiofiles | >=23.0.0 | 异步文件 I/O |
| python-multipart | >=0.0.6 | 文件上传支持 |

### 3.3 修改配置文件

根据实际环境修改 `app_config.yaml`（详见第 4 节）。

---

## 4. 配置文件说明

配置文件路径：`AID-service/app_config.yaml`

```yaml
# AID-Service Configuration

# 认证配置
auth:
  api_key: "11111111"          # API 访问密钥，客户端须携带此密钥

# 内部回调认证
internal:
  callback_token: "aid_internal_callback_token_2024"   # 内部服务回调令牌

# 数据库配置
database:
  path: "./data/aid_service.db"     # SQLite 数据库文件路径
  backup_path: "./backups/"          # 数据库备份目录

# 文件存储配置
storage:
  base_path: "./data/aid/"           # 任务文件存储根目录

# 算法服务配置
algorithm:
  base_url: "http://localhost:9000"  # 算法层服务地址
  timeout_sec: 30                    # 请求超时时间（秒）
  mock_mode: true                    # true=模拟模式（无需真实算法服务）

# 日志配置
logging:
  level: "INFO"                      # 日志级别（见第 5 节）
  path: "./logs/"                    # 日志文件存储目录
  retention_days: 30                 # 日志文件保留天数
```

### 4.1 认证配置（auth）

| 字段 | 说明 | 默认值 |
|-----|------|-------|
| `api_key` | 客户端访问密钥，所有 API 请求须在请求体中携带 `api_key` 字段 | `11111111` |

> **安全提示**：生产环境请修改为强密码，与 SDK 端 `config.properties` / `config.yml` 中的 `apiKey` 保持一致。

### 4.2 算法服务配置（algorithm）

| 字段 | 说明 |
|-----|------|
| `base_url` | 算法计算层的服务地址 |
| `timeout_sec` | 调用算法服务的超时时间 |
| `mock_mode` | `true`：模拟模式，跳过真实算法调用，适合调试；`false`：生产模式 |

---

## 5. 日志配置

### 5.1 日志级别

修改 `app_config.yaml` 中的 `logging.level` 字段：

| 级别 | 值 | 适用场景 |
|-----|-----|---------|
| 调试模式 | `"DEBUG"` | 开发、测试阶段，输出详细信息 |
| 信息模式 | `"INFO"` | 生产环境，输出关键流程信息（推荐） |
| 警告模式 | `"WARNING"` | 只记录异常和警告 |
| 错误模式 | `"ERROR"` | 只记录错误信息 |

**修改示例（改为 DEBUG）：**

```yaml
logging:
  level: "DEBUG"    # 原为 "INFO"，改为 "DEBUG"
  path: "./logs/"
  retention_days: 30
```

> **注意**：修改配置文件后需重启服务才能生效。

### 5.2 日志文件位置

- 日志目录：`AID-service/logs/`（服务启动时自动创建）
- 日志文件命名：`aid-service-YYYY-MM-DD.log`（按天滚动）
- 示例：`aid-service-2026-03-05.log`

### 5.3 日志保留策略

由 `retention_days` 控制，默认保留 30 天，超期自动删除旧日志。

### 5.4 日志格式

**控制台输出**（带颜色）：
```
2026-03-05 13:39:16 | INFO     | src.main:26 | AID-Service started. Database: ./data/aid_service.db
```

**文件输出**（纯文本）：
```
2026-03-05 13:39:16 | INFO     | src.main:26 | AID-Service started. Database: ./data/aid_service.db
```

### 5.5 日志模块说明

日志由 `src/utils/logger.py` 统一管理，提供分类日志器：

| 日志器 | 函数 | 用途 |
|-------|------|------|
| 访问日志 | `get_access_logger()` | 记录 API 请求访问 |
| 业务日志 | `get_business_logger()` | 记录业务逻辑处理 |
| 错误日志 | `get_error_logger()` | 记录异常错误 |
| 系统日志 | `get_system_logger()` | 记录服务启停等系统事件 |

---

## 6. 启动服务

### 6.1 Windows 启动

```bat
# 方式一：使用启动脚本
start.bat

# 方式二：手动命令
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6.2 Linux / macOS 启动

```bash
# 方式一：使用启动脚本
chmod +x start.sh
./start.sh

# 方式二：手动命令
python -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6.3 启动参数说明

| 参数 | 值 | 说明 |
|-----|-----|------|
| `--host` | `0.0.0.0` | 监听所有网卡（可改为 `127.0.0.1` 限制本机访问） |
| `--port` | `8080` | 服务端口 |
| `--reload` | — | 开发模式，代码变更自动重载（生产环境去掉此参数） |

### 6.4 启动成功标志

控制台出现以下输出即表示启动成功：

```
INFO     | src.main:26 | AID-Service started. Database: ./data/aid_service.db
INFO     | src.main:34 | Background services started
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```

---

## 7. 验证服务

### 7.1 健康检查

```bash
# GET 请求，无需认证
curl http://127.0.0.1:8080/api/v1/health
```

期望返回：
```json
{"code": 200, "message": "success", "data": {"status": "healthy"}}
```

### 7.2 API 文档

服务启动后访问以下地址查看接口文档：

- Swagger UI：`http://127.0.0.1:8080/docs`
- ReDoc：`http://127.0.0.1:8080/redoc`

### 7.3 API 认证方式

所有业务接口（除健康检查外）需在请求体 JSON 中携带 `api_key` 字段：

```json
{
  "api_key": "11111111",
  "...其他参数..."
}
```

---

## 8. 常见问题

### Q1：启动报错 `ModuleNotFoundError`

**原因**：Python 依赖未安装或安装不完整。

**解决**：
```bash
pip install -r requirements.txt
```

### Q2：端口 8080 被占用

**解决**：修改启动命令中的端口号：
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 9090
```

### Q3：API 返回 401 认证失败

**原因**：客户端请求体中的 `api_key` 与 `app_config.yaml` 中配置的不一致。

**解决**：检查并对齐以下两处配置：
- 服务端：`app_config.yaml` → `auth.api_key`
- Java SDK：`config/config.properties` → `apiKey`
- Python SDK：`config/config.yml` → `apiKey`

### Q4：修改配置后不生效

**原因**：配置文件在服务启动时加载，修改后需重启。

**解决**：按 `CTRL+C` 停止服务后重新启动。

### Q5：日志文件没有生成

**原因**：`logs/` 目录会在服务启动时自动创建，若目录无写权限则失败。

**解决**：手动创建目录或检查目录权限：
```bash
mkdir logs
```
