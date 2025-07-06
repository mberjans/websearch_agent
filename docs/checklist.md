### **Phase 1: Foundational Architecture & MVP**

#### **Ticket: WSA-101 \- Setup Project Structure, Dependency, and Environment Management**

* \[x\] **WSA-101-01:** Create the root project directory (web\_search\_agent/).  
* \[x\] **WSA-101-02:** Create the main source package directory (search\_agent/) and the tests directory (tests/).  
* \[x\] **WSA-101-03:** Inside search\_agent/, create sub-package directories: modules/, core/, and utils/.  
* \[x\] **WSA-101-04:** Add \_\_init\_\_.py files to search\_agent/ and all its sub-packages to define them as Python packages.1  
* \[ \] **WSA-101-05:** Initialize the project with poetry init to generate the pyproject.toml file. Poetry is mandated for its robust dependency resolution and reproducible builds via poetry.lock.2  
* \[ \] **WSA-101-06:** Populate pyproject.toml with initial project metadata (name, version, description).  
* \[ \] **WSA-101-07:** Create a .gitignore file in the root directory.  
* \[ \] **WSA-101-08:** Add entries to .gitignore to exclude virtual environment directories (.venv/), Python cache (\_\_pycache\_\_/), environment files (.env), and database files (\*.db).

#### **Ticket: WSA-102 \- Implement Core Interfaces and Configuration Management**

* \[ \] **WSA-102-01:** Create the file search\_agent/core/models.py.  
* \[ \] **WSA-102-02:** In models.py, define the SearchResult Pydantic model with fields: title (str), url (HttpUrl), and snippet (str).  
* \[ \] **WSA-102-03:** In models.py, define the SearchModuleOutput Pydantic model with all specified fields (source\_name, query, timestamp\_utc, execution\_time\_seconds, results).  
* \[ \] **WSA-102-04:** Create the file search\_agent/config.py.  
* \[ \] **WSA-102-05:** Implement a Settings class in config.py using Pydantic's BaseSettings to load configuration from environment variables and a .env file.8  
* \[ \] **WSA-102-06:** Add initial configuration variables to the Settings class, including placeholders for future API keys and EVALUATION\_DB\_PATH.  
* \[ \] **WSA-102-07:** Create an .env.template file in the root directory to document all required environment variables.  
* \[ \] **WSA-102-08:** Create the file search\_agent/core/exceptions.py.  
* \[ \] **WSA-102-09:** Define custom exception classes inheriting from a base SearchAgentError: ScrapingError, NoResultsError, and ConfigurationError.

#### **Ticket: WSA-103 \- Implement Selenium Search Module (MVP)**

* \[ \] **WSA-103-01:** Create the file search\_agent/modules/selenium\_search.py.  
* \[ \] **WSA-103-02:** Add selenium, typer, and webdriver-manager as project dependencies using poetry add.  
* \[ \] **WSA-103-03:** Implement the core search(query: str) function signature.  
* \[ \] **WSA-103-04:** Implement the Typer CLI wrapper function main(query: str) that calls search() and prints the resulting Pydantic model as JSON.13  
* \[ \] **WSA-103-05:** Add the if \_\_name\_\_ \== "\_\_main\_\_": block to execute the Typer application.  
* \[ \] **WSA-103-06:** Configure Selenium's ChromeOptions to run in headless mode using the \--headless=new argument.17  
* \[ \] **WSA-103-07:** Initialize the WebDriver using webdriver-manager to automate driver management.  
* \[ \] **WSA-103-08:** Implement browser automation to navigate to DuckDuckGo with the specified query.23  
* \[ \] **WSA-103-09:** Use WebDriverWait and expected\_conditions to reliably wait for the search results container to load.  
* \[ \] **WSA-103-10:** Implement robust CSS selectors to find and loop through each result element.  
* \[ \] **WSA-103-11:** Within the loop, extract the title, url, and snippet for each result.  
* \[ \] **WSA-103-12:** Populate the SearchResult and SearchModuleOutput Pydantic models with the scraped data and metadata.  
* \[ \] **WSA-103-13:** Wrap all WebDriver operations in a try...finally block to ensure driver.quit() is always called, preventing resource leaks.  
* \[ \] **WSA-103-14:** Catch Selenium-specific exceptions (e.g., TimeoutException) and re-raise them as custom application exceptions (e.g., ScrapingError).

#### **Ticket: WSA-104 \- Unit Tests for Selenium Search Module**

* \[ \] **WSA-104-01:** Create the test file tests/test\_selenium\_search.py.  
* \[ \] **WSA-104-02:** Add pytest and pytest-mock to the development dependencies in pyproject.toml.  
* \[ \] **WSA-104-03:** Write a test that uses the mocker fixture to patch the selenium.webdriver.Chrome object.  
* \[ \] **WSA-104-04:** Create a sample HTML string that mimics the DuckDuckGo results page structure.  
* \[ \] **WSA-104-05:** Configure the mocked driver's find\_elements method to return mock web elements based on the sample HTML.  
* \[ \] **WSA-104-06:** Write a test to call the search() function and assert that the returned object is a valid SearchModuleOutput instance.  
* \[ \] **WSA-104-07:** Assert that the content (titles, URLs) of the parsed results matches the expected data from the mock HTML.  
* \[ \] **WSA-104-08:** Write a test where the mocked driver raises a TimeoutException and assert that the search() function correctly catches it and raises a custom ScrapingError.

### **Phase 2: Architectural Validation**

#### **Ticket: WSA-201 \- Implement Playwright Search Module**

* \[ \] **WSA-201-01:** Add playwright to project dependencies using poetry add playwright.  
* \[ \] **WSA-201-02:** Run playwright install to download the required browser binaries.  
* \[ \] **WSA-201-03:** Create the file search\_agent/modules/playwright\_search.py.  
* \[ \] **WSA-201-04:** Implement the core search function with an async def search(query: str) signature, leveraging Playwright's native async capabilities.29  
* \[ \] **WSA-201-05:** Implement the Typer CLI wrapper, using asyncio.run() to call the async search function.  
* \[ \] **WSA-201-06:** Use Playwright's async context manager (async with async\_playwright() as p:) to manage browser instances.  
* \[ \] **WSA-201-07:** Implement navigation, query input, and data extraction using await page.goto(), await page.locator(), etc.  
* \[ \] **WSA-201-08:** Ensure the function returns a validated SearchModuleOutput object, adhering to the standard interface.

#### **Ticket: WSA-202 \- Unit Tests for Playwright Search Module**

* \[ \] **WSA-202-01:** Create the test file tests/test\_playwright\_search.py.  
* \[ \] **WSA-202-02:** Add pytest-asyncio to development dependencies.  
* \[ \] **WSA-202-03:** Write test functions as async def and decorate them with @pytest.mark.asyncio.  
* \[ \] **WSA-202-04:** Use mocking to patch Playwright's page object and its methods (goto, locator, inner\_text, etc.).  
* \[ \] **WSA-202-05:** Create a mock HTML response and configure the patched methods to return it.  
* \[ \] **WSA-202-06:** Call the search() function and assert that the parsed data in the final JSON output is correct.

### **Phase 3: The Quantitative Evaluator Module**

#### **Ticket: WSA-301 \- Implement Speed Evaluation Logic**

* \[ \] **WSA-301-01:** Create the file search\_agent/evaluator.py.  
* \[ \] **WSA-301-02:** Implement a function measure\_speed(module\_name: str, query: str).  
* \[ \] **WSA-301-03:** Use importlib.import\_module() to dynamically load the specified search module.  
* \[ \] **WSA-301-04:** Use time.perf\_counter() to record the start and end times around the module's search() call for high-precision benchmarking.35  
* \[ \] **WSA-301-05:** Calculate and return the total execution time in seconds.

#### **Ticket: WSA-302 \- Implement LLM-Based Quality Evaluation**

* \[ \] **WSA-302-01:** Add the openai library (or other required LLM client) to dependencies.  
* \[ \] **WSA-302-02:** Implement a function evaluate\_quality\_llm(search\_output: SearchModuleOutput).  
* \[ \] **WSA-302-03:** Securely retrieve the necessary API key from the settings object in config.py.40  
* \[ \] **WSA-302-04:** Engineer a clear, specific, zero-shot prompt that defines the task (rate relevance), the scale (1-10), and the required output format (a single integer) to ensure structured responses.44  
* \[ \] **WSA-302-05:** Call the LLM API with the engineered prompt and search results.  
* \[ \] **WSA-302-06:** Parse the integer score from the LLM's response and implement robust error handling for API or parsing failures.

#### **Ticket: WSA-303 \- Implement NLP-Based Quality Evaluation**

* \[ \] **WSA-303-01:** Add the spacy library to dependencies.  
* \[ \] **WSA-303-02:** Document the command to download a spaCy model with word vectors (e.g., python \-m spacy download en\_core\_web\_md).  
* \[ \] **WSA-303-03:** Implement a function evaluate\_quality\_nlp(search\_output: SearchModuleOutput).  
* \[ \] **WSA-303-04:** Load the spaCy model.  
* \[ \] **WSA-303-05:** Generate Doc objects for the query and the concatenated result snippets.  
* \[ \] **WSA-303-06:** Calculate the cosine similarity between the two Doc objects using the .similarity() method.49  
* \[ \] **WSA-303-07:** Return the resulting similarity score (a float between 0 and 1).

#### **Ticket: WSA-304 \- Implement SQLite Logging for Evaluation Results**

* \[ \] **WSA-304-01:** In evaluator.py, implement a setup\_database() function.  
* \[ \] **WSA-304-02:** Use Python's built-in sqlite3 module to connect to the database file path specified in config.py.54  
* \[ \] **WSA-304-03:** The setup\_database() function should execute a CREATE TABLE IF NOT EXISTS statement matching the schema in the development plan.  
* \[ \] **WSA-304-04:** Implement a log\_evaluation() function that takes all evaluation metrics as parameters.  
* \[ \] **WSA-304-05:** Use an INSERT statement with ? placeholders to safely insert a new record into the evaluation log table.  
* \[ \] **WSA-304-06:** Ensure the database connection is properly committed and closed after the insert operation.

### **Phase 4: The Central Orchestrator**

#### **Ticket: WSA-401 \- Implement Concurrent Module Execution**

* \[ \] **WSA-401-01:** Create the file search\_agent/orchestrator.py.  
* \[ \] **WSA-401-02:** Implement the main async def run\_orchestration(query: str) function.  
* \[ \] **WSA-401-03:** Import all available search modules.  
* \[ \] **WSA-401-04:** Create a list of awaitable tasks. For synchronous modules like Selenium, wrap the function call with asyncio.to\_thread() to prevent blocking the event loop.  
* \[ \] **WSA-401-05:** Execute all tasks concurrently using await asyncio.gather(\*tasks, return\_exceptions=True). Using asyncio is the correct approach for I/O-bound tasks like network requests.36  
* \[ \] **WSA-401-06:** Process the results from gather, separating successfully completed tasks from those that raised exceptions.  
* \[ \] **WSA-401-07:** Implement logging for any exceptions captured during module execution.

#### **Ticket: WSA-402 \- Implement Result Merging and De-duplication**

* \[ \] **WSA-402-01:** Implement a function merge\_and\_deduplicate(module\_outputs: list).  
* \[ \] **WSA-402-02:** Initialize an empty dictionary, unique\_results \= {}, to store unique results.  
* \[ \] **WSA-402-03:** Iterate through the results from all successful module runs.  
* \[ \] **WSA-402-04:** For each search result, normalize its URL (e.g., convert to lowercase, remove trailing slashes) to use as a key.  
* \[ \] **WSA-402-05:** If the normalized URL is not already a key in unique\_results, add the result object to the dictionary. This method efficiently removes duplicates while preserving the first-seen instance.65  
* \[ \] **WSA-402-06:** Return list(unique\_results.values()) to provide the final de-duplicated list.

#### **Ticket: WSA-403 \- Implement Initial Re-ranking Strategy**

* \[ \] **WSA-403-01:** Implement a function rerank\_results(results: list).  
* \[ \] **WSA-403-02:** Define a source priority mapping (e.g., a dictionary where API sources have a higher priority value than scraped sources).  
* \[ \] **WSA-403-03:** Use Python's sorted() function with a key lambda that looks up the result's source priority in the mapping.  
* \[ \] **WSA-403-04:** Ensure the function is designed to be pluggable, allowing for future replacement with more advanced algorithms like Cross-Encoders or MMR.67

### **Phase 5: Integration of API-Based Search Modules**

#### **Ticket: WSA-501 \- Implement Brave Search API Module**

* \[ \] **WSA-501-01:** Create the file search\_agent/modules/brave\_api\_search.py.  
* \[ \] **WSA-501-02:** Add a suitable HTTP client like httpx or the official brave-search library to dependencies.73  
* \[ \] **WSA-501-03:** Implement an async def search(query: str) function.  
* \[ \] **WSA-501-04:** Retrieve the BRAVE\_API\_KEY from the central config.py settings object.  
* \[ \] **WSA-501-05:** Use an async HTTP client to make a GET request to the Brave Search API endpoint, passing the API key in the headers.  
* \[ \] **WSA-501-06:** Parse the JSON response and map the relevant fields to the SearchModuleOutput Pydantic model.  
* \[ \] **WSA-501-07:** Implement the standard dual-mode Typer CLI wrapper.

#### **Ticket: WSA-502 \- Implement Google Custom Search API Module**

* \[ \] **WSA-502-01:** Create the file search\_agent/modules/google\_cse\_search.py.  
* \[ \] **WSA-502-02:** Add the google-api-python-client library to dependencies.78  
* \[ \] **WSA-502-03:** Implement an async def search(query: str) function. If the client library is synchronous, wrap the execution logic with asyncio.to\_thread().  
* \[ \] **WSA-502-04:** Retrieve GOOGLE\_API\_KEY and GOOGLE\_CSE\_ID from the central config.py settings.  
* \[ \] **WSA-502-05:** Use the Google API client library to build and execute the search request.  
* \[ \] **WSA-502-06:** Parse the JSON response and map the fields to the SearchModuleOutput model.  
* \[ \] **WSA-502-07:** Implement the standard dual-mode Typer CLI wrapper.

### **Phase 6: Expansion with Specialized Python Libraries**

#### **Ticket: WSA-601 \- Implement httpx \+ BeautifulSoup Search Module**

* \[ \] **WSA-601-01:** Create the file search\_agent/modules/httpx\_search.py.  
* \[ \] **WSA-601-02:** Add httpx and beautifulsoup4 to project dependencies. httpx is chosen for its high performance and native async support, making it superior to requests for this use case.80  
* \[ \] **WSA-601-03:** Implement an async def search(query: str) function.  
* \[ \] **WSA-601-04:** Use an httpx.AsyncClient to perform an async GET request to a target search engine with simple HTML.  
* \[ \] **WSA-601-05:** Use BeautifulSoup to parse the HTML content from the response.  
* \[ \] **WSA-601-06:** Implement CSS selectors to extract title, URL, and snippet from the parsed HTML.  
* \[ \] **WSA-601-07:** Map the extracted data to the standard SearchModuleOutput model.  
* \[ \] **WSA-601-08:** Implement the standard dual-mode Typer CLI wrapper.

#### **Ticket: WSA-602 \- Implement Scrapy Search Module**

* \[ \] **WSA-602-01:** Create the file search\_agent/modules/scrapy\_search.py.  
* \[ \] **WSA-602-02:** Add scrapy to project dependencies.  
* \[ \] **WSA-602-03:** Define a Scrapy Spider class within the module, configured to accept a query.  
* \[ \] **WSA-602-04:** Implement the spider's parse method to extract result data and yield each result as a dictionary.  
* \[ \] **WSA-602-05:** Implement the main search(query: str) function to programmatically configure and run the Scrapy spider using CrawlerProcess.  
* \[ \] **WSA-602-06:** Capture the items yielded by the spider and format the collected data into the standard SearchModuleOutput model.  
* \[ \] **WSA-602-07:** Implement the standard dual-mode Typer CLI wrapper. This integration is more complex as Scrapy is a full framework, not just a library.84