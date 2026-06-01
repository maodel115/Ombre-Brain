import re

with open('/Users/quxiao/Ombre-Brain/server.py', 'r') as f:
    content = f.read()

new_tool = '''
# =============================================================
# Tool 7: clock — Get current time and bridge data
# =============================================================
@mcp.tool()
async def clock(query: str = "time") -> str:
    """查询时间或崤崤的设备状态。query可选: time/heartrate/device"""
    import httpx as _httpx
    base = "https://claude-bridge.zeabur.app"
    endpoints = {
        "time": f"{base}/time",
        "heartrate": f"{base}/heartrate",
        "device": f"{base}/device",
    }
    url = endpoints.get(query, endpoints["time"])
    try:
        async with _httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            return resp.text
    except Exception as e:
        return f"查询失败: {e}"


'''

marker = '# =============================================================\n# Tool 6: dream'
content = content.replace(marker, new_tool + marker)

with open('/Users/quxiao/Ombre-Brain/server.py', 'w') as f:
    f.write(content)

print('done')

