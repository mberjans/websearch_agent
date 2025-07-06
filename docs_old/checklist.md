### **Phase 1: Foundational Architecture & MVP**

#### **Ticket: WSA-101 - Setup Project Structure, Dependency, and Environment Management**

* [x] **WSA-101-01:** Create the root project directory (web_search_agent/).  
* [x] **WSA-101-02:** Create the main source package directory (search_agent/) and the tests directory (tests/).  
* [x] **WSA-101-03:** Inside search_agent/, create sub-package directories: modules/, core/, and utils/.  
* [ ] **WSA-101-04:** Add __init__.py files to search_agent/ and all its sub-packages to define them as Python packages.1  
* [ ] **WSA-101-05:** Initialize the project with poetry init to generate the pyproject.toml file. Poetry is mandated for its robust dependency resolution and reproducible builds via poetry.lock.2  
* [ ] **WSA-101-06:** Populate pyproject.toml with initial project metadata (name, version, description).  
* [ ] **WSA-101-07:** Create a .gitignore file in the root directory.  
* [ ] **WSA-101-08:** Add entries to .gitignore to exclude virtual environment directories (.venv/), Python cache (__pycache__/), environment files (.env), and database files (*.db).

#### **Ticket: WSA-102 - Implement Core Interfaces and Configuration Management**

* [ ] **WSA-102-01:** Create the file search_agent/core/models.py.  
* [ ] **WSA-102-02:** In models.py, define the SearchResult Pydantic model with fields: title (str), url (HttpUrl), and snippet (str).  
* [ ] **WSA-102-03:** In models.py, define the SearchModuleOutput Pydantic model with all specified fields (source_name, query, timestamp_utc, execution_time_seconds, results).  
* [ ] **WSA-102-04:** Create the file search_agent/config.py.  
* [ ] **WSA-102-05:** Implement a Settings class in config.py using Pydantic's BaseSettings to load configuration from environment variables and a .env file.8  
* [ ] **WSA-102-06:** Add initial configuration variables to the Settings class, including placeholders for future API keys and EVALUATION_DB_PATH.  
* [ ] **WSA-102-07:** Create an .env.template file in the root directory to document all required environment variables.  
* [ ] **WSA-102-08:** Create the file search_agent/core/exceptions.py.  
* [ ] **WSA-102-09:** Define custom exception classes inheriting from a base SearchAgentError: ScrapingError, NoResultsError, and ConfigurationError.

#### **Ticket: WSA-103 - Implement Selenium Search Module (MVP)**

* [ ] **WSA-103-01:** Create the file search_agent/modules/selenium_search.py.  
* [ ] **WSA-103-02:** Add selenium, typer, and webdriver-manager as project dependencies using poetry add.  
* [ ] **WSA-103-03:** Implement the core search(query: str) function signature.  
* [ ] **WSA-103-04:** Implement the Typer CLI wrapper function main(query: str) that calls search() and prints the resulting Pydantic model as JSON.13  
* [ ] **WSA-103-05:** Add the if __name__ == "__main__": block to execute the Typer application.  
* [ ] **WSA-103-06:** Configure Selenium's ChromeOptions to run in headless mode using the --headless=new argument.17  
* [ ] **WSA-103-07:** Initialize the WebDriver using webdriver-manager to automate driver management.  
* [ ] **WSA-103-08:** Implement browser automation to navigate to DuckDuckGo with the specified query.23  
* [ ] **WSA-103-09:** Use WebDriverWait and expected_conditions to reliably wait for the search results container to load.  
* [ ] **WSA-103-10:** Implement robust CSS selectors to find and loop through each result element.  
* [ ] **WSA-103-11:** Within the loop, extract the title, url, and snippet for each result.  
* [ ] **WSA-103-12:** Populate the SearchResult and SearchModuleOutput Pydantic models with the scraped data and metadata.  
* [ ] **WSA-103-13:** Wrap all WebDriver operations in a try...finally block to ensure driver.quit() is always called, preventing resource leaks.  
* [ ] **WSA-103-14:** Catch Selenium-specific exceptions (e.g., TimeoutException) and re-raise them as custom application exceptions (e.g., ScrapingError).

#### **Ticket: WSA-104 - Unit Tests for Selenium Search Module**

* [ ] **WSA-104-01:** Create the test file tests/test_selenium_search.py.  
* [ ] **WSA-104-02:** Add pytest and pytest-mock to the development dependencies in pyproject.toml.  
* [ ] **WSA-104-03:** Write a test that uses the mocker fixture to patch the selenium.webdriver.Chrome object.  
* [ ] **WSA-104-04:** Create a sample HTML string that mimics the DuckDuckGo results page structure.  
* [ ] **WSA-104-05:** Configure the mocked driver's find_elements method to return mock web elements based on the sample HTML.  
* [ ] **WSA-104-06:** Write a test to call the search() function and assert that the returned object is a valid SearchModuleOutput instance.  
* [ ] **WSA-104-07:** Assert that the content (titles, URLs) of the parsed results matches the expected data from the mock HTML.  
* [ ] **WSA-104-08:** Write a test where the mocked driver raises a TimeoutException and assert that the search() function correctly catches it and raises a custom ScrapingError.