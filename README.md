this is new project 
<<<<<<< Updated upstream
=======

  docker build -t rag-debugger .
  docker run --rm --env-file .env -e DEBUG_ROOT=/workspace \
    -v "$(pwd)/my_project:/workspace:ro" rag-debugger . "your question"


    Sources:
SWE-agent, NeurIPS 2024
SWE-agent summary (hyper.ai)
Agentless (arXiv 2407.01489)
Agentless, FSE 2025
AutoCodeRover (arXiv 2404.05427)
LLM-based Agents for Automated Bug Fixing: How Far Are We? (ICSE 2026)
Agentic Software Issue Resolution survey (arXiv 2512.22256)
Advances and Frontiers of LLM-based Issue Resolution survey (arXiv 2601.11655)
SWE-bench glossary (Codegen)
SWE-agent research log (Bean Labs)
>>>>>>> Stashed changes
