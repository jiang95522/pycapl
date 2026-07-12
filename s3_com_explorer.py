"""
s3_com_explorer.py — CANoe COM 对象层级探测器
目标: 摸清 XCP 相关的 COM API 有哪些
"""
import win32com.client, time, sys
sys.stdout.reconfigure(encoding='utf-8')

CFG_PATH = r"D:\飞书download\02_CANOE_CANAPE_Project\02_CANOE_CANAPE_Project\Canoe15_500K\NVS_Project01.cfg"

def explore(obj, name, depth=0):
    """递归打印 COM 对象的属性和方法"""
    indent = "  " * depth
    print(f"\n{indent}┌─ {name} ({type(obj).__name__})")

    # 区分: 属性 (读访问不报错) vs 方法 vs _开头的内部东西
    attrs = [a for a in dir(obj) if not a.startswith('_')]

    members = []
    for a in attrs:
        try:
            val = getattr(obj, a)
            if callable(val):
                members.append((a, "方法()", ""))
            else:
                # 非方法的属性，尝试打印值
                try:
                    v = str(val)[:60]
                except:
                    v = "<无法显示>"
                members.append((a, f"= {v}", type(val).__name__))
        except Exception as e:
            members.append((a, f"❌ {e}", ""))

    for name_attr, info, typename in members:
        print(f"{indent}│ {name_attr:<30} {info:<40} {typename}")

    print(f"{indent}└─ {len(members)} 个成员")
    return obj

print("=" * 60)
print("CANoe COM XCP 层级探测")
print("=" * 60)

canoe = win32com.client.Dispatch("CANoe.Application")

# ==========================================
# 第 1 层: Configuration
# ==========================================
cfg = explore(canoe, "canoe.Configuration")

# ==========================================
# 第 2 层: Configuration.GeneralSetup
# ==========================================
try:
    gs = cfg.GeneralSetup
    explore(gs, "Configuration.GeneralSetup")
except Exception as e:
    print(f"\n  ❌ GeneralSetup 不存在: {e}")
    gs = None

# ==========================================
# 第 3 层: GeneralSetup.XCPSetup
# ==========================================
xcp_setup = None
if gs:
    try:
        xcp_setup = gs.XCPSetup
        explore(xcp_setup, "GeneralSetup.XCPSetup")
    except Exception as e:
        print(f"\n  ❌ XCPSetup 不存在: {e}")

# ==========================================
# 第 4 层: XCPSetup 的子对象
# ==========================================
if xcp_setup:
    # ECUs 集合
    try:
        ecus = xcp_setup.ECUs
        explore(ecus, "XCPSetup.ECUs (集合)")
        # 看看 ECUs 集合有什么方法 (Add? Item? Count?)
    except Exception as e:
        print(f"\n  ❌ ECUs 不存在: {e}")

    # 再探 XCPSetup 本身的全部成员 (可能有 MeasurementGroups 等)
    # 上面 explore 已经打印过了，这里不用重复

# ==========================================
# 第 5 层: 如果已有 ECU (工程里已导入 A2L)
# ==========================================
canoe.Open(CFG_PATH)

# 重新获取 (Open 后对象树可能刷新)
cfg = canoe.Configuration
gs = cfg.GeneralSetup
xcp_setup = gs.XCPSetup
try:
    ecus = xcp_setup.ECUs
    print(f"\n{'='*60}")
    print(f"工程中的 ECU 数量: {ecus.Count if hasattr(ecus,'Count') else '未知'}")

    # 尝试遍历 ECU
    for i in range(10):  # 最多试 10 个
        try:
            ecu = ecus(i + 1) if hasattr(ecus, '__call__') else ecus.Item(i + 1)
            print(f"\n  ECU[{i+1}]: {ecu}")
            explore(ecu, f"ECU[{i+1}]", depth=1)
        except:
            break

    # 也试一下按名字索引
    try:
        # 如果知道 ECU 名字的话
        for attr in dir(ecus):
            if not attr.startswith('_') and attr not in ['Count', 'Item', 'Add', 'Remove']:
                try:
                    val = getattr(ecus, attr)
                    print(f"\n  ECUs.{attr} = {val}")
                except:
                    pass
    except:
        pass
except Exception as e:
    print(f"\n  ❌ 遍历 ECU 失败: {e}")

# ==========================================
# 第 6 层: System.Namespaces — 看 XCP namespace
# ==========================================
print(f"\n{'='*60}")
print("System.Namespaces — 查找 XCP namespace")
print("=" * 60)
canoe.Measurement.Start()
time.sleep(3)
try:
    # 看看有没有 XCP 命名空间
    ns_xcp = canoe.System.Namespaces("XCP")
    explore(ns_xcp, 'System.Namespaces("XCP")', depth=1)
    # 下面有没有 ECU name 子命名空间?
except Exception as e:
    print(f"\n  ❌ 'XCP' namespace 不存在 (可能需要先 Connect XCP): {e}")

# 列出所有 namespace
try:
    nss = canoe.System.Namespaces
    print(f"\n  Namespaces 类型: {type(nss)}")
    # COM 集合通常支持 _NewEnum, 但 Python 可能直接用 for
    try:
        for ns in nss:
            print(f"  - {ns}")
    except:
        # 不行就用索引
        try:
            count = nss.Count
            print(f"  Namespace 数量: {count}")
            for i in range(1, count + 1):
                try:
                    print(f"  [{i}] {nss(i).Name if hasattr(nss(i),'Name') else nss(i)}")
                except:
                    print(f"  [{i}] ???")
        except Exception as e2:
            print(f"  无法枚举: {e2}")
except Exception as e:
    print(f"  无法访问 Namespaces: {e}")

canoe.Measurement.Stop()

print(f"\n{'='*60}")
print("探测完毕")
print("=" * 60)
input("\n按 Enter 退出...")
