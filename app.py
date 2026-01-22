import streamlit as st
import os
import asyncio
from dotenv import load_dotenv, set_key
from pathlib import Path
import json
from agent_engine import run_deep_agent
from langfuse.langchain import CallbackHandler

# Load environment variables
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

st.set_page_config(page_title="DeepAgent Document Engineer", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False

# Sidebar Navigation
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", ["Agent Runner", "Configuration", "Traces"])

# Configuration Page
if page == "Configuration":
    st.header("⚙️ Configuration")
    
    with st.form("config_form"):
        api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        base_url = st.text_input("Base URL", value=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"))
        model_name = st.text_input("Model Name", value=os.getenv("OPENAI_MODEL_NAME", "gpt-4o"))
        
        lf_pk = st.text_input("Langfuse Public Key", value=os.getenv("LANGFUSE_PUBLIC_KEY", ""))
        lf_sk = st.text_input("Langfuse Secret Key", value=os.getenv("LANGFUSE_SECRET_KEY", ""), type="password")
        lf_host = st.text_input("Langfuse Host", value=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
        
        st.subheader("Advanced")
        recursion_limit = st.number_input("Recursion Limit", min_value=1, max_value=1000, value=int(os.getenv("RECURSION_LIMIT", 150)), help="Maximum number of steps the agent can take.")

        submitted = st.form_submit_button("Save Configuration")
        
        if submitted:
            # Update .env file
            set_key(env_path, "OPENAI_API_KEY", api_key)
            set_key(env_path, "OPENAI_API_BASE", base_url)
            set_key(env_path, "OPENAI_MODEL_NAME", model_name)
            set_key(env_path, "LANGFUSE_PUBLIC_KEY", lf_pk)
            set_key(env_path, "LANGFUSE_SECRET_KEY", lf_sk)
            set_key(env_path, "LANGFUSE_SECRET_KEY", lf_sk)
            set_key(env_path, "LANGFUSE_HOST", lf_host)
            set_key(env_path, "RECURSION_LIMIT", str(recursion_limit))
            
            # Update session state / env vars immediately
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_API_BASE"] = base_url
            os.environ["OPENAI_MODEL_NAME"] = model_name
            os.environ["LANGFUSE_PUBLIC_KEY"] = lf_pk
            os.environ["LANGFUSE_SECRET_KEY"] = lf_sk
            os.environ["LANGFUSE_HOST"] = lf_host
            os.environ["RECURSION_LIMIT"] = str(recursion_limit)
            
            st.success("Configuration saved and environment updated!")

# Traces Page
elif page == "Traces":
    st.header("🔍 Agent Traces")
    st.markdown("View your agent's execution traces in Langfuse.")
    
    lf_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    st.link_button("Open Langfuse Dashboard", lf_host)
    
    # Could potentially embed an iframe here if desired, but external link is safer.

# Agent Runner Page
elif page == "Agent Runner":
    st.header("🤖 DeepAgent Runner")
    st.markdown("Select a specialized agent role and define your task.")

    # Load Prompts Index
    try:
        prompts_index_path = Path("prompts/prompts_index.json")
        if prompts_index_path.exists():
            with open(prompts_index_path, "r", encoding="utf-8") as f:
                prompts_data = json.load(f)
            
            # Create options list with "Custom Task" as first option
            prompt_options = {"Custom Task (No Predefined Role)": None}
            prompt_options.update({p["label"]: p for p in prompts_data["prompts"]})
            
            # Sidebar selection
            selected_label = st.selectbox("Select Agent Role", list(prompt_options.keys()))
            selected_prompt = prompt_options[selected_label]
            
            # Show description only if a predefined prompt is selected
            if selected_prompt:
                st.info(f"**{selected_prompt['label']}**: {selected_prompt['description']}")
            else:
                st.info("**Custom Task**: Enter your own task below without a predefined role. The agent will use a general-purpose system prompt.")
        else:
            st.error("Prompts index not found!")
            selected_prompt = None
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        selected_prompt = None

    # Task Input
    working_dir_input = st.text_input("Working Directory:", value=os.getcwd(), help="Absolute path to perform the task in.")
    
    # Advanced Options for Prompt Variables
    with st.expander("Advanced Configuration"):
        output_dir_input = st.text_input("Output Directory:", value=os.path.join(os.getcwd(), "docs"), help="Where documentation/artifacts should be saved.")
        doc_language = st.selectbox("Documentation Language:", ["English", "Chinese", "Spanish", "French", "German"])
        
        # Runtime recursion limit override (defaults to env var)
        default_recursion = int(os.getenv("RECURSION_LIMIT", 150))
        recursion_limit_run = st.number_input("Recursion Limit (Runtime)", min_value=1, max_value=2000, value=default_recursion, help="Override the global recursion limit for this run.")

    task_input = st.text_area("Enter your task:", height=100, placeholder="Analyze the current directory and generate specific outputs...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        start_btn = st.button("Kick off Agent", disabled=st.session_state.is_running)
    
    if start_btn:
        if not task_input:
            st.error("Please enter a task.")
        else:
            st.session_state.is_running = True
        
    if st.session_state.is_running and start_btn:
        st.session_state.messages.append({"role": "user", "content": f"**[{selected_label if selected_label else 'Default'}]** {task_input}"})
        
        # Create Tabs
        tab_plan, tab_exec = st.tabs(["Planning", "Execution"])
        
        with tab_exec:
            output_container = st.container()
        
        with tab_plan:
             plan_container = st.container()
        
        async def run_agent_task():
            # Get Config
            api_key = os.getenv("OPENAI_API_KEY")
            base_url = os.getenv("OPENAI_API_BASE")
            model_name = os.getenv("OPENAI_MODEL_NAME")
            
            lf_pk = os.getenv("LANGFUSE_PUBLIC_KEY")
            lf_sk = os.getenv("LANGFUSE_SECRET_KEY")
            lf_host = os.getenv("LANGFUSE_HOST")
            
            # Ensure Langfuse env vars are set for the library to pick them up
            if lf_pk and lf_sk and lf_host:
                os.environ["LANGFUSE_PUBLIC_KEY"] = lf_pk
                os.environ["LANGFUSE_SECRET_KEY"] = lf_sk
                os.environ["LANGFUSE_HOST"] = lf_host
                
                # Initialize global Langfuse client to silence "No Langfuse client..." warnings
                # and ensure any decorator-based tracing works.
                from langfuse import Langfuse
                try:
                    Langfuse()
                except Exception:
                    pass

            # Setup Langfuse Callback
            callbacks = []
            if lf_pk and lf_sk:
                handler = CallbackHandler(public_key=lf_pk)
                callbacks.append(handler)
            
            # Load and Format System Prompt (only if a predefined prompt was selected)
            system_prompt = None
            if selected_prompt:
                try:
                    prompt_file_path = Path("prompts") / selected_prompt["file"]
                    with open(prompt_file_path, "r", encoding="utf-8") as f:
                        raw_prompt = f.read()
                    
                    # Variable Substitution
                    system_prompt = raw_prompt.replace("{working_directory}", working_dir_input)\
                                             .replace("{output_directory}", output_dir_input)\
                                             .replace("{doc_language}", doc_language)
                except Exception as e:
                    st.error(f"Failed to load prompt file: {e}")
                    st.session_state.is_running = False
                    return
            # If selected_prompt is None (Custom Task), system_prompt remains None
            # and agent_engine.py will use its default fallback prompt

            try:
                # Run Agent
                output_placeholder = output_container.empty()
                full_response = ""
                
                with st.spinner(f"Agent ({selected_label}) is planning and executing..."):
                    # Get agent and stream (updated to handle tuple return)
                    agent, event_stream = run_deep_agent(task_input, api_key, base_url, model_name, working_dir_input, callbacks, system_prompt=system_prompt, recursion_limit=recursion_limit_run)

                    # Visualize Graph
                    try:
                        # Draw mermaid png
                        graph_png = agent.get_graph().draw_mermaid_png()
                        st.sidebar.divider()
                        st.sidebar.subheader("🗺️ Agent Graph")
                        st.sidebar.image(graph_png, caption="DeepAgent Workflow")
                    except Exception as e:
                        # Fallback if langgraph/mermaid missing
                        st.sidebar.warning(f"Graph visualization unavailable: {e}")

                    # Debug Configuration
                    show_debug = os.getenv("SHOW_DEBUG_LOGS", "false").lower() == "true"
                    if show_debug:
                        debug_expander = st.expander("Debug: Raw Agent Events", expanded=True)
                    
                    # Status container for current activity
                    status_placeholder = st.empty()

                    async for event in event_stream:
                        # Update status based on event keys
                        active_node = list(event.keys())[0] if event else "Unknown"
                        status_placeholder.caption(f"⚙️ **Active Node:** `{active_node}`")

                        if show_debug:
                            debug_expander.write(event)
                        
                        # Update Todo List in Planning Tab
                        current_todos = []
                        # Check top-level "todos" or inside "values"
                        if "todos" in event:
                             current_todos = event["todos"]
                        elif "values" in event and "todos" in event["values"]:
                             current_todos = event["values"]["todos"]
                        
                        if current_todos:
                            with plan_container:
                                plan_container.empty() # Clear previous
                                s_todos = ""
                                for todo in current_todos:
                                    # Todo format: {'task': '...', 'status': '...'}
                                    # Mapped status: pending=[ ], in_progress=[/], completed=[x]
                                    t_status = todo.get("status", "pending")
                                    # Fallback to 'task' if 'content' missing, but 'content' is the actual schema key
                                    t_task = todo.get("content") or todo.get("task") or "Unknown task"
                                    
                                    icon = "[ ]"
                                    if t_status == "completed":
                                        icon = "[x]"
                                    elif t_status == "in_progress":
                                        icon = "[/]"
                                        
                                    s_todos += f"- {icon} {t_task}\n"
                                
                                plan_container.markdown(s_todos)
                        
                        # Robustly extract messages from event
                        msgs = []
                        if "messages" in event:
                             msgs = event["messages"]
                        elif "values" in event and "messages" in event["values"]:
                             msgs = event["values"]["messages"]
                        else:
                             # Check if any value in the dict has "messages" (Node update)
                             for v in event.values():
                                 if isinstance(v, dict) and "messages" in v:
                                     msgs = v["messages"]
                                     break
                        
                        if msgs and isinstance(msgs, list):
                            last_msg = msgs[-1]
                            
                            # Content Update
                            content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                            
                            # Tool Call Update
                            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                for tc in last_msg.tool_calls:
                                    if tc['name'] == 'write_todos':
                                        st.info("🛠️ **Agent is updating the plan...**")
                                        # Render nicely in Execution tab too
                                        try:
                                            # args might be a dict or string JSON
                                            args = tc['args']
                                            if isinstance(args, str):
                                                args = json.loads(args)
                                            
                                            todos = args.get('todos', [])
                                            s_log = "### 📝 Updated Plan\n"
                                            for t in todos:
                                                status = t.get('status', 'pending')
                                                txt = t.get('content') or t.get('task') or "Unknown task"
                                                icon = "[ ]"
                                                if status == 'completed': icon = "[x]"
                                                elif status == 'in_progress': icon = "[/]"
                                                s_log += f"- {icon} {txt}\n"
                                            st.markdown(s_log)
                                        except:
                                            st.info(f"Args: `{tc['args']}`")
                                    else:
                                        st.info(f"🛠️ Agent is using tool: **{tc['name']}**\n\nArgs: `{tc['args']}`")
                            
                            # Text Update (if not just a tool call or mixed)
                            if content:
                                full_response += f"\n\n{content}"
                                output_placeholder.markdown(full_response)

                st.success("Task execution finished!")
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                st.session_state.is_running = False

        # Run async loop
        asyncio.run(run_agent_task())

    # Display Chat History
    st.divider()
    st.subheader("History")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
