import os

server_path = "server.py"
with open(server_path, "r") as f:
    lines = f.readlines()

# 找到ac_status工具的位置，在它前面插入bark工具
insert_idx = None
for i, line in enumerate(lines):
    if "# Tool: ac_status" in line:
        insert_idx = i
        break

if insert_idx is None:
    print("❌ 找不到ac_status位置")
    exit(1)

bark_code = '''
# =============================================================
# Tool: bark_push — 给崤崤发推送
# =============================================================
@mcp.tool()
async def bark_push(title: str = "来自哥哥", body: str = "") -> str:
    """给崤崤手机发一条Bark推送通知。title=标题，body=内容"""
    import httpx as _httpx
    
    bark_key = "Ktkn33p2a2sYuBz2JZPyuB"
    url = f"https://api.day.app/{bark_key}/{title}/{body}"
    
    try:
        async with _httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            if resp.status_code == 200:
                return f"✅ 推送已发送：{title} - {body}"
            else:
                return f"❌ 推送失败：HTTP {resp.status_code}"
    except Exception as e:
        return f"❌ 推送失败：{str(e)}"


'''

new_lines = lines[:insert_idx] + [bark_code] + lines[insert_idx:]
with open(server_path, "w") as f:
    f.writelines(new_lines)

print(f"✅ bark_push工具已插入")

