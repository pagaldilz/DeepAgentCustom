# DeepAgent Custom

This project implements a custom Deep Agent using LangChain, Langfuse, and OpenAI/Anthropic models. It features a Streamlit interface for interacting with the agent.

## Project Structure

- `app.py`: Main Streamlit application entry point.
- `agent_engine.py`: Core logic for setting up and running the Deep Agent.
- `prompts/`: Directory containing agent system prompts.
  - `document_engineer.md`: The system prompt for the Document Engineer agent.
- `deepagents/`: Local package containing backend and graph definitions.
- `.env`: Configuration file for API keys and settings.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd DeepAgentCustom
    ```

2.  **Run automated setup (Windows):**
    Double-click `run_setup.bat` or run it from the terminal:
    ```powershell
    .\run_setup.bat
    ```
    This script will:
    - Create a Python virtual environment (`.venv`) if it doesn't exist.
    - Upgrade `pip`.
    - Install all necessary dependencies from `requirements.txt`.

3.  **Activate the environment:**
    To activate the environment manually for development:
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

4.  **Configuration:**
    Copy `.env.example` to `.env` and fill in your API keys:
    ```bash
    copy .env.example .env
    ```
    Update the values in `.env`:
    - `OPENAI_API_KEY`: Your OpenAI API key.
    - `LANGFUSE_PUBLIC_KEY`: Your Langfuse public key.
    - `LANGFUSE_SECRET_KEY`: Your Langfuse secret key.
    - `LANGFUSE_HOST`: Your Langfuse host (e.g., https://cloud.langfuse.com).

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

Navigate to the URL provided in the terminal (usually `http://localhost:8501`) to interact with the agent.

## Features

### 🤖 Specialized Agent Personas
The system includes over 20 specialized agent roles to handle specific software engineering tasks:

- **Design & Architecture**:
  - `01_code_architect`: Architecture Analysis & Design Patterns
  - `05_api_designer`: REST/GraphQL API Design & OpenAPI Specs
  - `11_database_architect`: Schema Design & Index Optimization
  - `17_greenfield_architect`: New System Architecture Design

- **Security & Compliance**:
  - `02_security_auditor`: Vulnerability Scanning & Threat Modeling
  - `10_dependency_analyst`: Dependency Security & License Auditing
  - `15_compliance_auditor`: SOC2, GDPR, HIPAA Compliance
  - `22_zero_trust_architect`: Zero-Trust Implementation

- **Code Quality & Testing**:
  - `04_testing_engineer`: Unit Test Generation & Coverage Analysis
  - `09_refactoring_expert`: Code Smell Detection & SOLID Improvements
  - `12_code_reviewer`: Deep Code Review & Feedback
  - `21_test_quality_improver`: Test Quality & Robustness

- **Performance & Reliability**:
  - `03_performance_optimizer`: Complexity Analysis & Optimization
  - `16_incident_analyst`: Root Cause Analysis & Post-Mortems
  - `19_performance_campaign`: System-wide Performance Tuning
  - `23_disaster_recovery`: DR Planning & Resilience

- **Migration & DevOps**:
  - `06_devops_engineer`: CI/CD & Infrastructure-as-Code
  - `07_migration_specialist`: Framework Migration & Modernization
  - `14_enterprise_migration`: Large-scale Enterprise Migrations
  - `20_microservices_decomposer`: Monolith Decomposition

- **Documentation**:
  - `08_knowledge_extractor`: Tribal Knowledge Extraction
  - `13_document_engineer`: Comprehensive Implementation Documentation
  - `18_legacy_documenter`: Legacy System Documentation

### ⚙️ Advanced Capabilities

- **Interactive UI**:
  - **Task Planning**: Dedicated "Planning" tab showing the agent's real-time To-Do list.
  - **Graph Visualization**: Live Mermaid.js visualization of the agent's execution graph.
  - **Execution Stream**: Real-time streaming of agent steps and tool outputs.

- **Configuration & Flexibility**:
  - **Model Agnostic**: Compatible with OpenAI and other OpenAI-compatible providers (locally or cloud).
  - **Dynamic Context**: Configurable working directory, output directory, and target documentation language.
  - **Custom Tasks**: Ability to run generic or custom tasks without a predefined persona.

- **Observability & Security**:
  - **Langfuse Integration**: Deep tracing of all agent steps, tool calls, and LLM interactions.
  - **Sandboxed Environment**: Filesystem backend ensures the agent operates safely within the specified working directory.

- **🛡️ Anti-Recursion & Efficiency**:
  - **Resource Monitoring**: Real-time middleware tracks and enforces hard limits on file reads (max 30) and execution steps (max 50) to prevent infinite loops.
  - **Automated Finalization**: Detects when 80% of tasks are complete and automatically triggers the agent to finalize and output results.
  - **Operational Constraints**: Injected system-level directives ensure the agent prioritizes drafting over exhaustive searching when nearing limits.
  - **Heuristic Discovery**: Agent is instructed to use `ls -R` and pattern recognition to avoid redundant directory traversal.
