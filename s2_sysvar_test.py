"""
Step 2（sysvar 版）: 开阀测试 — 使用 System Variables
=====================================================
自动启动 CANoe，通过 SysVar 控制阀。
正确路径: canoe.System.Namespaces("ASU").Variables("ValveCmd").Value
"""
import win32com.client, time, sys
sys.stdout.reconfigure(encoding='utf-8')

CFG_PATH = r"D:\飞书download\02_CANOE_CANAPE_Project\02_CANOE_CANAPE_Project\Canoe15_500K\NVS_Project01.cfg"
NS_NAME = "ASU"
VAR_CMD = "ValveCmd"
VAR_WAKE = "WakeupEnable"

print("=" * 50)
print("Step 2（sysvar 版）: 开阀测试")
print("=" * 50)

# 1. 启动 CANoe
print("\n[1/4] 启动 CANoe...")
canoe = win32com.client.Dispatch("CANoe.Application")
canoe.Visible = True
canoe.Open(CFG_PATH)
time.sleep(2)
canoe.Measurement.Start()
time.sleep(4)
print("[OK] CANoe 已启动")

# 2. 获取 SysVar 对象
print("\n[2/4] 获取 SysVar 对象...")
try:
    ns = canoe.System.Namespaces(NS_NAME)
    var_cmd = ns.Variables(VAR_CMD)
    var_wake = ns.Variables(VAR_WAKE)
    print(f"[OK] 命名空间 {NS_NAME} 已找到")
    print(f"     ValveCmd 当前值: {var_cmd.Value}")
    print(f"     WakeupEnable 当前值: {var_wake.Value}")
except Exception as e:
    print(f"[FAIL] 获取 SysVar 失败: {e}")
    input("\n按 Enter 退出...")
    exit(1)

# 3. 关阀 + 关唤醒
print("\n[3/4] 初始化...")
var_cmd.Value = 0
var_wake.Value = 1
print(f"[OK] ValveCmd=0（关阀）, WakeupEnable=1（唤醒已开）")
time.sleep(1)

# 4. 开阀
print(f"\n[4/4] 开阀测试（观察电流表）...")
var_cmd.Value = 1
print(f"[OK] ValveCmd=1（开阀），持续 10 秒...")
for i in range(10):
    time.sleep(1)
    v = var_cmd.Value
    w = var_wake.Value
    print(f"     第{i+1}s: ValveCmd={v}, WakeupEnable={w}")

var_cmd.Value = 0
print(f"[OK] ValveCmd=0（关阀）")

print(f"\n{'='*50}")
if any(input("电流表有变化吗？(y/n): ").lower() == 'y' for _ in [1]):
    print("  ✅ SysVar 控制阀成功！")
else:
    print("  ⚠ 阀没动，问题在 DBC/ECU 侧，Python↔SysVar 通路已通")
print(f"{'='*50}")

input("\n按 Enter 退出...")
canoe.Measurement.Stop()