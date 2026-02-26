---
name: code-analyzer
description: Advanced code analysis skill with perception, reasoning, and planning capabilities. This skill should be used when performing systematic codebase analysis, interpreting user requirements, making informed decisions, and providing actionable insights with probabilistic reasoning capabilities.
---

# Code Analyzer

This skill provides advanced code analysis capabilities with perception, reasoning, and planning features. It systematically analyzes codebases, interprets user requirements, makes informed decisions, and provides actionable insights with uncertainty handling and probabilistic reasoning.

## Capabilities

### Perception and Understanding
- **Read and understand text**: Parse code files, documentation, and specifications
- **Interpret user input**: Translate natural language requirements to actionable analysis tasks
- **Detect system state changes**: Monitor codebase changes, dependencies, and configurations

### Goal Management
- **Clear objectives**: Establish defined analysis goals and success criteria
- **Break big goals into smaller tasks**: Decompose complex analysis into manageable units
- **Track progress**: Monitor completion status and progress metrics

### Decision Making
- **Compare multiple possible actions**: Evaluate different analysis approaches
- **Select best action based on context**: Choose optimal strategies based on current context
- **Handle uncertainty**: Manage ambiguous requirements and incomplete information
- **Use probability when needed**: Apply probabilistic reasoning for assessments

### Planning and Reasoning
- **Predict outcomes**: Antipolate results of potential changes
- **Think ahead**: Consider long-term implications of design decisions
- **Simulate consequences**: Model effects of proposed changes
- **Optimize decisions**: Balance trade-offs between competing objectives

## When to Use This Skill

Use this skill when:
- Performing systematic codebase analysis for security, performance, or quality
- Interpreting complex user requirements for code changes
- Making informed decisions about code architecture or refactoring
- Providing actionable insights with probabilistic reasoning
- Needing to handle uncertainty in code analysis scenarios

## Using the Code Analyzer

### Analysis Process Flow
1. **Perceive**: Use Read and Grep tools to examine relevant code files
2. **Interpret**: Extract specific requirements from user requests
3. **Plan**: Break analysis into smaller, manageable tasks
4. **Execute**: Systematically analyze the codebase using appropriate tools
5. **Evaluate**: Compare findings against objectives and assess quality
6. **Report**: Present findings with actionable recommendations

### Decision Making with Uncertainty
When the skill encounters ambiguous requirements or incomplete information:
- Use the AskUserQuestion tool to clarify requirements
- Apply probabilistic reasoning to assess different approaches
- Provide confidence levels for assessments
- Identify areas requiring additional investigation

### Resource Utilization
- **Scripts**: Execute specialized analysis scripts from the `scripts/` directory
- **References**: Load detailed reference documentation from `references/` when needed
- **Assets**: Use template files from `assets/` for consistent reporting

## Execution Guidelines

### Systematic Analysis Approach
- Start with broad perception of the codebase
- Focus on specific modules or components as needed
- Systematically examine code quality, security, performance, and architecture
- Document findings with specific examples and context

### Reporting Standards
- Provide high-level summary of findings
- Include detailed issues with severity levels
- Offer actionable solutions with implementation guidance
- Assess risks and mitigation strategies
- Estimate effort for implementing recommendations

## Skill Resources

This skill includes specialized resources for different types of analysis:

### scripts/
Analysis utilities for specific codebase tasks (Python/Bash/etc.) that can be run directly to perform particular operations.

**Examples:**
- `static_analysis.py` - Performs static code analysis with configurable rules
- `dependency_checker.py` - Analyzes dependency relationships and vulnerabilities
- `security_scanner.py` - Scans for security vulnerabilities and compliance issues

### references/
Detailed documentation and reference materials intended to be loaded into context to inform the analysis process and decision-making.

**Examples:**
- `code_quality_standards.md` - Comprehensive guide to code quality metrics
- `security_checklist.md` - Detailed security assessment criteria
- `architecture_patterns.md` - Common architectural patterns and anti-patterns
- `best_practices.md` - Industry best practices for various technologies

### assets/
Template files and assets intended for use in output generation, including reports, documentation templates, and boilerplate code.

**Examples:**
- `analysis_report_template.md` - Standard template for analysis reports
- `recommendation_matrix.xlsx` - Template for prioritizing findings
- `security_checklist.pdf` - Printable checklist for security reviews