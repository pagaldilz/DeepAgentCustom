# DeepAgent Prompt Library

A collection of 23 specialized prompts designed to leverage DeepAgent's full capabilities for various software engineering tasks.

## 📋 Available Prompts (23 Total)

### Core Prompts (01-13)
| # | Prompt | Category | Description |
|---|--------|----------|-------------|
| 01 | [🏗️ Architecture Analysis](./01_code_architect.md) | Design | System design and architecture documentation |
| 02 | [🔒 Security Audit](./02_security_auditor.md) | Security | Vulnerability scanning and threat modeling |
| 03 | [⚡ Performance Optimization](./03_performance_optimizer.md) | Performance | Bottleneck analysis and optimization |
| 04 | [🧪 Test Generation](./04_testing_engineer.md) | Testing | Test coverage and test generation |
| 05 | [🔌 API Design](./05_api_designer.md) | Design | REST/GraphQL API design and OpenAPI specs |
| 06 | [🚀 DevOps Setup](./06_devops_engineer.md) | Infrastructure | CI/CD pipelines and containerization |
| 07 | [🔄 Code Migration](./07_migration_specialist.md) | Migration | Legacy modernization and upgrades |
| 08 | [🧠 Knowledge Extraction](./08_knowledge_extractor.md) | Documentation | Tribal knowledge and onboarding docs |
| 09 | [🔧 Refactoring Analysis](./09_refactoring_expert.md) | Quality | Code smells and SOLID analysis |
| 10 | [📦 Dependency Analysis](./10_dependency_analyst.md) | Security | Package security and upgrades |
| 11 | [🗄️ Database Design](./11_database_architect.md) | Design | Schema design and optimization |
| 12 | [👀 Code Review](./12_code_reviewer.md) | Quality | Thorough code review and feedback |
| 13 | [📝 Documentation Generator](./13_document_engineer.md) | Documentation | Comprehensive technical documentation |

### Advanced Use Cases (14-23)
| # | Prompt | Category | Description |
|---|--------|----------|-------------|
| 14 | [🏢 Enterprise Migration](./14_enterprise_migration.md) | Enterprise | Large-scale codebase migration (Python 2→3, framework upgrades) |
| 15 | [�️ Compliance Audit](./15_compliance_auditor.md) | Compliance | SOC2, GDPR, HIPAA compliance audits |
| 16 | [🔍 Incident Analysis](./16_incident_analyst.md) | Incident Response | Root cause analysis and post-mortem documentation |
| 17 | [🌱 Greenfield Architecture](./17_greenfield_architect.md) | Design | Design new systems from scratch |
| 18 | [📚 Legacy Documentation](./18_legacy_documenter.md) | Documentation | Document undocumented legacy systems |
| 19 | [📊 Performance Campaign](./19_performance_campaign.md) | Performance | Systematic performance optimization campaigns |
| 20 | [🔀 Microservices Decomposition](./20_microservices_decomposer.md) | Migration | Break monoliths into microservices (strangler pattern) |
| 21 | [✅ Test Quality Improvement](./21_test_quality_improver.md) | Testing | Increase test coverage with quality tests |
| 22 | [🔐 Zero-Trust Security](./22_zero_trust_architect.md) | Security | Zero-trust architecture with mTLS and policy enforcement |
| 23 | [🌐 Disaster Recovery](./23_disaster_recovery.md) | Reliability | Multi-region DR with aggressive RTO/RPO targets |

## �️ Categories

The prompts are organized into 12 categories:

- **🏗️ Design & Architecture** - System architecture, API design, database design
- **🔒 Security & Hardening** - Security audits, vulnerability scanning, zero-trust
- **🛡️ Compliance & Governance** - SOC2, GDPR, HIPAA compliance auditing
- **⚡ Performance** - Performance optimization and profiling
- **🧪 Testing & QA** - Test generation, coverage improvement, quality testing
- **🚀 DevOps & Infrastructure** - CI/CD, containerization, infrastructure-as-code
- **🔄 Migration & Modernization** - Legacy modernization, microservices decomposition
- **🏢 Enterprise & Scale** - Large-scale enterprise migrations and transformations
- **📝 Documentation** - Technical documentation, knowledge extraction
- **✨ Code Quality** - Refactoring, code review, quality improvement
- **🔍 Incident Response** - Root cause analysis, post-mortems
- **🌐 Reliability & DR** - Disaster recovery, high availability

## 🔧 Dynamic Variables

All prompts support these dynamic variables that should be replaced before use:

| Variable | Description | Example |
|----------|-------------|---------|
| `{working_directory}` | Project root path | `H:\\Projects\\MyApp` |
| `{output_directory}` | Documentation output path | `H:\\Projects\\MyApp\\docs` |
| `{doc_language}` | Output language | `English`, `Chinese` |

## 📂 Frontend Integration

Use `prompts_index.json` to populate dropdown menus:

```javascript
// Load prompts index
const promptsIndex = await fetch('/prompts/prompts_index.json').then(r => r.json());

// Populate dropdown
promptsIndex.prompts.forEach(prompt => {
  dropdown.addOption(prompt.id, prompt.label, prompt.description);
});

// Load selected prompt
async function loadPrompt(promptId) {
  const prompt = promptsIndex.prompts.find(p => p.id === promptId);
  const content = await fetch(`/prompts/${prompt.file}`).then(r => r.text());
  
  // Replace variables
  return content
    .replace(/{working_directory}/g, workingDir)
    .replace(/{output_directory}/g, outputDir)
    .replace(/{doc_language}/g, language);
}
```

## 🎯 Prompt Design Principles

Each prompt follows these principles:

1. **Explicit Tool Instructions** - Clear guidance on DeepAgent tools
2. **Multi-Phase Workflow** - Structured phases (Discovery → Analysis → Output)
3. **Mermaid Diagrams** - Visual documentation in every output
4. **Subagent Delegation** - Use specialized subagents for complex tasks
5. **Quality Constraints** - Accuracy requirements and evidence-based conclusions
6. **Self-Check Checklists** - Built-in quality assurance

## 📁 File Structure

All prompts are numbered (01-23) for better organization as the library grows:

```
prompts/
├── README.md                       # This file
├── prompts_index.json              # Machine-readable index (v2.0.0)
│
├── 01_code_architect.md            # Architecture analysis
├── 02_security_auditor.md          # Security audit
├── 03_performance_optimizer.md     # Performance optimization
├── 04_testing_engineer.md          # Test generation
├── 05_api_designer.md              # API design
├── 06_devops_engineer.md           # DevOps & infrastructure
├── 07_migration_specialist.md      # Code migration
├── 08_knowledge_extractor.md       # Knowledge extraction
├── 09_refactoring_expert.md        # Refactoring analysis
├── 10_dependency_analyst.md        # Dependency analysis
├── 11_database_architect.md        # Database design
├── 12_code_reviewer.md             # Code review
├── 13_document_engineer.md         # Documentation generator
├── 14_enterprise_migration.md      # Enterprise migration
├── 15_compliance_auditor.md        # Compliance audit
├── 16_incident_analyst.md          # Incident analysis
├── 17_greenfield_architect.md      # Greenfield architecture
├── 18_legacy_documenter.md         # Legacy documentation
├── 19_performance_campaign.md      # Performance campaign
├── 20_microservices_decomposer.md  # Microservices decomposition
├── 21_test_quality_improver.md     # Test quality improvement
├── 22_zero_trust_architect.md      # Zero-trust security
└── 23_disaster_recovery.md         # Disaster recovery
```

## 🚀 Usage

1. Select a prompt from the dropdown in the UI
2. The prompt is loaded with your configured variables
3. Enter your specific task requirements
4. DeepAgent executes the specialized workflow
5. Review generated documentation in the output directory

## 💡 Numbering Convention

Prompts are numbered 01-23 for:
- **Easy Reference** - Quickly refer to prompts by number
- **Stable Ordering** - Consistent ordering as library grows
- **Future Expansion** - Room for insertions between numbers if needed

New prompts will continue the sequence (24, 25, etc.).
