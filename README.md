# ASU NVM 自动化测试 — 分步脚本说明

> 本目录放置分步测试脚本，按顺序执行，每完成一步验收后再继续下一步。

## 当前进度

| 脚本                    | 说明                                   | 状态             |
| --------------------- | ------------------------------------ | -------------- |
| `s1_canoe_connect.py` | Step 1: CANoe COM 连接验证               | ✅ 通过           |
| `s2_sysvar_test.py`   | **Step 2: 使用 System Variables 开阀测试** | ✅ **通过！阀已能控制** |
| `s3_...`              | Step 3~5 待创建                         | ⏳              |

---

## System Variables（sysvar）使用方法

### 什么是 sysvar？

System Variables 是 CANoe 提供的 Python ↔ CAPL 通信机制。Python 通过 COM 写值，CAPL 用 `@sysvar::` 语法实时读取。**不依赖 DBC 信号映射**，是 CANoe 官方设计的跨语言通信方式。

### 前置条件：在 CANoe 中手动创建 System Variables

**只用做一次**，操作步骤：

1. 打开 CANoe 工程 `NVS_Project01.cfg`
2. 菜单栏 **Home** → 点击 **System Variables** 按钮
3. 左侧树 → 右键 **System Variables** → **New Variable...**
4. 创建 `ValveCmd`：Name=`ValveCmd`, Namespace=`ASU`, Type=**Integer**, Default=0
5. 创建 `WakeupEnable`：Name=`WakeupEnable`, Namespace=`ASU`, Type=**Integer**, Default=1
6. 编译 CAPL（**F11**）
7. 保存工程（**Ctrl+S**）

### Python 读写 sysvar 的正确 API

```python
# ✅ 正确（已验证）
canoe.System.Namespaces("ASU").Variables("ValveCmd").Value = 1

# ❌ 错误（CANoe 15 SP6 不支持）
canoe.SystemVariables("ASU", "ValveCmd").Value = 1    # 不存在
canoe.System("ASU").Variables("ValveCmd").Value = 1    # 不存在
```

**完整用法：**

```python
# 获取变量对象
var_cmd = canoe.System.Namespaces("ASU").Variables("ValveCmd")

# 写值
var_cmd.Value = 1   # 开阀
var_cmd.Value = 0   # 关阀

# 读值
val = var_cmd.Value
```

### CAPL 读写 sysvar 的代码

```c
// CAPL 用 @sysvar::命名空间::变量名 读取（已验证通过）
Fr09Msg.SuspDistbnVlvCtrlStsSuspDistbnVlvCtrlSts = @sysvar::ASU::ValveCmd;

// 控制唤醒
if (@sysvar::ASU::WakeupEnable == 1)
{
    output(XcmNmMsg);
}
```

---

## 经验教训（踩过的坑）

### ❌ 失败方案 1：Signals().Value + getSignal()

**尝试：** Python 写 `canoe.Signals("信号名").Value = 1`，CAPL 用 `getSignal(报文::信号)` 读取。

**结果：** ❌ 信号数据库值变了但报文发出去没变，阀不动作。

**原因：** `Signals().Value` 和 `getSignal()` 走的是 DBC 信号映射，受节点隔离影响，Python 改的值不一定能被 CAPL 读到。

### ❌ 失败方案 2：导入 .vsysvar 文件

**尝试：** 创建一个 XML 格式的 `.vsysvar` 文件导入 CANoe。

**结果：** ❌ 报错 "The content of the file is invalid"。

**原因：** 不知道正确的 XML schema，不如手动创建方便。

### ✅ 成功方案：手动创建 SysVar + COM 读写

**步骤：**

1. 在 CANoe System Variables 管理器手动创建变量
2. CAPL 用 `@sysvar::ASU::ValveCmd` 直接读取
3. Python 用 `canoe.System.Namespaces("ASU").Variables("ValveCmd").Value` 读写

**为什么成功：** SysVar 是 CANoe 内部变量空间，不依赖 DBC，不受节点隔离，COM 和 CAPL 都能直接访问。

---

## 运行方式

```
py -3 steps\s1_canoe_connect.py      # Step 1: 验证连接
py -3 steps\s2_sysvar_test.py        # Step 2: sysvar 开阀测试 ✅
```

> ⚠ 必须用 `py -3`，不要用 `python`（系统有 Microsoft Store 别名冲突）
> ⚠ 运行前请关闭所有 CANoe 窗口，脚本会自行启动

---

## 详细说明

请参考 `docs/` 目录下的文档：

- `docs/执行步骤.md` — 分步指南和当前进度
- `docs/测试方案.md` — 架构设计
- `docs/会话记录.md` — 接续记录