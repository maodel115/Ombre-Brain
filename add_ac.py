import os

# Step 1: 给requirements.txt加mijiaAPI
req_path = "requirements.txt"
with open(req_path, "r") as f:
    content = f.read()
if "mijiaAPI" not in content:
    with open(req_path, "a") as f:
        f.write("\nmijiaAPI\n")
    print("✅ requirements.txt 已添加 mijiaAPI")
else:
    print("⏭️ requirements.txt 已有 mijiaAPI")

# Step 2: 在server.py的clock工具前面插入空调工具
server_path = "server.py"
with open(server_path, "r") as f:
    lines = f.readlines()

# 找到clock工具的注释行
insert_idx = None
for i, line in enumerate(lines):
    if "# Tool 7: clock" in line:
        insert_idx = i
        break

if insert_idx is None:
    print("❌ 找不到clock工具位置")
    exit(1)

ac_code = '''
# =============================================================
# Tool: ac_status — 查空调当前状态
# =============================================================
@mcp.tool()
async def ac_status() -> str:
    """查询崤崤房间空调的当前状态（开关、模式、温度、风速、摆风）"""
    import json as _json
    from mijiaAPI import mijiaAPI as _mijiaAPI

    auth_data = os.environ.get("MI_AUTH_DATA", "")
    if not auth_data:
        return "❌ 未配置MI_AUTH_DATA环境变量"

    auth_path = "/tmp/mi_auth.json"
    with open(auth_path, "w") as f:
        f.write(auth_data)

    try:
        api = _mijiaAPI(auth_path)
        api.login()

        did = "2176155374"
        props = api.get_devices_prop([
            {"did": did, "siid": 3, "piid": 1},
            {"did": did, "siid": 3, "piid": 2},
            {"did": did, "siid": 3, "piid": 4},
            {"did": did, "siid": 4, "piid": 2},
            {"did": did, "siid": 4, "piid": 4},
        ])

        mode_map = {0: "制冷", 1: "制热", 2: "自动", 3: "送风", 4: "除湿"}
        fan_map = {0: "自动", 1: "低风", 2: "中风", 3: "高风"}

        result = {}
        for p in props:
            siid, piid, val = p.get("siid"), p.get("piid"), p.get("value")
            if siid == 3 and piid == 1:
                result["开关"] = "开" if val else "关"
            elif siid == 3 and piid == 2:
                result["模式"] = mode_map.get(val, str(val))
            elif siid == 3 and piid == 4:
                result["温度"] = f"{val}°C"
            elif siid == 4 and piid == 2:
                result["风速"] = fan_map.get(val, str(val))
            elif siid == 4 and piid == 4:
                result["摆风"] = "开" if val else "关"

        return f"崤崤房间空调状态：\\n" + "\\n".join(f"  {k}: {v}" for k, v in result.items())
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"


# =============================================================
# Tool: ac_control — 控制空调
# =============================================================
@mcp.tool()
async def ac_control(action: str = "", temperature: int = 0, mode: str = "", fan: str = "", swing: str = "") -> str:
    """控制崤崤房间的空调。action: on/off; temperature: 16-30; mode: cool/heat/auto/fan/dry; fan: auto/low/medium/high; swing: on/off。可单独设置某一项，也可组合。"""
    import json as _json
    from mijiaAPI import mijiaAPI as _mijiaAPI

    auth_data = os.environ.get("MI_AUTH_DATA", "")
    if not auth_data:
        return "❌ 未配置MI_AUTH_DATA环境变量"

    auth_path = "/tmp/mi_auth.json"
    with open(auth_path, "w") as f:
        f.write(auth_data)

    try:
        api = _mijiaAPI(auth_path)
        api.login()

        did = "2176155374"
        mode_map = {"cool": 0, "heat": 1, "auto": 2, "fan": 3, "dry": 4}
        fan_map = {"auto": 0, "low": 1, "medium": 2, "high": 3}

        commands = []
        messages = []

        if action == "on":
            commands.append({"did": did, "siid": 3, "piid": 1, "value": True})
            messages.append("开机")
        elif action == "off":
            commands.append({"did": did, "siid": 3, "piid": 1, "value": False})
            messages.append("关机")

        if temperature:
            if temperature < 16 or temperature > 30:
                return "❌ 温度范围16-30°C"
            commands.append({"did": did, "siid": 3, "piid": 4, "value": temperature})
            messages.append(f"温度{temperature}°C")

        if mode:
            if mode not in mode_map:
                return f"❌ 模式可选: cool/heat/auto/fan/dry"
            commands.append({"did": did, "siid": 3, "piid": 2, "value": mode_map[mode]})
            mode_zh = {"cool": "制冷", "heat": "制热", "auto": "自动", "fan": "送风", "dry": "除湿"}
            messages.append(f"模式{mode_zh[mode]}")

        if fan:
            if fan not in fan_map:
                return f"❌ 风速可选: auto/low/medium/high"
            commands.append({"did": did, "siid": 4, "piid": 2, "value": fan_map[fan]})
            fan_zh = {"auto": "自动", "low": "低风", "medium": "中风", "high": "高风"}
            messages.append(f"风速{fan_zh[fan]}")

        if swing:
            if swing not in ("on", "off"):
                return "❌ 摆风可选: on/off"
            commands.append({"did": did, "siid": 4, "piid": 4, "value": swing == "on"})
            messages.append(f"摆风{'开' if swing == 'on' else '关'}")

        if not commands:
            return "❌ 请至少指定一个操作（action/temperature/mode/fan/swing）"

        result = api.set_devices_prop(commands)
        failed = [r for r in result if r.get("code") != 0]
        if failed:
            return f"⚠️ 部分操作失败: {failed}"

        return f"✅ 空调已设置: {'、'.join(messages)}"
    except Exception as e:
        return f"❌ 控制失败: {str(e)}"


'''

# 插入
new_lines = lines[:insert_idx] + [ac_code] + lines[insert_idx:]
with open(server_path, "w") as f:
    f.writelines(new_lines)

print(f"✅ 空调工具已插入到 server.py 第{insert_idx}行前面")
print("✅ 完成！")

