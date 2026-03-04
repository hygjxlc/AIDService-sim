# Status Monitor Module Specification

## Overview
实时采集算法层的仿真任务执行状态，提供任务状态查询能力，支持运行中任务的进度信息和失败任务的错误日志获取。

## Added Requirements

### REQ-SM-001: Task Status Query (queryTaskStatus)
**SHALL** provide API to query real-time task execution status.

**Scenarios:**
- SC-052: 查询created状态任务，返回status=created
- SC-053: 查询running状态任务，返回status=running和附加信息
- SC-054: 查询failed状态任务，返回status=failed和错误日志
- SC-055: 查询finished状态任务，返回status=finished
- SC-056: 查询不存在的TaskID，返回status=not_exist
- SC-057: 查询已删除的TaskID，返回status=delete

**Acceptance Criteria:**
- 返回7种任务状态之一：not_exist, created, running, failed, stop, delete, finished
- running状态返回附加信息：已完成循环轮次、关键参数误差
- failed状态返回附加信息：最后错误日志
- 其他状态附加信息为null
- 成功返回code=200

**Input Parameters:**
| 参数 | 类型 | 必选 | 约束 |
|-----|------|-----|------|
| TaskID | string | 是 | 符合TaskID生成规则 |

**Response:**
| 字段 | 类型 | 说明 |
|-----|------|------|
| code | int | 200成功，404失败 |
| message | string | 响应描述 |
| taskID | string | 任务ID |
| status | string | 任务状态 |
| extra | json | 附加信息（running/failed有值） |

### REQ-SM-002: Running Task Extra Info
**SHALL** provide detailed progress information for running tasks.

**Scenarios:**
- SC-058: 获取running任务的已完成循环轮次
- SC-059: 获取running任务的关键参数误差计算信息

**Acceptance Criteria:**
- extra字段为JSON格式
- 包含字段：cycle（已完成循环轮次）、errorInfo（误差计算信息）
- 示例：{"cycle": 5, "errorInfo": {"deviation": 0.02}}
- 从算法层实时获取进度信息

### REQ-SM-003: Failed Task Error Log
**SHALL** provide error log information for failed tasks.

**Scenarios:**
- SC-060: 获取failed任务的最后错误日志
- SC-061: 错误日志包含时间戳和错误描述

**Acceptance Criteria:**
- extra字段为JSON格式（与running一致）
- 包含字段：error_code（错误码）、error_message（错误描述）、error_time（时间戳）
- 示例：{"error_code": 500, "error_message": "算法层计算溢出，任务终止", "error_time": "2026-03-04T10:00:00"}
- 从算法层或error_log表获取错误信息

### REQ-SM-004: Algorithm Layer Status Sync
**SHALL** synchronize task status with algorithm layer in real-time.

**Scenarios:**
- SC-062: 算法层任务完成时，状态同步为finished
- SC-063: 算法层任务失败时，状态同步为failed
- SC-064: 算法层连接异常时，记录错误日志

**Acceptance Criteria:**
- 实时同步算法层的任务状态
- 算法层异常时自动更新任务状态为failed
- 记录状态变更到error_log表
- 状态变更时更新task_info表的update_time字段

### REQ-SM-005: Task Status Enumeration
**SHALL** define and enforce strict task status values.

**Status Definitions:**
| 状态 | 含义 | 附加信息 |
|-----|------|---------|
| not_exist | TaskID不存在/已被删除 | 无 |
| created | 任务已创建，未启动 | 无 |
| running | 任务正在执行 | 循环轮次、误差信息 |
| failed | 任务执行失败 | 错误日志(JSON: error_code/error_message/error_time) |
| stop | 任务已被手动停止 | 无 |
| delete | 任务已被删除 | 无 |
| finished | 任务执行完成 | 无 |

**Acceptance Criteria:**
- 状态值严格限制为上述7种
- 状态转换遵循业务逻辑
- 状态变更实时持久化到SQLite
