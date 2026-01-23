import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler

# Add local deepagents package to path
current_dir = Path(__file__).parent
deepagents_path = current_dir / "deepagents"
if str(deepagents_path) not in sys.path:
    sys.path.insert(0, str(deepagents_path))

from deepagents.graph import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from custom_middleware import ResourceLimitMiddleware, TodoCompletionMiddleware

ANTI_RECURSION_PROMPT = """
# Operational Directives (Anti-Recursion)

## Discovery Limit 
Perform a single `ls -R` or `list_directory` to map the structure. Do not visit every subdirectory individually.

## Stop Condition
Stop all `read_file` operations after accessing 30 core files (prioritize entry points like app.py, graph.py, and nodes.py).

## Heuristic Analysis
If you encounter a large directory of similar files (e.g., utility scripts or prompts), read only one to understand the pattern, then deduce the rest.

## Action Priority
Prioritize generating the final response over gathering 100% complete data. Use placeholders for missing low-level details if necessary to avoid hitting the recursion limit.

## Completion Criteria - YOU MUST FINISH when ANY of these occur:
- ✅ Read 30 files
- ✅ Executed 50 tool calls  
- ✅ Generated draft documentation
- ✅ 80% of todos marked complete
- ✅ Have 80% confidence in analysis

**CRITICAL**: Use completion phrases in your response:
- "ANALYSIS COMPLETE"
- "FINAL REPORT"
- "DOCUMENTATION READY"

This signals the system to terminate gracefully.

## Constraint
If you reach 20 steps without a final answer, stop researching and output the best possible draft based on the information gathered so far. You must deliver a result rather than crashing.
"""

def run_deep_agent(task: str, api_key: str, base_url: str, model_name: str, working_directory: str, callbacks=None, system_prompt: str = None, recursion_limit: int = 150):
    """
    Runs the generic Deep Agent with the given configuration and system prompt.
    """
    
    # Load default system prompt if not provided
    if not system_prompt:
        prompt_path = current_dir / "prompts" / "document_engineer.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = "You are a helpful assistant." # Fallback

    # Inject Anti-Recursion Directives
    system_prompt += f"\n\n{ANTI_RECURSION_PROMPT}"

    # Initialize OpenAI-compatible model
    model = ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0,
    )

    # Initialize Langfuse handler if not provided in callbacks
    # Note: Passed callbacks should ideally include the Langfuse handler if managed externally
    if callbacks is None:
        callbacks = []
        
    # Backend Factory for Sandboxing
    # We create a factory that initializes the FilesystemBackend with the user's working directory
    # and enables virtual_mode to prevent escaping that directory.
    def backend_factory(rt):
        return FilesystemBackend(root_dir=working_directory, virtual_mode=True)

    # Create custom middleware for resource limits
    resource_middleware = ResourceLimitMiddleware(max_file_reads=30, max_steps=50)
    todo_middleware = TodoCompletionMiddleware(completion_threshold=0.8)
    
    # Create the Deep Agent
    # We pass the custom system prompt, backend factory, and custom middleware.
    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        backend=backend_factory,
        middleware=[resource_middleware, todo_middleware],
    )

    # Invoke the agent
    # We return the generator/iterator for streaming if needed, or specific response
    # For Streamlit, we might want to yield chunks.
    
    # Input structure
    try:
        inputs = {
            "messages": [
                {"role": "user", "content": task}
            ]
        }
        stream = agent.astream(inputs, config={"callbacks": callbacks, "recursion_limit": recursion_limit})
    except Exception as e:
        # Fallback for sync/async compatibility issues or different agent structures
        print(f"Error starting stream: {e}")
        raise e
    
    # Use astream for streaming events
    # Return both the agent (for graph viz) and the stream
    return agent, stream

# Alias for backward compatibility
run_document_engineer = run_deep_agent

if __name__ == "__main__":
    # Test run
    load_dotenv()
    print("Running test...")
    # This block is for manual testing only
    pass
