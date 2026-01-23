"""Custom middleware for enforcing resource limits and preventing infinite loops."""

from typing import Any
from langchain.agents.middleware.types import AgentMiddleware
from langchain_core.messages import AIMessage


class ResourceLimitMiddleware(AgentMiddleware):
    """Middleware to track and enforce limits on file reads and total steps."""
    
    def __init__(self, max_file_reads: int = 30, max_steps: int = 50):
        """
        Initialize the ResourceLimitMiddleware.
        
        Args:
            max_file_reads: Maximum number of read_file tool calls allowed
            max_steps: Maximum number of agent steps before forcing completion
        """
        self.max_file_reads = max_file_reads
        self.max_steps = max_steps
        self.file_reads = 0
        self.step_count = 0
        self.warned_files = False
        self.warned_steps = False
    
    async def __call__(self, state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """Process state and enforce limits."""
        self.step_count += 1
        
        # Count read_file calls in current state
        messages = state.get("messages", [])
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") == "read_file":
                        self.file_reads += 1
        
        # Enforce step limit (hard stop at max_steps)
        if self.step_count >= self.max_steps:
            if not self.warned_steps:
                print(f"⚠️ HARD LIMIT: Reached {self.max_steps} steps. Forcing agent to complete.")
                self.warned_steps = True
            
            # Inject a strong completion signal
            completion_msg = AIMessage(
                content=f"ANALYSIS COMPLETE: Reached step limit ({self.max_steps}). Outputting final draft based on data gathered so far."
            )
            return {**state, "messages": [*messages, completion_msg]}
        
        # Enforce file read limit (warning at 80%, hard stop at 100%)
        if self.file_reads >= int(self.max_file_reads * 0.8) and not self.warned_files:
            print(f"⚠️ WARNING: {self.file_reads}/{self.max_file_reads} files read. Approaching limit.")
            self.warned_files = True
        
        if self.file_reads >= self.max_file_reads:
            print(f"⚠️ HARD LIMIT: Reached {self.max_file_reads} file reads. Agent should finalize.")
            # Don't force stop here, just warn - let step limit handle it
        
        return state


class TodoCompletionMiddleware(AgentMiddleware):
    """Middleware to detect when todos are mostly complete and force finalization."""
    
    def __init__(self, completion_threshold: float = 0.8):
        """
        Initialize TodoCompletionMiddleware.
        
        Args:
            completion_threshold: Fraction of todos that must be complete to trigger finish (0.0-1.0)
        """
        self.completion_threshold = completion_threshold
        self.completion_triggered = False
    
    async def __call__(self, state: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """Check todo completion status and inject completion signal if needed."""
        todos = state.get("todos", [])
        
        if not todos or self.completion_triggered:
            return state
        
        # Count completed todos
        completed = sum(1 for todo in todos if todo.get("status") == "completed")
        total = len(todos)
        
        if total > 0:
            completion_rate = completed / total
            
            if completion_rate >= self.completion_threshold:
                print(f"✅ TODO THRESHOLD: {completed}/{total} tasks complete ({completion_rate:.0%}). Triggering finalization.")
                self.completion_triggered = True
                
                # Inject completion message
                messages = state.get("messages", [])
                completion_msg = AIMessage(
                    content=f"TODO COMPLETION SIGNAL: {completed}/{total} tasks complete. Generating final output now."
                )
                return {**state, "messages": [*messages, completion_msg]}
        
        return state
