**AGENTS.md**
================

### Role/Mission

As an autonomous coding agent, our mission is to integrate data from LMArena, Artificial Analysis, and LiveBench into a centralized platform. We will achieve this by utilizing APIs and datasets, with a preference for API-based integrations over HTML scraping. The goal of this project is to provide a scalable and maintainable solution that leverages free resources and makes decisions independently.

### Technical Stack

* Programming Language: Python
* API clients: requests, BeautifulSoup (with Scrapling for HTML parsing)
* Data storage: Pandas, NumPy
* Free API resources: API keys from LMArena, Artificial Analysis, and LiveBench
* Development environment: GitHub Actions

### Requirements

1. **Integration**: Successfully integrate data from LMArena, Artificial Analysis, and LiveBench into a centralized platform.
2. **API-based integration**: Leverage APIs to fetch data, with a preference for API-based integrations over HTML scraping.
3. **Free resources**: Utilize free API resources and avoid paid solutions.
4. **Independent decision-making**: Make decisions independently, without human intervention.
5. **Scalability**: Design the solution to handle increased data volumes and traffic.
6. **Maintainability**: Ensure the solution is easy to understand, modify, and extend.
7. **Robust error handling**: Implement robust error handling mechanisms to handle API rate limits, errors, and other unexpected scenarios.

### File Structure

The following is a suggested file structure for the project:

```markdown
data_source_integration/
|
|-- agents.md (this file)
|-- README.md
|-- requirements.txt
|-- QUESTIONS.md (for questions and assumptions)
|-- src/
|  |
|  |-- lm_arena_agent.py (LMArena API client)
|  |-- artificial_analysis_agent.py (Artificial Analysis API client)
|  |-- livebench_agent.py (LiveBench API client)
|  |-- data_processor.py (data processing module)
|  |-- data_loader.py (data loading module)
|
|-- tests/
|  |
|  |-- test_lm_arena_agent.py
|  |-- test_artificial_analysis_agent.py
|  |-- test_livebench_agent.py
|
|-- .github/workflows/
|  |
|  |-- main.yml (GitHub Actions workflow file)
|
|-- .gitignore
```

### Testing Requirements

Tests will be written using the `unittest` framework in Python. We will use the following test scenarios:

* Test API client functionality (e.g., successful and failed API requests)
* Test data processing and loading mechanisms
* Test the integration of multiple API clients

### Git Protocol

The project will follow standard GitHub pull request and merge protocols. Any changes or updates will be made through pull requests, which will be reviewed and approved by the project maintainers.

### Completion Criteria

The project will be considered complete when the following criteria are met:

* All APIs have been successfully integrated.
* The solution is scalable and maintainable.
* The solution handles errors and unexpected scenarios.
* The project has been deployed to a GitHub Pages site or a similar platform.
* The solutions adheres to free API usage policies.