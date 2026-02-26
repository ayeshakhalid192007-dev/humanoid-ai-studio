# Code Quality Standards Reference

This reference provides the standards and metrics used by the Code Analyzer skill for assessing code quality.

## Quality Metrics

### Maintainability Index
- **Definition**: A composite score that measures how maintainable the code is
- **Formula**: Based on cyclomatic complexity, lines of code, and Halstead volume
- **Target**: Score above 20 is considered maintainable

### Cyclomatic Complexity
- **Definition**: Measure of the number of linearly independent paths through a program's source code
- **Thresholds**:
  - 1-10: Simple, well-structured code
  - 11-20: More complex, but still manageable
  - 21-50: Complex, consider refactoring
  - >50: Very complex, requires immediate refactoring

### Lines of Code (LOC)
- **Function Level**: Aim for functions that are 20-50 lines
- **Class Level**: Aim for classes that are 200-500 lines
- **File Level**: Aim for files that are 500-1000 lines

## Common Code Smells

### Long Method
- **Symptoms**: Methods with more than 20 lines of code
- **Refactoring**: Extract method, decompose conditional

### Large Class
- **Symptoms**: Classes with more than 500 lines or too many responsibilities
- **Refactoring**: Extract class, extract interface

### Long Parameter List
- **Symptoms**: Methods with more than 3-4 parameters
- **Refactoring**: Introduce parameter object, preserve whole object

### Feature Envy
- **Symptoms**: Methods that use data from other classes more than their own
- **Refactoring**: Move method, extract method

## Best Practices

### Naming Conventions
- Use descriptive names for variables, functions, and classes
- Follow language-specific naming conventions (camelCase, snake_case, etc.)
- Avoid abbreviations and single-letter variable names (except for loop counters)

### Documentation Standards
- Document all public APIs
- Include examples in documentation where helpful
- Keep comments up-to-date with code changes

### Error Handling
- Use exceptions appropriately
- Don't ignore caught exceptions
- Provide meaningful error messages

## Static Analysis Rules

### Security Rules
- Check for SQL injection vulnerabilities
- Identify cross-site scripting (XSS) issues
- Flag hardcoded credentials

### Performance Rules
- Identify potential memory leaks
- Detect inefficient algorithms
- Flag unnecessary object creation

### Maintainability Rules
- Flag overly complex methods
- Identify duplicated code blocks
- Detect unused variables and functions