import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

NEEDS_APPROVAL = {"run_command", "run_tests", "edit_file", "git_create_branch",
                  "git_commit", "git_push", "create_pull_request"}

SYSTEM = """You are a coding debugger working inside one project folder.
Workflow:
1. Get a signal: run the failing command (run_command) or check_syntax. Do not guess from reading alone.
2. Localize: use the error's file and line, then read only that part (read_file).
3. Expand only on evidence: if the code calls or imports something, use find_symbol, then read that definition. Never open files just to look around.
4. After learning something about a file, call save_note with one short line (what a function takes and returns, what you found).
5. After any change, rerun the failing command and report its actual output.
Quote code exactly as tools return it. Never correct or rewrite it in your answer.
If a tool returns an error, read it and adjust."""


def gated(tool):
    """Wrap a tool so the user must approve each call."""
    original = tool.coroutine

    async def run(**kwargs):
        print(f"\n--- Agent wants to run: {tool.name} ---")
        for k, v in kwargs.items():
            print(f"{k}:\n{v}\n")
        answer = await asyncio.to_thread(input, "Approve? [y/N] ")
        if answer.strip().lower() != "y":
            return "DENIED by the user. Do not retry the same action. Explain or propose an alternative."
        return await original(**kwargs)

    return StructuredTool(
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
        coroutine=run,
        response_format=tool.response_format,
    )


def resolve_root(arg):
    root = os.path.realpath(os.path.expanduser(arg or os.getenv("DEBUG_ROOT") or os.getcwd()))
    if not os.path.isdir(root):
        raise SystemExit(f"Not a folder: {root}")
    if root in {"/", os.path.expanduser("~")}:
        raise SystemExit(f"Refusing to use {root} as the root. Point to a project folder.")
    return root


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", nargs="?", default="Which file defines the main entry point? Use search_code.")
    parser.add_argument("--root", help="project folder the agent may read")
    args = parser.parse_args()

    root = resolve_root(args.root)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GOOGLE_API_KEY not set. Check your .env file.")

    client = MultiServerMCPClient({
        "debugger": {
            "command": sys.executable,
            "args": ["mcp_server.py"],
            "transport": "stdio",
            "env": {"DEBUG_ROOT": root},
        }
    })

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        max_retries=1,
    )

    print(f"Root: {root}")
    async with client.session("debugger") as session:      # one server process for the whole run
        tools = await load_mcp_tools(session)
        print("Tools:", [t.name for t in tools])
        tools = [gated(t) if t.name in NEEDS_APPROVAL else t for t in tools]

        agent = create_react_agent(llm, tools, prompt=SYSTEM, checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": "session-1"}, "recursion_limit": 12}

    while True:
        question = await asyncio.to_thread(input, "\nYou (or 'exit'): ")
        if question.strip().lower() in {"exit", "quit"}:
         break
        async for step in agent.astream(
        {"messages": [("user", question)]}, config=config, stream_mode="values"):
            step["messages"][-1].pretty_print()


if __name__ == "__main__":
    asyncio.run(main())