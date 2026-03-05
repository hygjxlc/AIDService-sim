# Architecture Specification for AID-service

## Overview
本规格描述 AID-service（金属加工仿真系统服务端）的整体架构风格、核心组件、横切关注点以及必须遵守的架构约束，用于指导实现与评审，确保服务端在任务管理、文件管理、状态监控、结果下发、数据存储和错误处理等方面具备一致且可维护的架构。

---

## Added Requirements

### REQ-ARC-SVC-001: Architecture Style and Runtime Environment

**The service architecture SHALL follow a layered service architecture style with clear separation between API layer, service layer, repository layer, and infrastructure components.**

**Scenarios:**
- SC-ARC-SVC-001: 通过 FastAPI 对外暴露 REST 接口，由服务层处理业务逻辑
- SC-ARC-SVC-002: 服务层通过仓储层访问 SQLite 数据库
- SC-ARC-SVC-003: 服务层通过算法客户端访问算法层

**Acceptance Criteria:**
- 技术栈：
  - 后端语言：Python 3.8+
  - Web 框架：FastAPI
  - 数据库：SQLite
- 分层：
  - API 层：仅负责请求解析、响应封装，与路由绑定
  - Service 层：实现业务逻辑、调用算法层和文件系统
  - Repository 层：封装所有数据库访问（Task/File/Error 等）
  - Infrastructure 层：算法客户端、文件存储、备份服务等
- 所有外部系统访问（算法层、文件系统、数据库）不得直接从 API 层发起，必须通过 Service/Repository 层完成

---

### REQ-ARC-SVC-002: Core Components per Capability

**The architecture SHALL define core components corresponding to each capability defined in OpenSpec.**

**Scenarios:**
- SC-ARC-SVC-004: 任务管理相关接口由 TaskService 统一实现
- SC-ARC-SVC-005: 文件上传与存储由 FileService 统一实现
- SC-ARC-SVC-006: 状态同步与监控由 StatusSyncService/StatusMonitorService 统一实现
- SC-ARC-SVC-007: 结果下发由 ResultDeliveryService 统一实现
- SC-ARC-SVC-008: 错误码与错误日志由 ErrorHandling 相关组件统一实现

**Acceptance Criteria:**
- 对应组件至少包括：
  - `AuthenticationService` / 认证中间件 → 对应 capability: authentication
  - `TaskService` → 对应 capability: task_management
  - `FileService` → 对应 capability: file_management
  - `StatusSyncService` / 状态监控定时任务 → 对应 capability: status_monitor
  - `ResultDeliveryService` → 对应 capability: result_delivery
  - `TaskRepository` / `FileRepository` / `ErrorLogRepository` → 对应 capability: data_storage
  - `ErrorHandling`（统一异常处理器 + 错误码映射）→ 对应 capability: error_handling
- 每个 REST API 端点必须归属于上述某一个 Service，不允许在路由函数中直接写大量业务逻辑

---

### REQ-ARC-SVC-003: API Layer (FastAPI Routers)

**The API layer SHALL be implemented using FastAPI routers, delegating all business logic to the service layer.**

**Scenarios:**
- SC-ARC-SVC-009: `/api/v1/newTaskCreate` 路由调用 TaskService.new_task_create
- SC-ARC-SVC-010: `/api/v1/uploadParamfiles` 路由调用 FileService.upload_paramfiles
- SC-ARC-SVC-011: `/api/v1/queryTaskStatus` 路由调用 TaskService/StatusSyncService

**Acceptance Criteria:**
- 所有 REST 端点均通过 FastAPI Router 定义，并放置于 `src/api` 包内：
  - 任务相关路由：`src/api/tasks.py`
  - 文件上传路由：`src/api/files.py`
  - 健康检查路由：`src/api/health.py`
- 路由函数仅负责：
  - 请求体/参数解析
  - 认证装饰器挂载
  - 调用对应 Service 方法
  - 将 Service 返回值转换为统一响应模型
- 路由函数中不得直接访问数据库或文件系统

---

### REQ-ARC-SVC-004: Service Layer and Algorithm Client

**The service layer SHALL encapsulate business logic and all interactions with the algorithm layer via a dedicated AlgorithmClient.**

**Scenarios:**
- SC-ARC-SVC-012: 启动任务时，TaskService 调用 AlgorithmClient.start_simulation
- SC-ARC-SVC-013: 停止任务时，TaskService 调用 AlgorithmClient.stop_simulation
- SC-ARC-SVC-014: 查询任务状态时，StatusSyncService 定期调用 AlgorithmClient.query_status

**Acceptance Criteria:**
- Service 层组件至少包括：
  - `TaskService`（创建/启动/停止/删除/状态查询）
  - `FileService`（文件上传、校验与存储）
  - `BackupService`（数据备份）
  - `StatusSync` 或`StatusSyncService`（定时同步状态）
- 算法层访问必须通过 `AlgorithmClient`（位于 `src/services/algorithm_client.py` 或类似位置）完成：
  - 对外提供：`start_task`, `stop_task`, `query_task_status`, `fetch_result` 等方法
- Service 层不得直接使用 `requests` 等 HTTP 库访问算法层，必须通过 AlgorithmClient 封装

---

### REQ-ARC-SVC-005: Repository Layer and Data Storage

**The repository layer SHALL encapsulate all direct SQLite access behind repository classes.**

**Scenarios:**
- SC-ARC-SVC-015: TaskService 通过 TaskRepository 持久化任务信息
- SC-ARC-SVC-016: FileService 通过 FileRepository 记录文件上传信息
- SC-ARC-SVC-017: ErrorHandling 通过 ErrorLogRepository 记录错误日志

**Acceptance Criteria:**
- 至少存在以下仓储类：
  - `TaskRepository`（围绕 task_info 表的 CRUD）
  - `FileRepository`（围绕 file_info 表的 CRUD）
  - `ErrorLogRepository`（围绕 error_log 表的 CRUD）
- 任何对 SQLite 的访问必须通过 Repository 层完成，不允许在 Service 或 API 层直接编写 SQL
- Repository 层可以共享统一的数据库会话管理模块（如 `db.py`）

---

### REQ-ARC-SVC-006: Cross-Cutting Concerns (Error Handling, Logging, Security)

**The architecture SHALL define cross-cutting concerns for error handling, logging, and security consistent with OpenSpec error_codes and quality sections.**

**Scenarios:**
- SC-ARC-SVC-018: 任一 API 出错时，统一返回 `code` + `message`，并记录 error_log
- SC-ARC-SVC-019: 所有请求/响应记录结构化日志（JSON）
- SC-ARC-SVC-020: 所有需要认证的接口都经过 API Key 中间件验证

**Acceptance Criteria:**
- 错误处理：
  - 存在全局异常处理器，将内部异常映射为 `error_codes` 中定义的 code（200, 301–303, 401–404, 500）
  - 错误日志写入 error_log 表，字段至少包含 task_id、error_code、error_message、interface_name、error_time
- 日志：
  - 使用统一日志模块（如 `src/utils/logger.py`）输出结构化日志
  - 日志字段至少包含：timestamp, level, api, task_id, code, message
- 安全：
  - API Key 认证实现为 FastAPI 依赖或中间件，不通过每个路由手写逻辑
  - /health 等公共端点可以绕过认证，其余业务端点默认必须开启认证

---

### REQ-ARC-SVC-007: Architectural Constraints and Non-Functional Requirements

**The architecture SHALL enforce constraints required to meet the non-functional requirements defined in the quality section.**

**Scenarios:**
- SC-ARC-SVC-021: 高并发情况下，数据库访问仍然保持稳定
- SC-ARC-SVC-022: 文件上传 API 响应时间满足性能指标
- SC-ARC-SVC-023: 新增 API 时，能够自然地接入现有分层架构和错误处理机制

**Acceptance Criteria:**
- 性能与扩展：
  - 服务端设计需支持 config.yaml 中定义的并发和吞吐指标
  - 长时间运行时，文件存储和数据库访问不出现连接泄漏
- 可维护性：
  - 新增 API 时，不需要修改底层基础设施（数据库、算法客户端）即可接入
  - 业务逻辑变更集中在 Service 层，尽量不影响 API 层与 Repository 层接口
- 分层约束：
  - API 层 → Service 层 → Repository/AlgorithmClient 层 的调用方向单向，不允许反向依赖
  - 禁止从 Repository 层依赖 Service 或 API 层