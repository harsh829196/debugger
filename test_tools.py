import asyncio, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env={"DEBUG_ROOT": os.path.abspath("my_rag_project")},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            print("TOOLS:", [t.name for t in (await s.list_tools()).tools])
            print(await s.call_tool("list_files", {"directory": "."}))
            print(await s.call_tool("read_file", {"path": "retriever.py", "start_line": 1, "end_line": 5}))
            print(await s.call_tool("read_file", {"path": "../../etc/passwd"}))  # should be refused

asyncio.run(main())