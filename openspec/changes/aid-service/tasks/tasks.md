# AID-service Implementation Tasks

## Overview
基于需求规格文档，按模块划分的实现任务列表，用于指导多智能体协同开发。

---

## Phase 1: Project Setup & Infrastructure

### TASK-001: Project Initialization
- [ ] 创建 FastAPI 项目骨架
- [ ] 配置 requirements.txt 依赖
- [ ] 创建项目目录结构 (src/api, src/services, src/models, src/database)
- [ ] 配置 .env 环境变量模板

### TASK-002: Database Setup
- [ ] 实现 SQLite 数据库初始化模块
- [ ] 创建 task_info 表结构和 ORM 模型
- [ ] 创建 file_info 表结构和 ORM 模型
- [ ] 创建 error_log 表结构和 ORM 模型
- [ ] 实现数据库连接池管理
- [ ] 实现事务管理工具类

### TASK-003: Configuration Management
- [ ] 创建配置文件结构 (config.yaml)
- [ ] 实现配置读取模块
- [ ] 配置 API Key、数据库路径、存储路径等参数
- [ ] 实现配置校验逻辑

---

## Phase 2: Core Modules Implementation

### TASK-004: Authentication Module (authentication_spec.md)
- [ ] 实现 API Key 认证中间件
- [ ] 从配置文件读取合法 API Key
- [ ] 创建认证拦截器装饰器
- [ ] 实现认证失败响应 (code=401)
- [ ] 预留扩展接口 (Token/OAuth2.0)
- [ ] 编写认证模块单元测试

### TASK-005: Error Handling Module (error_handling_spec.md)
- [ ] 定义错误码枚举类 (200, 301-303, 401-404, 500)
- [ ] 实现统一响应格式类 (BaseResponse)
- [ ] 创建全局异常处理器
- [ ] 实现错误日志记录功能
- [ ] 编写错误处理单元测试

### TASK-006: Data Storage Module (data_storage_spec.md)
- [ ] 实现 TaskRepository (CRUD 操作)
- [ ] 实现 FileRepository (CRUD 操作)
- [ ] 实现 ErrorLogRepository (CRUD 操作)
- [ ] 实现 TaskID 序列生成器
- [ ] 实现数据库备份定时任务
- [ ] 编写存储模块单元测试

---

## Phase 3: Business API Implementation

### TASK-007: Task Creation API (newTaskCreate)
- [ ] 实现 POST /api/v1/newTaskCreate 端点
- [ ] 实现 simulateType 校验 (LaWan/CHOnYA/ZhuZao/ZhaZhi/ZHEWan/JIYA)
- [ ] 实现 taskName 格式校验 (1-64字符, 字母/数字/下划线)
- [ ] 实现 TaskID 生成逻辑
- [ ] 创建任务目录结构
- [ ] 持久化任务信息到数据库
- [ ] 编写 API 单元测试

### TASK-008: File Upload API (uploadParamfiles)
- [ ] 实现 POST /api/v1/uploadParamfiles 端点
- [ ] 请求体包含 TaskID 和 files 文件数组
- [ ] 实现多文件上传处理
- [ ] 实现文件名称校验 (必选/可选文件列表)
- [ ] 实现文件格式校验 (stp/txt/csv/yml/jnl)
- [ ] 实现文件大小校验 (≤10M B)
- [ ] 实现文件存储 (/data/aid/{TaskID}/)
- [ ] 实现同名文件覆盖
- [ ] 持久化文件信息到数据库 (file_type=required/optional)
- [ ] 编写 API 单元测试

### TASK-009: Task Verification API (newTaskverify)
- [ ] 实现 POST /api/v1/newTaskverify 端点
- [ ] 请求体包含 TaskID
- [ ] 查询已上传文件列表
- [ ] 校验7个必选文件完整性
- [ ] 返回 ready 状态和 missingFiles 列表
- [ ] 编写 API 单元测试

### TASK-010: Task Start API (startTask)
- [ ] 实现 POST /api/v1/startTask 端点
- [ ] 请求体包含 TaskID
- [ ] 校验任务状态 (created/stop)
- [ ] 校验必选文件完整性
- [ ] 调用算法层启动仿真
- [ ] 更新任务状态为 running
- [ ] 编写 API 单元测试

### TASK-011: Task Stop API (stopTask)
- [ ] 实现 POST /api/v1/stopTask 端点
- [ ] 请求体包含 TaskID
- [ ] 校验任务状态 (running)
- [ ] 调用算法层停止仿真
- [ ] 更新任务状态为 stop
- [ ] 保留参数文件
- [ ] 编写 API 单元测试

### TASK-012: Task Delete API (deleteTask)
- [ ] 实现 POST /api/v1/deleteTask 端点
- [ ] 请求体包含 TaskID
- [ ] 支持删除任意状态任务
- [ ] running 状态任务先停止
- [ ] 删除任务目录及所有文件
- [ ] 删除数据库相关记录
- [ ] 编写 API 单元测试

### TASK-013: Task Status Query API (queryTaskStatus)
- [ ] 实现 POST /api/v1/queryTaskStatus 端点
- [ ] 请求体包含 TaskID
- [ ] 从算法层获取实时状态
- [ ] 返回7种状态之一
- [ ] running 状态返回进度信息 (cycle, errorInfo)
- [ ] failed 状态返回错误日志
- [ ] 编写 API 单元测试

### TASK-014: Task Result Fetch API (fetachTaskResult)
- [ ] 实现 GET /api/v1/fetachTaskResult 端点
- [ ] 查询参数包含 TaskID
- [ ] 校验任务状态 (finished)
- [ ] 验证结果文件存在
- [ ] 返回 .stp 格式文件流
- [ ] 编写 API 单元测试

### TASK-015: Health Check API (health)
- [ ] 实现 GET /api/v1/health 端点
- [ ] 跳过认证中间件
- [ ] 检查数据库连接
- [ ] 检查算法层连接
- [ ] 返回服务健康状态 (code/status/message/timestamp)
- [ ] 编写 API 单元测试

---

## Phase 4: Algorithm Layer Integration

### TASK-016: Algorithm Layer Client
- [ ] 定义算法层接口协议
- [ ] 实现算法层 HTTP 客户端
- [ ] 实现启动仿真接口调用
- [ ] 实现停止仿真接口调用
- [ ] 实现状态查询接口调用
- [ ] 实现连接超时处理
- [ ] 实现重试机制

### TASK-017: Algorithm Layer Callback Handler
- [ ] 实现算法层回调接收端点
- [ ] 接收仿真完成通知
- [ ] 接收结果文件
- [ ] 更新任务状态
- [ ] 记录错误日志

---

## Phase 5: File & Status Management

### TASK-018: File Storage Service
- [ ] 实现文件存储服务类
- [ ] 实现目录创建/删除
- [ ] 实现文件写入/读取
- [ ] 实现文件覆盖逻辑
- [ ] 实现目录清理功能

### TASK-019: Status Sync Service
- [ ] 实现状态同步服务
- [ ] 定时轮询算法层状态
- [ ] 状态变更时更新数据库
- [ ] 记录状态变更日志

---

## Phase 6: Quality & Operations

### TASK-020: Logging & Monitoring
- [ ] 配置日志框架 (loguru/logging)
- [ ] 实现结构化日志格式
- [ ] 日志按日滚动
- [ ] 记录接口请求/响应日志
- [ ] 记录错误堆栈信息

### TASK-021: Performance Optimization
- [ ] 实现接口响应时间监控
- [ ] 确保接口响应时间<2s
- [ ] 确保 Health Check 响应<100ms
- [ ] 实现数据库连接池

### TASK-022: Security Hardening
- [ ] 文件上传安全检查
- [ ] 防止恶意文件上传
- [ ] 目录权限控制
- [ ] 敏感信息脱敏

### TASK-023: Database Backup
- [ ] 实现定时备份任务
- [ ] 备份间隔 1 小时
- [ ] 保留 24 小时备份
- [ ] 自动清理过期备份

---

## Phase 7: Testing & Documentation

### TASK-024: Unit Tests
- [ ] 认证模块单元测试
- [ ] 任务管理 API 单元测试
- [ ] 文件管理 API 单元测试
- [ ] 数据存储模块单元测试
- [ ] 错误处理模块单元测试

### TASK-025: Integration Tests
- [ ] 完整任务生命周期测试
- [ ] 文件上传流程测试
- [ ] 算法层集成测试
- [ ] 错误场景测试

### TASK-026: API Documentation
- [ ] 生成 OpenAPI/Swagger 文档
- [ ] 编写接口使用示例
- [ ] 记录错误码说明

### TASK-027: Architecture Implementation Alignment (architecture_spec.md)
- [ ] 对照 architecture_spec.md 检查 API 层、服务层、仓储层和算法客户端的实现是否完整
- [ ] 确认各 capability（authentication、task_management、file_management、status_monitor、result_delivery、data_storage、error_handling）均有对应 service/repository 组件
- [ ] 确认 API 层不直接访问数据库或文件系统，均通过 Service/Repository 层访问

### TASK-028: Architecture Compliance Review (architecture_spec.md)
- [ ] 按 REQ-ARC-SVC-001 ~ REQ-ARC-SVC-007 制作架构检查清单
- [ ] 检查错误码使用是否与 error_codes 段一致
- [ ] 检查日志字段和格式是否与 quality.observability 要求一致
- [ ] 检查认证中间件是否覆盖所有需要认证的接口
- [ ] 输出一次架构评审结论记录（通过/问题列表）

---

## Task Dependencies

```
TASK-001 → TASK-002 → TASK-003
                ↓
TASK-004, TASK-005, TASK-006 (可并行)
                ↓
TASK-007 → TASK-008 → TASK-009 → TASK-010/TASK-011/TASK-012
                                            ↓
TASK-013, TASK-014, TASK-015, TASK-016, TASK-017
                ↓
TASK-018, TASK-019 → TASK-020/TASK-021/TASK-022/TASK-023
                ↓
TASK-024 → TASK-025 → TASK-026
```

---

## Acceptance Criteria Summary

| 阶段 | 验收标准 |
|-----|---------|
| Phase 1 | 项目可启动，数据库自动创建 |
| Phase 2 | 认证、错误处理、存储模块可独立测试 |
| Phase 3 | 所有 9 个 API 端点正常运行 |
| Phase 4 | 算法层调用正常，回调处理正确 |
| Phase 5 | 文件存储、状态同步正常工作 |
| Phase 6 | 性能达标，安全加固完成 |
| Phase 7 | 测试覆盖率>80%，文档完整 |
