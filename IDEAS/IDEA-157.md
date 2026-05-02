# AGENTS.md
## Role/Mission
The autonomous coding agent is responsible for implementing source plugins, HTTP cache, and normalization logic for the application. The agent will work independently to design, develop, and test the required features, ensuring they meet the specified requirements. The mission is to create a robust and efficient system that can fetch, parse, and normalize data from various sources, returning a unified schema.

## Technical Stack
The agent will utilize the following technical stack:
- **Scrapling** for web scraping and data extraction
- **httpx** for making HTTP requests and caching
- **numpy** for numerical computations and data manipulation
- **Python** as the primary programming language
- **GitHub Actions** as the CI/CD platform

## Requirements
1. Create source plugins in the `sources` directory, including:
	* `lmarena.py`
	* `artificial_analysis.py`
	* `livebench.py`
2. Implement the following methods in each source plugin:
	* `fetch()`: retrieves data from the source
	* `parse()`: parses the retrieved data into a structured format
	* `to_dataframe()`: converts the parsed data into a Pandas DataFrame
3. Ensure each source plugin returns a unified schema with the following columns:
	* `model`
	* `vendor`
	* `category`
	* `raw_score`
	* `raw_units`
	* `source_name`
	* `source_updated_at`
4. Implement HTTP cache using `httpx` to minimize redundant requests
5. Develop normalization logic to handle inconsistencies in the data

## File Structure
The agent will maintain the following file structure:
```markdown
sources/
|-- lmarena.py
|-- artificial_analysis.py
|-- livebench.py
|-- __init__.py
utils/
|-- http_cache.py
|-- normalization.py
|-- __init__.py
tests/
|-- test_sources.py
|-- test_utils.py
|-- __init__.py
README.md
QUESTIONS.md
AGENTS.md
```
## Testing Requirements
The agent will write unit tests and integration tests to ensure the source plugins, HTTP cache, and normalization logic are working correctly. Tests will be written using the `pytest` framework and will be located in the `tests` directory.

## Git Protocol
The agent will follow the standard GitHub workflow:
- Create a new branch for each feature or bug fix
- Commit changes regularly with descriptive commit messages
- Open a pull request to merge changes into the main branch
- Use GitHub Actions to automate testing and deployment

## Completion Criteria
The agent will consider the task complete when:
- All source plugins are implemented and working correctly
- HTTP cache is functional and reducing redundant requests
- Normalization logic is handling inconsistencies in the data
- All tests are passing and code coverage is satisfactory
- The unified schema is being returned correctly by each source plugin
If any questions or issues arise during development, the agent will document them in `QUESTIONS.md` for future reference.