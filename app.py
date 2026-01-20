import streamlit as st
import os
import asyncio
from dotenv import load_dotenv, set_key
from pathlib import Path
from agent_engine import run_document_engineer
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
        
        submitted = st.form_submit_button("Save Configuration")
        
        if submitted:
            # Update .env file
            set_key(env_path, "OPENAI_API_KEY", api_key)
            set_key(env_path, "OPENAI_API_BASE", base_url)
            set_key(env_path, "OPENAI_MODEL_NAME", model_name)
            set_key(env_path, "LANGFUSE_PUBLIC_KEY", lf_pk)
            set_key(env_path, "LANGFUSE_SECRET_KEY", lf_sk)
            set_key(env_path, "LANGFUSE_HOST", lf_host)
            
            # Update session state / env vars immediately
            os.environ["OPENAI_API_KEY"] = api_key
            os.environ["OPENAI_API_BASE"] = base_url
            os.environ["OPENAI_MODEL_NAME"] = model_name
            os.environ["LANGFUSE_PUBLIC_KEY"] = lf_pk
            os.environ["LANGFUSE_SECRET_KEY"] = lf_sk
            os.environ["LANGFUSE_HOST"] = lf_host
            
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
    st.header("🤖 Document Engineer Agent")
    st.markdown("Provide a task to generate documentation for your project.")

    # Task Input
    working_dir_input = st.text_input("Working Directory:", value=os.getcwd(), help="Absolute path to the directory for the agent to work in. Sandboxed to this path.")
    task_input = st.text_area("Enter your task:", height=100, placeholder="Analyze the current directory and generate a README.md...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        start_btn = st.button("Kick off Agent", disabled=st.session_state.is_running)
    
    if start_btn and task_input:
        st.session_state.is_running = True
        st.session_state.messages.append({"role": "user", "content": task_input})
        
        # Container for output
        output_container = st.container()
        
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
            
            try:
                # Run Agent
                output_placeholder = output_container.empty()
                full_response = ""
                
                with st.spinner("Agent is planning and executing..."):
                    # Stream updates
                    debug_expander = st.expander("Debug: Raw Agent Events", expanded=True)
                    

                    async for event in run_document_engineer(task_input, api_key, base_url, model_name, working_dir_input, callbacks):
                        # Log raw event to debug expander
                        debug_expander.write(event)
                        
                        # Robustly extract messages from event
                        # Event can be {"messages": ...} or {"node_name": {"messages": ...}} or {"values": ...}
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
                                    st.info(f"🛠️ Agent is using tool: **{tc['name']}**\n\nArgs: `{tc['args']}`")
                            
                            # Text Update (if not just a tool call or mixed)
                            if content:
                                # Start new markdown block for new message or append?
                                # Simple append approach
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
