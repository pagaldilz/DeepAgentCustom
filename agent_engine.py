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

def run_deep_agent(task: str, api_key: str, base_url: str, model_name: str, working_directory: str, callbacks=None, system_prompt: str = None):
    """
    Runs the generic Deep Agent with the given configuration and system prompt.
    """
    
    # Load default system prompt if not provided
    if not system_prompt:
        prompt_path = current_dir / "ralph_mode" / "document_engineer.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = "You are a helpful assistant." # Fallback

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

    # Create the Deep Agent
    # We pass the custom system prompt and the backend factory.
    agent = create_deep_agent(
        model=model,
        system_prompt=system_prompt,
        backend=backend_factory,
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
        stream = agent.astream(inputs, config={"callbacks": callbacks, "recursion_limit": 150})
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
