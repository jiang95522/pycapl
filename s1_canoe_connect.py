"""
Step 1: 验证 CANoe COM 连接
==============================
1. 创建 CANoe COM 对象
2. 打开工程文件
3. 启动测量
"""
import win32com.client, time, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# 工程路径（直接从 config.py 来）
CFG_PATH = r"C:\Users\Administrator\Desktop\Test_material\02_CANOE_CANAPE_Project\Canoe15_500K\NVS_Project01.cfg"

print("=" * 50)  
print("Step 1: CANoe COM 连接验证")
print("=" * 50)  #打印五十个=

# 1. 检查工程文件
print(f"\n[1/4] 检查工程文件...")
if not os.path.exists(CFG_PATH):
    print(f"[FAIL] 找不到: {CFG_PATH}")
    exit(1)
print(f"[OK] 工程文件存在: {CFG_PATH}")

#Dispatch() 是 pywin32 提供的工厂函数。"CANoe.Application" 不是随便写的字符串，
#它是 CANoe 注册在 Windows 里的 ProgID（程序标识符）。
# Dispatch() 返回的不是 CANoe.exe 本身，而是 CANoe 内部的一个 Application 对象，它暴露了一组方法供外部调用。

# 2. 创建 CANoe 对象
print(f"\n[2/4] 创建 CANoe COM 对象...")
try:           # ① 试试看
    canoe = win32com.client.Dispatch("CANoe.Application")
    print(f"[OK] 版本: {canoe.Version}")
except Exception as e:         # ② 如果出错了，接住
    print(f"[FAIL] 创建失败: {e}")  #    打印友好的错误信息
    print("      请确认 CANoe 已安装")
    exit(1)                  #   正常退出

# 3. 打开工程
print(f"\n[3/4] 打开工程...")
try:
    canoe.Open(CFG_PATH)
    print(f"[OK] Open 成功")
except Exception as e:
    print(f"[FAIL] Open 失败: {e}")
    print("      => 请关闭所有 CANoe 窗口后再试")
    exit(1)

# 4. 启动测量
print(f"\n[4/4] 启动测量...")
time.sleep(2)
try:
    canoe.Measurement.Start()
    time.sleep(2)
    print(f"[OK] Measurement.Start 成功")
except Exception as e:
    print(f"[FAIL] Start 失败: {e}")
    exit(1)

print(f"\n{'='*50}")
print(f"  Step 1 通过！CANoe 已连接并运行中")
print(f"{'='*50}")