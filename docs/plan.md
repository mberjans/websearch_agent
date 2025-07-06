

# **A Phased Development Plan for a Modular Web Search Agent System**

### **Executive Summary**

This document outlines a comprehensive, phased development plan for a high-performance, modular, and extensible web search agent system. The primary objective is to create a sophisticated platform capable of aggregating search results from a diverse set of sources, including direct web scraping via browser automation and programmatic queries to commercial search APIs. The architecture is founded on four core principles: **Modularity**, ensuring each search method is an independent and interchangeable component; **Dual-Mode Operation**, allowing each module to function as both a standalone command-line tool and an importable library function; **Standardized I/O**, enforcing a consistent JSON data format for seamless interoperability; and **Headless Operation**, guaranteeing compatibility with server-side, non-GUI environments.

The development roadmap is structured into six distinct phases. The initial phases focus on establishing a robust architectural foundation with the implementation of two browser-based scraping modules (Selenium and Playwright). Subsequent phases introduce a sophisticated evaluation module for quantitative analysis of speed and quality, followed by a central orchestrator responsible for concurrent module execution, result aggregation, and intelligent re-ranking. The system's capabilities are then expanded by integrating fast, reliable commercial search APIs (e.g., Brave, Google) and other specialized Python libraries (e.g., Scrapy, httpx).

The final deliverable will be a powerful and versatile search aggregation system. Its data-driven design, facilitated by the evaluator and orchestrator, allows for dynamic, performance-aware selection of the optimal search tool for any given query. This plan provides an actionable blueprint for an engineering team to construct a system that is not only powerful upon completion but also maintainable, scalable, and adaptable to future technological advancements in web data retrieval.

## **Section 1: Foundational Architecture and Project Scaffolding**

The initial stage of any robust software project is the establishment of a solid architectural foundation. The decisions made in this phase are critical, as they dictate the project's long-term maintainability, scalability, and ease of development. This section details the blueprint for the project structure, dependency management strategy, configuration handling, and the core interfaces that will ensure seamless interoperability between all system components.

### **1.1. Scalable Project Structure: The Blueprint for Modularity**

A well-organized project structure is paramount for simplifying development, enhancing maintainability, and facilitating team collaboration.1 The proposed structure explicitly separates application logic, tests, configuration, and documentation, adhering to established Python community best practices.2

The project will be organized using a "src layout," where the main application code resides within a dedicated package directory (search\_agent/). This approach prevents a range of common import and packaging problems and ensures that tests are executed against the installable package, thereby simulating a more realistic usage scenario.5 The

modules/ sub-package is the designated home for all search agents, providing a clear and isolated namespace for each implementation and directly realizing the core principle of modularity.3 The inclusion of

\_\_init\_\_.py files in each directory formally designates them as Python packages, enabling a clean, hierarchical import system that avoids namespace conflicts.3

The proposed directory layout is as follows:

web\_search\_agent/  
├──.git/  
├──.venv/ or.poetry/  
├── search\_agent/  
│   ├── \_\_init\_\_.py  
│   ├── modules/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── selenium\_search.py  
│   │   └──... (other modules will be added here)  
│   ├── utils/  
│   │   ├── \_\_init\_\_.py  
│   │   └── parsers.py  
│   ├── core/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── models.py         \# Pydantic models for I/O schema  
│   │   └── exceptions.py     \# Custom exception classes  
│   ├── evaluator.py  
│   ├── orchestrator.py  
│   └── config.py  
├── tests/  
│   ├── \_\_init\_\_.py  
│   ├── test\_selenium\_search.py  
│   └──... (tests mirroring the search\_agent structure)  
├── docs/  
├──.env  
├──.gitignore  
├── pyproject.toml  
└── README.md

This structure provides clear separation of concerns, making the codebase easier to navigate and maintain as it grows.2

### **1.2. Dependency and Environment Management: Choosing Poetry for Reproducibility**

Traditional dependency management using pip and a requirements.txt file, while simple, is often insufficient for complex projects. It can lead to inconsistent environments and challenging dependency conflicts, a situation commonly referred to as "dependency hell".7 The linear, one-by-one installation process of

pip can result in incompatible sub-dependencies being installed, breaking previously installed packages.7

To mitigate these risks and ensure robust, reproducible builds, this project will mandate the use of **Poetry**. Poetry is a modern, all-in-one tool that handles dependency management, virtual environment creation, and packaging.8 Its adoption brings several key advantages:

* **Deterministic Dependency Resolution:** Before installing any packages, Poetry analyzes the entire dependency graph to find a single, compatible set of versions for all direct and transitive dependencies. This preemptively resolves conflicts that pip might miss.8  
* **Standardized pyproject.toml:** Project metadata, main dependencies, and development-only dependencies (e.g., pytest, black) are all defined in a single, standardized pyproject.toml file. This replaces the scattered collection of requirements.txt, dev-requirements.txt, setup.py, and other configuration files.7  
* **Guaranteed Reproducibility with poetry.lock:** Poetry automatically generates a poetry.lock file that records the exact versions of every package and sub-package installed. Committing this file to version control guarantees that every developer, as well as the CI/CD pipeline, will build the exact same environment, eliminating "works on my machine" issues.8  
* **Integrated Virtual Environments:** The developer workflow is simplified as Poetry automatically creates and manages a dedicated virtual environment for the project, isolating its dependencies from the global system or other projects.9

The pyproject.toml file will serve as the single source of truth for all project dependencies, ensuring a clean, manageable, and highly reproducible development lifecycle.

### **1.3. Secure Configuration Strategy: Pydantic and Environment Variables**

Hardcoding configuration values such as API keys, database credentials, or LLM endpoints directly into the application code is a severe security vulnerability and makes the application rigid and difficult to deploy across different environments (e.g., development, testing, production).10

The architectural solution is a centralized configuration management system using Pydantic's BaseSettings in conjunction with environment variables. This approach involves a single config.py module that loads configuration settings from the environment, which can be conveniently populated from a local .env file during development.12

The implementation in search\_agent/config.py will be as follows:

Python

from pydantic\_settings import BaseSettings, SettingsConfigDict  
from pydantic import SecretStr, HttpUrl  
from typing import Optional

class Settings(BaseSettings):  
    """  
    Centralized application configuration.  
    Settings are loaded from environment variables or a.env file.  
    """  
    \# API Keys and Secrets  
    BRAVE\_API\_KEY: Optional \= None  
    GOOGLE\_API\_KEY: Optional \= None  
    OPENAI\_API\_KEY: Optional \= None  
    ANTHROPIC\_API\_KEY: Optional \= None

    \# Google Custom Search Engine  
    GOOGLE\_CSE\_ID: Optional\[str\] \= None

    \# Evaluator Database  
    EVALUATION\_DB\_PATH: str \= "evaluation\_log.db"

    \# LLM Configuration  
    LLM\_EVALUATOR\_MODEL: str \= "gpt-4o-mini"  
    LLM\_EVALUATOR\_ENDPOINT: Optional\[HttpUrl\] \= None

    model\_config \= SettingsConfigDict(  
        env\_file='.env',   
        env\_file\_encoding='utf-8',  
        case\_sensitive=False  
    )

\# Instantiate a single settings object for the entire application  
settings \= Settings()

This pattern provides a single, type-safe configuration object (settings) that is available throughout the application.12 Pydantic automatically validates the types of the loaded environment variables, raising an error early if a value is incorrect. The use of the

SecretStr type is a critical security feature; it prevents sensitive values like API keys from being accidentally exposed in logs, error tracebacks, or even standard print() statements.12 The

.env file, which contains the actual secrets for local development, will be explicitly excluded from version control via the .gitignore file, preventing accidental commits of sensitive credentials.10

### **1.4. Core System Interfaces: The Contracts for Interoperability**

To achieve true modularity and extensibility, the system must be built upon a set of well-defined "contracts" or interfaces. These interfaces ensure that different components can communicate and interact with each other without needing to know about their internal implementations. This promotes low coupling, a key principle of robust software design.2

#### **1.4.1. The Standardized JSON I/O Schema**

Every search module, whether it uses a browser, an API, or any other method, must produce output in a consistent and predictable format. This allows the Orchestrator and Evaluator to consume results from any source without requiring custom parsing logic for each one.

To enforce this standard, the output schema will be defined using a Pydantic model in search\_agent/core/models.py. Pydantic provides not only a single source of truth for the data structure but also runtime data validation, ensuring that all modules adhere to the contract.

Python

\# in search\_agent/core/models.py  
from pydantic import BaseModel, Field, HttpUrl  
from datetime import datetime  
from typing import List

class SearchResult(BaseModel):  
    """Represents a single search result item."""  
    title: str \= Field(..., description="The title of the search result.")  
    url: HttpUrl \= Field(..., description="The URL of the search result.")  
    snippet: str \= Field(..., description="A descriptive snippet of the result content.")

class SearchModuleOutput(BaseModel):  
    """Defines the standardized output structure for all search modules."""  
    source\_name: str \= Field(..., description="The name of the module that generated the result (e.g., 'selenium\_search').")  
    query: str \= Field(..., description="The original search query.")  
    timestamp\_utc: datetime \= Field(..., description="The UTC timestamp of when the search was completed.")  
    execution\_time\_seconds: float \= Field(..., description="The total execution time for the search module in seconds.")  
    results: List \= Field(..., description="A list of search result items.")

#### **1.4.2. The Dual-Mode (CLI/Library) Module Pattern**

A core requirement is that each search module must be executable as a standalone command-line tool (e.g., python selenium\_search.py \--query "...") and also be importable as a standard Python function (e.g., from modules.selenium\_search import search).

The selection of the **Typer** library is a deliberate architectural decision to enforce this pattern elegantly and efficiently. Typer, which is built upon the powerful Click library, uses Python type hints to create modern, self-documenting CLIs with minimal boilerplate code.14 Its decorator-based approach is superior to the standard library's

argparse for this specific use case because it allows a single, standard Python function to serve as the entry point for both library and CLI usage.17 This structurally binds the CLI to the library function, adhering to the DRY (Don't Repeat Yourself) principle and significantly reducing the surface area for bugs and testing. Unit tests written for the core

search() function provide high confidence that the CLI wrapper will behave identically, a major win for long-term maintainability.

The implementation pattern for every module will be as follows:

Python

\# Example pattern in a module like selenium\_search.py  
import typer  
import json  
import time  
from datetime import datetime, timezone  
from search\_agent.core.models import SearchModuleOutput, SearchResult  
\#... other necessary imports

\# The Typer app instance  
app \= typer.Typer()

def search(query: str) \-\> SearchModuleOutput:  
    """  
    The core library function that performs the search.  
    This function contains the main logic and is what other parts of the system will import and call.  
    """  
    start\_time \= time.perf\_counter()  
      
    \# \--- Main search and scraping logic goes here \---  
    \# Example placeholder for scraped results  
    scraped\_results \=  
    \# \--- End of main logic \---  
      
    end\_time \= time.perf\_counter()  
    execution\_time \= end\_time \- start\_time  
      
    return SearchModuleOutput(  
        source\_name="selenium\_search", \# This would be dynamic or hardcoded per module  
        query=query,  
        timestamp\_utc=datetime.now(timezone.utc),  
        execution\_time\_seconds=execution\_time,  
        results=scraped\_results  
    )

@app.command()  
def main(  
    query: str \= typer.Option(  
       ...,   
        "--query",   
        "-q",   
        help\="The search query to execute."  
    )  
):  
    """  
    The CLI entry point. This function is a thin wrapper around the core \`search\` function.  
    It handles CLI argument parsing and prints the standardized JSON output.  
    """  
    result\_obj \= search(query)  
    \# Pydantic's model\_dump\_json method ensures standardized, validated JSON output.  
    print(result\_obj.model\_dump\_json(indent=2))

if \_\_name\_\_ \== "\_\_main\_\_":  
    \# This block makes the script executable from the command line.  
    app()

This pattern ensures that all modules are consistent, reusable, and independently testable, forming the bedrock of the system's modular architecture.

## **Section 2: Phase 1 \- Minimal Viable Product: The Selenium-Based Search Module**

### **2.1. Objectives, Key Tasks, and Deliverables**

* **Objective:** The primary goal of Phase 1 is to deliver a single, fully functional, end-to-end search module using the Selenium library. This phase serves as the proof-of-concept for the entire foundational architecture, validating the project structure, the dual-mode execution pattern, and the standardized I/O schema. Successful completion of this phase will result in the first tangible component of the system.  
* **Key Tasks:**  
  1. **Project Setup:** Implement the complete directory structure as defined in Section 1.1.  
  2. **Environment Initialization:** Initialize the project using poetry init and add the initial set of dependencies: selenium, typer, pydantic, and python-dotenv.  
  3. **Module Development:** Create the selenium\_search.py file within the search\_agent/modules/ directory, adhering strictly to the dual-mode pattern established in Section 1.4.2.  
  4. **Headless Browser Logic:** Implement the logic to configure and launch a headless web browser (Chrome or Firefox) using Selenium's Options class. This is a non-negotiable requirement for server-side operation.19 The  
     \--headless=new argument is the current standard for Chrome.19  
  5. **Search Automation:** Code the automation sequence to navigate to a search engine (DuckDuckGo is a recommended starting point due to its relative friendliness towards automated access), input the query, and execute the search.22  
  6. **Scraping and Parsing:** Implement robust element locators (preferring specific CSS Selectors or XPath) to identify and extract the title, URL, and snippet from each search result on the page.24  
  7. **Data Serialization:** Populate the SearchModuleOutput Pydantic model with the scraped data, query information, and timing metrics. Serialize this object to a standardized JSON string for printing to standard output.  
  8. **Initial Testing:** Create a corresponding test\_selenium\_search.py file in the tests/ directory to unit test the core search() function.  
* **Deliverables:**  
  1. A fully functional and documented selenium\_search.py module.  
  2. A pyproject.toml file defining the project and its dependencies.  
  3. The auto-generated poetry.lock file ensuring reproducible builds.  
  4. A README.md file with clear instructions on how to install dependencies and run the module from the command line.

### **2.2. Implementation Deep-Dive: Headless Browser Automation**

The core technical challenge of this phase is the correct and robust implementation of headless browser automation. The entire system is designed for a server environment without a graphical user interface, making this functionality essential.20

The implementation will involve creating a helper function to instantiate the WebDriver with the necessary headless options. This encapsulates the configuration logic and keeps the main search function clean.

Python

\# in search\_agent/modules/selenium\_search.py  
from selenium import webdriver  
from selenium.webdriver.chrome.service import Service as ChromeService  
from webdriver\_manager.chrome import ChromeDriverManager  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected\_conditions as EC  
from selenium.common.exceptions import TimeoutException

def \_get\_headless\_driver() \-\> webdriver.Chrome:  
    """Configures and returns a headless Chrome WebDriver instance."""  
    options \= Options()  
    \# The modern way to enable headless mode  
    options.add\_argument("--headless=new")   
    \# These arguments are often necessary for running in containerized/server environments  
    options.add\_argument("--disable-gpu")  \# Recommended for compatibility \[21\]  
    options.add\_argument("--no-sandbox")  
    options.add\_argument("--disable-dev-shm-usage")  
    options.add\_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    \# Use webdriver-manager to automatically handle driver installation  
    driver \= webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)  
    return driver

\# Inside the main search() function:  
driver \= \_get\_headless\_driver()  
try:  
    driver.get(f"https://duckduckgo.com/?q={query}\&ia=web")  
    \# Use WebDriverWait to make the scraper resilient to page load times.  
    \# This is far more robust than a fixed \`time.sleep()\`. \[23\]  
    WebDriverWait(driver, 10).until(  
        EC.presence\_of\_element\_located((By.ID, "links"))  
    )  
      
    result\_elements \= driver.find\_elements(By.CSS\_SELECTOR, 'article\[data-testid="result"\]')  
    \#... scraping logic to loop through elements and extract data...

except TimeoutException:  
    \# Handle the case where the results page doesn't load in time  
    print("Error: Timed out waiting for search results to load.")  
    \# In a real implementation, this would log the error and raise a custom exception.  
finally:  
    \# The finally block ensures the browser process is always terminated,  
    \# preventing resource leaks and "zombie" processes on the server.  
    driver.quit()

The use of webdriver-manager abstracts away the painful process of manually downloading and managing chromedriver executables. The try...finally block is a critical pattern for resource management, guaranteeing that the browser instance is closed even if errors occur during scraping. Furthermore, employing WebDriverWait instead of fixed delays (time.sleep()) makes the scraper more efficient and robust, as it waits only as long as necessary for elements to appear.23

### **2.3. Robustness: A Strategy for Comprehensive Error and Exception Handling**

A production-grade module must anticipate and handle failures gracefully. It cannot simply crash or return partial data.

* **Custom Exceptions:** We will define a set of custom exceptions in search\_agent/core/exceptions.py. This allows the calling code (like the Orchestrator) to programmatically understand the type of failure and react accordingly.  
  Python  
  \# in search\_agent/core/exceptions.py  
  class SearchAgentError(Exception):  
      """Base exception for the search agent system."""  
      pass

  class ScrapingError(SearchAgentError):  
      """Raised when an error occurs during the scraping process."""  
      pass

  class NoResultsError(SearchAgentError):  
      """Raised when a search successfully completes but yields no results."""  
      pass

  class ConfigurationError(SearchAgentError):  
      """Raised when a required configuration (e.g., API key) is missing."""  
      pass

* **Error Handling Logic:** The scraping logic within each module will be wrapped in try...except blocks.  
  * Selenium-specific exceptions like TimeoutException or NoSuchElementException will be caught and re-raised as our custom ScrapingError. This abstracts the implementation detail (that Selenium was used) from the caller.  
  * If the scraper runs successfully but finds zero result elements, it will raise a NoResultsError. This is a more explicit and informative signal than returning an empty list, which could be ambiguous.22 The Orchestrator can then decide if it needs to run a fallback module.  
* **Logging:** The built-in logging module will be configured to log errors with timestamps and module names, providing essential diagnostic information for debugging issues on the server.

## **Section 3: Phase 2 \- Architectural Validation: The Playwright-Based Search Module**

### **3.1. Objectives, Key Tasks, and Deliverables**

* **Objective:** The central goal of this phase is to rigorously validate the modularity and extensibility of the core architecture. By introducing a second search module built with a different technology (Playwright), we prove that our standardized interfaces are effective and that new agents can be integrated without requiring changes to other parts of the system. This phase also initiates the process of comparative performance analysis.  
* **Key Tasks:**  
  1. **Dependency Addition:** Add playwright to the project's dependencies using poetry add playwright. Run playwright install to download the necessary browser binaries.  
  2. **Module Creation:** Create a new file, playwright\_search.py, inside the search\_agent/modules/ directory.  
  3. **Interface Adherence:** Implement the module following the exact same architectural patterns as the Selenium module:  
     * It must have a core async def search(query: str) \-\> SearchModuleOutput: function.  
     * It must use Typer to provide a CLI wrapper around the core function.  
     * It must return a Pydantic SearchModuleOutput object, serialized to the standard JSON format.  
  4. **Asynchronous Implementation:** Leverage Playwright's native asynchronous API to implement the browser automation logic. This will be a key difference from the synchronous Selenium implementation.  
* **Deliverables:**  
  1. A fully functional and tested playwright\_search.py module.  
  2. Updated pyproject.toml and poetry.lock files reflecting the new dependency.  
  3. A unit test file, test\_playwright\_search.py, to validate the new module's functionality in isolation.

### **3.2. Technology Rationale: Why Playwright?**

The choice of Playwright as the second library is strategic and based on its distinct advantages and differences from Selenium, which makes it an excellent candidate for architectural validation and performance comparison.

* **Performance and Modern Architecture:** Playwright is generally recognized as being faster than Selenium. This is largely due to its modern architecture, which communicates with browsers over the Chrome DevTools Protocol (or similar protocols for other browsers) and its use of persistent browser contexts. Unlike Selenium, which may start a new browser process for each test or session, Playwright can create isolated browser contexts within a single browser instance, significantly reducing startup overhead and execution time.26  
* **Asynchronous-First Design:** Playwright is designed from the ground up to be asynchronous, integrating seamlessly with Python's asyncio library.27 This aligns perfectly with the future requirements of the Orchestrator (Phase 4), which will need to run multiple search modules concurrently to achieve high performance. Introducing an async-native module now prepares the codebase for this eventuality.  
* **Simplified and Robust Automation:** Playwright features built-in "auto-waiting" mechanisms. This means that when an action like page.click() is called, Playwright automatically waits for the element to be visible, enabled, and stable before attempting the action. This can lead to simpler, more readable, and more robust code compared to Selenium's required use of explicit WebDriverWait objects for similar reliability.

The introduction of Playwright is not merely about adding another tool to the collection; it is a critical test of the system's architectural integrity. The success of this phase is measured not by whether playwright\_search.py works in isolation, but by the fact that it can be "dropped into" the system and be immediately usable by the Evaluator and Orchestrator (developed in later phases) with *zero modifications* to those components.

This process directly demonstrates the principle of **low coupling**, a cornerstone of superior software design.2 It proves that the choice of scraping technology within any given module is a black-box implementation detail. This decoupling grants the system immense long-term flexibility. The development team can add, remove, or swap out search modules based on performance, cost, or reliability without triggering a cascade of changes throughout the system. For instance, if a new, more efficient scraping library emerges in the future, a new module can be written to implement the standard interface and integrated with minimal effort, ensuring the system remains technologically current and performant.

## **Section 4: Phase 3 \- The Quantitative Evaluator Module**

### **4.1. Objectives, Key Tasks, and Deliverables**

* **Objective:** To evolve the system from a collection of functional components to a data-driven platform. This phase involves creating a sophisticated evaluator module capable of quantitatively measuring and logging the performance (speed) and quality (relevance) of any search module. This provides the empirical data necessary for benchmarking, comparison, and intelligent decision-making in later phases.  
* **Key Tasks:**  
  1. **Module Scaffolding:** Create the evaluator.py script in the main search\_agent/ directory.  
  2. **Speed Evaluation:** Implement a function that can programmatically import and execute any search module for a given query, using high-precision timers to accurately measure its total execution time.  
  3. **LLM-Based Quality Evaluation:** Integrate with a Large Language Model (LLM) API. This task includes designing a precise and effective prompt that instructs the LLM to rate the quality and relevance of a set of search results.  
  4. **NLP-Based Quality Evaluation:** Implement a non-LLM, deterministic method for scoring result quality. This will be achieved by calculating the cosine similarity between the query and the result snippets.  
  5. **Data Persistence:** Implement a logging mechanism to store all evaluation results (speed, LLM score, NLP score, and other metadata) into a structured SQLite database for future analysis.  
* **Deliverables:**  
  1. A fully functional evaluator.py module with CLI capabilities for running evaluations.  
  2. A defined SQLite database schema for storing evaluation logs.  
  3. Example evaluation reports generated from running the evaluator against the Selenium and Playwright modules.

### **4.2. Performance Benchmarking: Measuring Speed Accurately**

To obtain reliable speed metrics, the evaluator must use an appropriate timing mechanism. While time.time() is common, time.perf\_counter() is the preferred choice for benchmarking as it provides the highest available resolution performance counter, making it more accurate for measuring short durations.28 The

timeit module is excellent for micro-benchmarking small, isolated code snippets but is less suitable for timing the end-to-end execution of a script that involves significant I/O operations like network requests and browser interaction.29

The evaluation process will be as follows:

1. The evaluator will dynamically import the specified search module (e.g., search\_agent.modules.selenium\_search).  
2. It will record a start time using start\_time \= time.perf\_counter().  
3. It will then execute the module's core search(query) function.  
4. Upon completion, it will record an end time using end\_time \= time.perf\_counter().  
5. The total execution time will be calculated as duration \= end\_time \- start\_time.  
6. This duration, along with other metadata, will be logged to the database.

### **4.3. Automated Quality Evaluation: Beyond Speed**

Measuring speed is straightforward, but measuring quality is a more nuanced challenge. To address this, the evaluator will implement two distinct, complementary methods for assessing the relevance of search results.

#### **4.3.1. LLM-based Relevance & Quality Rating**

This method aims to leverage the sophisticated language understanding of an LLM to provide a human-like assessment of search result quality.

* **Integration:** The evaluator will use the appropriate Python client library (e.g., openai, anthropic) to interface with an LLM. API keys and model choices will be managed centrally via the config.py module, ensuring no secrets are hardcoded.32  
* **Prompt Engineering:** The effectiveness of this evaluation hinges entirely on the quality of the prompt. A carefully engineered "zero-shot" prompt is required to guide the LLM to produce a structured, consistent, and useful output. The prompt must clearly define the task, the rating scale, and the required output format, minimizing ambiguity and unstructured responses.34

An example of a well-structured prompt for this task:

You are an expert search quality analyst. Your task is to evaluate a list of search results based on their relevance and usefulness for the given user query.

Please provide a single integer score from 1 to 10 based on the following scale:  
1: Completely irrelevant or spam.  
5: Partially relevant, but does not directly answer the user's intent.  
10: Perfectly relevant, high-quality, and directly addresses the user's intent.

The user's query is:  
"{query}"

Here are the search results to evaluate:  
\---  
{formatted\_results}  
\---

Based on the query and the provided results, what is the overall relevance score?  
Provide only the integer score and nothing else.

Relevance Score (1-10):

This prompt structure, with its clear role-setting, explicit instructions, and constrained output format ("Provide only the integer score"), is designed to turn the LLM into a reliable and automatable component of the evaluation pipeline.36

#### **4.3.2. NLP-based Relevance Scoring**

This method provides a computationally cheaper, deterministic, and non-LLM baseline for quality assessment. It will measure the semantic similarity between the user's query and the returned search results.

* **Implementation:** The system will use the spaCy library to calculate the cosine similarity between the vector embeddings of the query and the result snippets.38 Cosine similarity measures the cosine of the angle between two vectors in a multi-dimensional space, providing a score between 0 (not similar) and 1 (identical).41 The formula is given by:

  Similarity=cos(θ)=∥A∥∥B∥A⋅B​  
  where A and B are the vector representations of the texts.  
* **Process:**  
  1. Load a spaCy model that includes word vectors, such as en\_core\_web\_md or the larger en\_core\_web\_lg for higher accuracy.39  
  2. Create a spaCy Doc object for the query: query\_doc \= nlp(query).  
  3. Concatenate the snippets of all returned results into a single string: results\_text \= " ".join(\[res.snippet for res in results\]).  
  4. Create a Doc object for the combined snippets: results\_doc \= nlp(results\_text).  
  5. Calculate the similarity score using spaCy's built-in method, which computes the cosine similarity of the averaged vectors of the Doc objects: score \= query\_doc.similarity(results\_doc).38

The decision to implement both LLM-based and NLP-based evaluation methods creates a powerful analytical framework. While the LLM provides a nuanced, contextual understanding of relevance, the cosine similarity score offers a stable, repeatable measure of semantic overlap. A significant divergence between these two scores for a given set of results can be highly informative. For example, a high cosine similarity but a low LLM score might indicate that the results are "keyword-stuffed" with terms from the query but are actually low-quality or miss the user's true intent. Conversely, a low cosine similarity with a high LLM score could suggest the results are contextually relevant using synonyms or related concepts that the LLM understands but that are not captured by simple vector averaging. Logging both metrics enables a much deeper, multi-faceted analysis of each search module's behavior.

### **4.4. Data Persistence: The Evaluation Log**

To enable long-term analysis and data-driven improvements, all evaluation metrics must be stored persistently. A full-scale relational database like PostgreSQL would be overkill for this system's needs. Python's built-in sqlite3 module is the ideal choice, providing a lightweight, serverless, file-based database that requires no external dependencies or complex setup.42

The evaluator.py module will contain functions to connect to a database file (e.g., evaluation\_log.db), create the necessary table schema if it doesn't exist, and insert a new record for each evaluation run.44

---

**Table 1: Evaluation Log SQLite Schema**

**Purpose:** To systematically capture and store performance and quality metrics for every search module execution, enabling historical analysis, trend identification, and data-driven decision-making for the Orchestrator. The schema is designed to answer critical questions such as, "What is the average speed of selenium\_search for queries containing 'AI'?" or "Which module consistently achieves the highest LLM quality score?".

| Column Name | Data Type | Description |
| :---- | :---- | :---- |
| id | INTEGER | Primary Key, auto-incrementing unique identifier for each evaluation run. |
| run\_timestamp\_utc | TEXT | The ISO 8601 formatted UTC timestamp when the evaluation was executed. |
| module\_name | TEXT | The name of the search module being evaluated (e.g., 'selenium\_search', 'brave\_api\_search'). |
| query | TEXT | The user query that was submitted to the search module. |
| execution\_time\_seconds | REAL | The total time taken by the module to execute the search, measured in seconds with high precision. |
| llm\_quality\_score | INTEGER | The 1-10 quality score assigned by the LLM evaluator. Can be NULL if this evaluation was not run. |
| nlp\_similarity\_score | REAL | The 0-1 cosine similarity score from the NLP evaluator. Can be NULL if this evaluation was not run. |
| result\_count | INTEGER | The number of results returned by the module. |
| was\_successful | INTEGER | A boolean flag (0 or 1\) indicating if the module completed without raising an exception. |
| error\_message | TEXT | The text of the exception message if was\_successful is 0\. NULL otherwise. |
| raw\_output\_json | TEXT | The complete, raw JSON output from the search module, stored for detailed inspection and re-analysis. |

---

## **Section 5: Phase 4 \- The Central Orchestrator**

### **5.1. Objectives, Key Tasks, and Deliverables**

* **Objective:** To construct the central intelligence of the system. The Orchestrator is responsible for managing the concurrent execution of multiple search modules, aggregating their outputs into a single coherent set, and applying sophisticated ranking logic to produce a final, high-quality list of results for the end-user.  
* **Key Tasks:**  
  1. **Module Scaffolding:** Create the orchestrator.py script in the search\_agent/ directory.  
  2. **Dynamic Module Execution:** Implement logic to dynamically discover and import all available search modules from the search\_agent/modules/ directory.  
  3. **Concurrent Execution:** Implement a concurrency model to run multiple search modules in parallel for a single user query, drastically reducing the total response time.  
  4. **Result Aggregation:** Develop robust algorithms for merging the result lists from all modules, with a primary focus on effective de-duplication of results.  
  5. **Re-ranking Strategy:** Implement an initial re-ranking algorithm to intelligently order the merged result set, moving beyond simple concatenation.  
  6. **Dynamic Module Selection:** Design the orchestrator to be extensible for future, more intelligent module selection strategies based on historical performance data.  
* **Deliverables:**  
  1. A functional orchestrator.py script that accepts a query, executes multiple search modules, and produces a single, de-duplicated, and ranked list of results in the standard JSON format.  
  2. A clear demonstration of concurrent execution improving overall system latency.

### **5.2. Concurrent Execution with asyncio: For I/O-Bound Performance**

Executing search modules sequentially is untenable from a performance perspective; the total latency would be the sum of each module's individual runtime. Since web scraping and API calls are fundamentally I/O-bound tasks—where the program spends the majority of its time waiting for network responses—they are ideal candidates for a concurrency model.

The choice between Python's multiprocessing and asyncio libraries is a critical architectural decision. multiprocessing achieves true parallelism by creating separate processes, each with its own Python interpreter, thereby bypassing the Global Interpreter Lock (GIL). This makes it the best choice for CPU-bound tasks.45 However, it incurs higher memory overhead and more complex inter-process communication.

In contrast, asyncio uses a single thread and a cooperative multitasking model managed by an event loop. It is exceptionally lightweight and designed specifically for handling a large number of concurrent I/O operations.45 Given that our search tasks are overwhelmingly I/O-bound,

**asyncio is the architecturally correct choice**.48

This decision requires that our search modules be compatible with the async paradigm. Modules based on httpx or playwright are natively asynchronous. For synchronous libraries like selenium or requests, asyncio.to\_thread() provides a clean way to run their blocking functions in a separate thread pool without blocking the main event loop.

The implementation in orchestrator.py will look like this:

Python

\# in orchestrator.py  
import asyncio  
from search\_agent.modules import selenium\_search, playwright\_search, brave\_api\_search

async def run\_orchestration(query: str):  
    """  
    Orchestrates the concurrent execution of multiple search modules.  
    """  
    \# asyncio.gather() runs all awaitable tasks concurrently and waits for them all to complete.  
    module\_outputs \= await asyncio.gather(  
        \# Wrap the synchronous selenium\_search.search function to run in a separate thread  
        asyncio.to\_thread(selenium\_search.search, query),  
          
        \# playwright\_search.search is assumed to be an async function  
        playwright\_search.search(query),  
          
        \# brave\_api\_search.search is also assumed to be async  
        brave\_api\_search.search(query),  
          
        \# Return exceptions instead of raising them to allow partial results  
        return\_exceptions=True   
    )

    \# Filter out any exceptions that may have occurred  
    successful\_results \= \[res for res in module\_outputs if not isinstance(res, Exception)\]  
      
    \#... proceed with merging and re-ranking the successful\_results...

### **5.3. Result Aggregation: De-duplication and Merging**

Once the modules have run, their results must be combined into a single, clean list. The most critical step in this process is de-duplication.

* **De-duplication Strategy:** The primary key for identifying a unique search result is its URL. The most efficient method for de-duplicating a list of items is to use a set for tracking seen items, which provides average O(1) time complexity for additions and lookups. For preserving the order of results, a common and effective pattern is to iterate through the lists and add items to a new list only if they haven't been seen before.51 A dictionary can also be used, keyed by the URL, to achieve the same effect while storing the full result object.

The implementation will be as follows:

Python

\# in orchestrator.py  
from typing import List, Dict  
from search\_agent.core.models import SearchModuleOutput, SearchResult

def merge\_and\_deduplicate(module\_outputs: List) \-\> List:  
    """  
    Merges results from multiple modules and de-duplicates them based on URL.  
    """  
    unique\_results: Dict \= {}  
    for output in module\_outputs:  
        if output and output.results:  
            for result in output.results:  
                \# Normalize the URL to handle minor variations (e.g., http vs https, trailing slashes)  
                normalized\_url \= str(result.url).lower().rstrip('/')  
                if normalized\_url not in unique\_results:  
                    unique\_results\[normalized\_url\] \= result  
      
    return list(unique\_results.values())

For more advanced use cases, fuzzy matching on titles or snippets using libraries like dedupe could be considered to catch near-duplicates with slightly different URLs, but URL-based de-duplication provides a robust and performant baseline.52

### **5.4. Advanced Re-ranking Strategies**

A simple merged list is insufficient; the final output must be intelligently ranked to present the most relevant and diverse results first. The Orchestrator will be designed with a pluggable re-ranking strategy.

* **Initial Heuristic Strategy:** The first implementation will use a simple, source-based heuristic. For example, results from high-trust sources (like commercial APIs) will be ranked higher than results from web scrapers. The internal order from each source will be preserved.  
* **Future Advanced Strategies:** The architecture will support the integration of more sophisticated re-ranking algorithms. These are critical for moving beyond basic relevance and incorporating factors like quality, freshness, and diversity.53  
  1. **Cross-Encoder Re-ranking:** This technique uses a powerful transformer-based model (a Cross-Encoder) to compute a highly accurate relevance score for each (query, document) pair. Unlike simple cosine similarity, a cross-encoder processes both texts simultaneously, allowing it to capture much deeper contextual interactions. The merged list would be re-ranked based on these scores.54  
  2. **Maximal Marginal Relevance (MMR):** This algorithm is used to improve the diversity of the result set. After an initial relevance ranking, MMR iteratively builds the final list by selecting the next item that offers the best trade-off between being relevant to the query and being dissimilar to the items already selected. This prevents the top results from being redundant variations of the same information.55  
  3. **LLM-based Listwise Re-ranking (e.g., RankGPT):** The most advanced approach involves using a powerful LLM to perform listwise re-ranking. The model is given the query and the entire list of candidate documents and is prompted to re-order the list for optimal overall quality, relevance, and coherence. This holistic approach can capture subtle relationships between documents that pairwise methods miss.57

### **5.5. Dynamic Module Selection**

While the initial strategy will be to "run all" available modules, a key long-term goal for the Orchestrator is to intelligently select which modules to run for a given query. This makes the system more efficient, cost-effective, and performant. The design must be extensible to support this.

The Orchestrator will be able to query the evaluation\_log.db created in Phase 3 to make data-driven decisions. Future strategies could include:

* **Performance-Based Routing:** Query the log for the historical performance (speed and quality scores) of modules for similar queries. Prioritize the module with the best historical performance and use others as fallbacks.  
* **Cost-Based Routing:** If modules have associated costs (e.g., paid APIs), the Orchestrator can implement a strategy to minimize expense. For example, it could first run free scraping modules and only invoke a paid API if the initial results are insufficient or of low quality.  
* **Query-Type-Based Routing:** Analyze the query itself to select the most appropriate module. For example, a query containing "latest news on..." could be routed directly to a news-specific API module, while a query like "how to fix..." could be routed to modules that scrape technical forums.

## **Section 6: Phase 5 \- Integration of API-Based Search Modules**

### **6.1. Objectives and Rationale**

The objective of this phase is to significantly enhance the system's speed, reliability, and result quality by integrating with commercial search APIs. While direct scraping is powerful, it can be brittle and slow. APIs offer a stable, high-throughput, and often higher-quality source of search results. Integrating them diversifies the system's capabilities and provides a reliable baseline against which scraping modules can be benchmarked.

### **6.2. Key Tasks and Deliverables**

The process for adding each new API module will rigorously follow the established architectural pattern: a new file in the modules/ directory, implementation of the dual-mode interface, and adherence to the standardized JSON output.

* **Key Tasks:**  
  1. **Develop brave\_api\_search.py:**  
     * Integrate with the Brave Search API. The official brave-search Python wrapper is a good candidate for this integration, as it simplifies the API interaction.58 Alternatively, a direct implementation using an async HTTP client like  
       httpx can be used.59  
     * The module will fetch the BRAVE\_API\_KEY from the central settings object.  
  2. **Develop google\_cse\_search.py:**  
     * Integrate with the Google Custom Search Engine (CSE) JSON API. This requires using the official Google API Python Client Library.60  
     * The module must be configured with both an API Key and a Search Engine ID (CX), which will be fetched from the settings object.61  
  3. **Configuration Management:** Update config.py and the .env.template file to include placeholders for BRAVE\_API\_KEY, GOOGLE\_API\_KEY, and GOOGLE\_CSE\_ID.  
  4. **Orchestrator and Evaluator Updates:**  
     * Update the orchestrator.py to import and execute these new, fast, async-native modules.  
     * Update the evaluator.py to be able to benchmark these API modules for speed and quality, adding their results to the evaluation\_log.db.  
* **Deliverables:**  
  1. Two or more production-ready, API-based search modules (brave\_api\_search.py, google\_cse\_search.py).  
  2. Full integration of these modules into the Orchestrator's concurrent execution flow.  
  3. Demonstration of the Evaluator benchmarking the new API modules alongside the existing scraping modules.

## **Section 7: Phase 6 \- Expansion with Specialized Python Libraries**

### **7.1. Objectives and Rationale**

The final development phase aims to complete the suite of search agents by incorporating other powerful Python libraries that offer unique advantages not covered by full browser automation or general-purpose APIs. This ensures the Orchestrator has the most diverse and specialized toolkit possible, allowing it to select the absolute best tool for a specific task.

### **7.2. Key Tasks and Deliverables**

* **Objective:** To research, identify, and implement modules for specialized libraries, maintaining all established architectural standards.  
* **Key Tasks:**  
  1. **Research and Selection:** Identify other valuable libraries for web data extraction. Prime candidates are Scrapy and httpx.  
  2. **Develop httpx\_search.py:**  
     * **Rationale:** For search engines with simple, static HTML result pages that do not rely heavily on JavaScript, using a full browser like Selenium or Playwright is computationally expensive and slow. httpx is a modern, high-performance, async-native HTTP client that can retrieve the raw HTML of such pages with minimal overhead.62 This module would represent the fastest possible method for compatible targets. It would be paired with a lightweight HTML parser like  
       BeautifulSoup to extract the data.63  
  3. **Develop scrapy\_search.py:**  
     * **Rationale:** Scrapy is not just a library; it is a complete, asynchronous web scraping *framework* designed for large-scale, high-performance crawling.65 While our system is agent-based rather than crawler-based, a Scrapy module could be designed to perform a more complex, multi-page search task on a specific, high-value target site. For example, it could be configured to not only scrape the first page of results but also follow the top three links and extract additional context from those pages. This deeper search capability is beyond the scope of the simpler single-page scraping modules. Scrapy's built-in support for asynchronous requests, middlewares, and data pipelines makes it exceptionally powerful for these complex scenarios.67  
  4. **Integration:** As with all other modules, these new agents will be fully integrated into the Orchestrator and made available to the Evaluator for benchmarking.  
* **Deliverables:**  
  1. A comprehensive and diverse set of search modules, including agents for httpx and Scrapy.  
  2. An updated Orchestrator capable of leveraging this full suite of tools.  
  3. A final evaluation report comparing the performance and quality of all implemented modules across various query types.

To guide the selection and development of these modules, the following table summarizes the trade-offs of each technology.

---

**Table 2: Search Technology Trade-offs**

**Purpose:** To provide a clear, at-a-glance reference for engineers to understand the strategic advantages and disadvantages of each search technology. This information is crucial for guiding the Orchestrator's dynamic module selection logic and for making informed decisions about which type of module to develop for future targets.

| Technology | Execution Speed | Resource Usage | Dynamic JS Handling | Robustness/Reliability | Ideal Use Case |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Commercial API** | Very Fast | Very Low | N/A | Very High | The default choice for high-quality, reliable, and fast results when a budget is available. 61 |
| **httpx \+ BeautifulSoup** | Very Fast | Very Low | None | Low | The fastest scraping method for simple, static HTML websites that do not use JavaScript to render content. 62 |
| **Scrapy** | Fast | Low | Limited (requires integration) | High | High-volume, large-scale scraping of structured, mostly static websites. Excellent for complex crawling logic. 67 |
| **Playwright** | Moderate | High | Excellent | High | Scraping modern, complex, JavaScript-heavy web applications. Faster than Selenium due to its modern architecture. 26 |
| **Selenium** | Slow | High | Excellent | Moderate | A mature, universally supported tool for scraping any website, especially those requiring complex user interactions. 26 |

---

## **Section 8: System-Wide Considerations and Future Enhancements**

### **8.1. Operational Robustness: Anti-Scraping Countermeasures**

Web scraping modules are inherently vulnerable to anti-bot detection systems. To enhance their operational robustness, several strategies will be documented and can be implemented as needed:

* **User-Agent Rotation:** Cycle through a list of legitimate, common browser user-agent strings to avoid being identified by a single, static agent.  
* **Proxy Integration:** Route requests through a pool of residential or data center proxies to mask the server's IP address and distribute the request load across multiple origins. Libraries like httpx, Selenium, and Playwright all support proxy configuration.  
* **Intelligent Delays:** Introduce randomized, small delays between requests to better mimic human browsing patterns.  
* **Advanced Evasion Services:** For particularly difficult targets, a dedicated module could be created to interface with a commercial anti-blocking service (e.g., ZenRows, ScrapingBee). These services handle proxy rotation, CAPTCHA solving, and browser fingerprinting automatically.19

### **8.2. Architectural Extensibility: A Guide for the Future**

The long-term value of this system lies in its modularity and extensibility. A formal guide will be created in the project's documentation (docs/) outlining the process for adding new components.

* **Adding a New Search Module:** The guide will provide a checklist for developers:  
  1. Create the new module file in search\_agent/modules/.  
  2. Implement the search() function with the standard signature.  
  3. Wrap it with the Typer CLI pattern.  
  4. Ensure it returns a validated SearchModuleOutput object.  
  5. Add any new dependencies via poetry add.  
  6. Import the new module into the Orchestrator's execution list.  
  7. Write corresponding unit tests.  
* **Adding a New Evaluation Metric:** The guide will detail how to add a new scoring method to evaluator.py, add a corresponding column to the SQLite database schema (requiring a migration script), and update the logging function to include the new metric.

### **8.3. Deployment and Operations**

For deployment, the application should be containerized using **Docker**. A Dockerfile will be created to define the environment, copy the application code, and install dependencies using poetry install. This creates a portable, self-contained artifact that can be deployed consistently anywhere.

For automated or scheduled execution, the system can be triggered by a simple cron job on the server, which would execute the orchestrator.py script. For more complex scheduling needs or distributed task management, integrating a task queue like **Celery** with a message broker (e.g., RabbitMQ or Redis) would be the next logical step.

## **Conclusion**

This development plan details the architectural design and phased implementation of a sophisticated, modular web search agent system. By adhering to the core principles of modularity, standardized interfaces, and dual-mode operation, the proposed architecture ensures the final product is not only powerful but also highly maintainable, extensible, and robust.

The phased approach systematically builds the system from the ground up, starting with a foundational MVP to validate the architecture, followed by the introduction of a quantitative evaluation framework that enables data-driven decision-making. The central Orchestrator, with its capacity for concurrent execution and intelligent result aggregation, serves as the system's brain, transforming disparate data sources into a single, high-quality stream of information.

The deliberate inclusion of a diverse range of search technologies—from browser automation with Selenium and Playwright, to high-throughput APIs like Brave and Google, to specialized frameworks like Scrapy—provides the Orchestrator with a versatile toolkit. This allows the system to dynamically select the optimal method for any given query, balancing speed, cost, and the complexity of the target website. The result is a system that is greater than the sum of its parts: a flexible, performance-aware, and continuously improving platform for web intelligence. This document provides a clear and actionable blueprint for constructing this advanced system.

#### **Works cited**

1. Best Practices in Structuring Python Projects \- Dagster, accessed July 5, 2025, [https://dagster.io/blog/python-project-best-practices](https://dagster.io/blog/python-project-best-practices)  
2. How to design modular Python projects \- LabEx, accessed July 5, 2025, [https://labex.io/tutorials/python-how-to-design-modular-python-projects-420186](https://labex.io/tutorials/python-how-to-design-modular-python-projects-420186)  
3. Organizing Python Code into Modules for Better Organization and Reusability \- llego.dev, accessed July 5, 2025, [https://llego.dev/posts/organizing-python-code-modules-better-organization-reusability/](https://llego.dev/posts/organizing-python-code-modules-better-organization-reusability/)  
4. Dead Simple Python: Project Structure and Imports \- DEV Community, accessed July 5, 2025, [https://dev.to/codemouse92/dead-simple-python-project-structure-and-imports-38c6](https://dev.to/codemouse92/dead-simple-python-project-structure-and-imports-38c6)  
5. What is the optimal structure for a Python project? \- Reddit, accessed July 5, 2025, [https://www.reddit.com/r/Python/comments/18qkivr/what\_is\_the\_optimal\_structure\_for\_a\_python\_project/](https://www.reddit.com/r/Python/comments/18qkivr/what_is_the_optimal_structure_for_a_python_project/)  
6. Structuring Your Project — The Hitchhiker's Guide to Python, accessed July 5, 2025, [https://docs.python-guide.org/writing/structure/](https://docs.python-guide.org/writing/structure/)  
7. Poetry vs Pip: Choosing the Right Python Package Manager | Better Stack Community, accessed July 5, 2025, [https://betterstack.com/community/guides/scaling-python/poetry-vs-pip/](https://betterstack.com/community/guides/scaling-python/poetry-vs-pip/)  
8. Beginner's Guide to Python Poetry vs Pip | Osayi Akoko, accessed July 5, 2025, [https://osayiakoko.hashnode.dev/a-comprehensive-guide-to-python-poetry-for-beginners](https://osayiakoko.hashnode.dev/a-comprehensive-guide-to-python-poetry-for-beginners)  
9. Poetry \> pip \+ venv? Here's why developers are switching \- DEV Community, accessed July 5, 2025, [https://dev.to/leapcell/poetry-pip-venv-heres-why-developers-are-switching-5005](https://dev.to/leapcell/poetry-pip-venv-heres-why-developers-are-switching-5005)  
10. Simplifying Configuration Management in Pure Python \- The Computist Journal, accessed July 5, 2025, [https://blog.apiad.net/p/simplifying-configuration-management](https://blog.apiad.net/p/simplifying-configuration-management)  
11. Working with Python Configuration Files: Tutorial & Best Practices \- Configu, accessed July 5, 2025, [https://configu.com/blog/working-with-python-configuration-files-tutorial-best-practices/](https://configu.com/blog/working-with-python-configuration-files-tutorial-best-practices/)  
12. Best Practices for Implementing Configuration Class in Python | by VerticalServe Blogs, accessed July 5, 2025, [https://verticalserve.medium.com/best-practices-for-implementing-configuration-class-in-python-b63b70048cc5](https://verticalserve.medium.com/best-practices-for-implementing-configuration-class-in-python-b63b70048cc5)  
13. Best Practices for Working with Configuration in Python Applications, accessed July 5, 2025, [https://tech.preferred.jp/en/blog/working-with-configuration-in-python/](https://tech.preferred.jp/en/blog/working-with-configuration-in-python/)  
14. Comparing Python Command Line Interface Tools: Argparse, Click, and Typer | CodeCut, accessed July 5, 2025, [https://codecut.ai/comparing-python-command-line-interface-tools-argparse-click-and-typer/](https://codecut.ai/comparing-python-command-line-interface-tools-argparse-click-and-typer/)  
15. Alternatives, Inspiration and Comparisons \- Typer, accessed July 5, 2025, [https://typer.tiangolo.com/alternatives/](https://typer.tiangolo.com/alternatives/)  
16. Navigating the CLI Landscape in Python: A Comparative Study of argparse, click, and typer, accessed July 5, 2025, [https://medium.com/@mohd\_nass/navigating-the-cli-landscape-in-python-a-comparative-study-of-argparse-click-and-typer-480ebbb7172f](https://medium.com/@mohd_nass/navigating-the-cli-landscape-in-python-a-comparative-study-of-argparse-click-and-typer-480ebbb7172f)  
17. Why Click? — Click Documentation (8.2.x), accessed July 5, 2025, [https://click.palletsprojects.com/en/stable/why/](https://click.palletsprojects.com/en/stable/why/)  
18. Click vs argparse \- Which CLI Package is Better? \- Python Snacks, accessed July 5, 2025, [https://www.pythonsnacks.com/p/click-vs-argparse-python](https://www.pythonsnacks.com/p/click-vs-argparse-python)  
19. Web Scraping With a Headless Browser in Python \[Selenium ..., accessed July 5, 2025, [https://www.zenrows.com/blog/headless-browser-python](https://www.zenrows.com/blog/headless-browser-python)  
20. Headless Browser Testing With Selenium Python | BrowserStack, accessed July 5, 2025, [https://www.browserstack.com/guide/headless-browser-testing-selenium-python](https://www.browserstack.com/guide/headless-browser-testing-selenium-python)  
21. How to configure ChromeDriver to initiate Chrome browser in Headless mode through Selenium? \- Stack Overflow, accessed July 5, 2025, [https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug](https://stackoverflow.com/questions/46920243/how-to-configure-chromedriver-to-initiate-chrome-browser-in-headless-mode-throug)  
22. DuckDuckGo-Scraper/DuckDuckGo.py at main · JohnScooby/DuckDuckGo-Scraper \- GitHub, accessed July 5, 2025, [https://github.com/JohnScooby/DuckDuckGo-Scraper/blob/main/DuckDuckGo.py](https://github.com/JohnScooby/DuckDuckGo-Scraper/blob/main/DuckDuckGo.py)  
23. Web scraping using Selenium in Python \- Futile Devices, accessed July 5, 2025, [https://www.futiledevices.be/webscraping-post/](https://www.futiledevices.be/webscraping-post/)  
24. Scrape Related Searches from DuckDuckGo using Python \- SerpApi, accessed July 5, 2025, [https://serpapi.com/blog/scrape-related-searches-from-duckduckgo-using-python/](https://serpapi.com/blog/scrape-related-searches-from-duckduckgo-using-python/)  
25. Headless Browser Testing with Selenium & Python \- BlazeMeter, accessed July 5, 2025, [https://www.blazemeter.com/blog/headless-browser-selenium-python](https://www.blazemeter.com/blog/headless-browser-selenium-python)  
26. Playwright vs. Selenium for web scraping \- Apify Blog, accessed July 5, 2025, [https://blog.apify.com/playwright-vs-selenium/](https://blog.apify.com/playwright-vs-selenium/)  
27. Playwright vs Selenium \- Scrapfly, accessed July 5, 2025, [https://scrapfly.io/blog/playwright-vs-selenium/](https://scrapfly.io/blog/playwright-vs-selenium/)  
28. How to measure the execution time of a Python script \- Quora, accessed July 5, 2025, [https://www.quora.com/How-can-I-measure-the-execution-time-of-a-Python-script](https://www.quora.com/How-can-I-measure-the-execution-time-of-a-Python-script)  
29. How to check the Execution Time of Python script ? \- GeeksforGeeks, accessed July 5, 2025, [https://www.geeksforgeeks.org/python/how-to-check-the-execution-time-of-python-script/](https://www.geeksforgeeks.org/python/how-to-check-the-execution-time-of-python-script/)  
30. How to Benchmark (Python) Code \- Sebastian Witowski, accessed July 5, 2025, [https://switowski.com/blog/how-to-benchmark-python-code/](https://switowski.com/blog/how-to-benchmark-python-code/)  
31. 3 Simple Ways to Time Your Python Code \- Better Programming, accessed July 5, 2025, [https://betterprogramming.pub/top-3-ways-to-time-python-code-d46b37d418e0](https://betterprogramming.pub/top-3-ways-to-time-python-code-d46b37d418e0)  
32. Your First Local LLM API Project in Python Step-By-Step ..., accessed July 5, 2025, [https://machinelearningmastery.com/your-first-local-llm-api-project-in-python-step-by-step/](https://machinelearningmastery.com/your-first-local-llm-api-project-in-python-step-by-step/)  
33. Building with LLMs: A Practical Guide to API Integration, accessed July 5, 2025, [https://www.buildfastwithai.com/blogs/building-with-llms-a-practical-guide-to-api-integration](https://www.buildfastwithai.com/blogs/building-with-llms-a-practical-guide-to-api-integration)  
34. Prompt engineering concepts \- Amazon Bedrock, accessed July 5, 2025, [https://docs.aws.amazon.com/en\_us/bedrock/latest/userguide/prompt-engineering-guidelines.html](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/prompt-engineering-guidelines.html)  
35. Examples of Prompts | Prompt Engineering Guide, accessed July 5, 2025, [https://www.promptingguide.ai/introduction/examples](https://www.promptingguide.ai/introduction/examples)  
36. Large Language Model Prompt Engineering for Common Data Problems \- Matillion, accessed July 5, 2025, [https://www.matillion.com/blog/large-language-model-prompt-engineering-for-common-data-problems](https://www.matillion.com/blog/large-language-model-prompt-engineering-for-common-data-problems)  
37. Zero-shot prompt-based classification: topic labeling in times of foundation models in German Tweets \- arXiv, accessed July 5, 2025, [https://arxiv.org/html/2406.18239v1](https://arxiv.org/html/2406.18239v1)  
38. Measuring semantic similarity with spaCy | Python, accessed July 5, 2025, [https://campus.datacamp.com/courses/natural-language-processing-with-spacy/spacy-linguistic-annotations-and-word-vectors?ex=12](https://campus.datacamp.com/courses/natural-language-processing-with-spacy/spacy-linguistic-annotations-and-word-vectors?ex=12)  
39. Python | Word Similarity using spaCy \- GeeksforGeeks, accessed July 5, 2025, [https://www.geeksforgeeks.org/python/python-word-similarity-using-spacy/](https://www.geeksforgeeks.org/python/python-word-similarity-using-spacy/)  
40. Similarity in Spacy \- nlp \- Stack Overflow, accessed July 5, 2025, [https://stackoverflow.com/questions/53453559/similarity-in-spacy](https://stackoverflow.com/questions/53453559/similarity-in-spacy)  
41. Python | Measure similarity between two sentences using cosine similarity \- GeeksforGeeks, accessed July 5, 2025, [https://www.geeksforgeeks.org/machine-learning/python-measure-similarity-between-two-sentences-using-cosine-similarity/](https://www.geeksforgeeks.org/machine-learning/python-measure-similarity-between-two-sentences-using-cosine-similarity/)  
42. Introduction to Programming SQLite Database Using Python for Data logging Applications : r/instructables \- Reddit, accessed July 5, 2025, [https://www.reddit.com/r/instructables/comments/1kj2uvo/introduction\_to\_programming\_sqlite\_database\_using/](https://www.reddit.com/r/instructables/comments/1kj2uvo/introduction_to_programming_sqlite_database_using/)  
43. How to Enable SQLite Query Logging? \- GeeksforGeeks, accessed July 5, 2025, [https://www.geeksforgeeks.org/sqlite/how-to-enable-sqlite-query-logging/](https://www.geeksforgeeks.org/sqlite/how-to-enable-sqlite-query-logging/)  
44. sqlite3 — DB-API 2.0 interface for SQLite databases — Python 3.13 ..., accessed July 5, 2025, [https://docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)  
45. AsyncIO vs Threading vs Multiprocessing: A Beginner's Guide \- Codimite, accessed July 5, 2025, [https://codimite.ai/blog/asyncio-vs-threading-vs-multiprocessing-a-beginners-guide/](https://codimite.ai/blog/asyncio-vs-threading-vs-multiprocessing-a-beginners-guide/)  
46. python \- multiprocessing vs multithreading vs asyncio \- Stack Overflow, accessed July 5, 2025, [https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio](https://stackoverflow.com/questions/27435284/multiprocessing-vs-multithreading-vs-asyncio)  
47. Advanced Guide to Asyncio, Threading, and Multiprocessing in Python | Stackademic, accessed July 5, 2025, [https://stackademic.com/blog/advanced-guide-to-asyncio-threading-and-multiprocessing-in-python-c4dc50971d24](https://stackademic.com/blog/advanced-guide-to-asyncio-threading-and-multiprocessing-in-python-c4dc50971d24)  
48. Best method for parallel web requests \- Python \- Reddit, accessed July 5, 2025, [https://www.reddit.com/r/Python/comments/9rm427/best\_method\_for\_parallel\_web\_requests/](https://www.reddit.com/r/Python/comments/9rm427/best_method_for_parallel_web_requests/)  
49. Python Multithreading vs Multiprocessing vs Asyncio Explained in 10 Minutes \- YouTube, accessed July 5, 2025, [https://www.youtube.com/watch?v=QXwefd3z8IU](https://www.youtube.com/watch?v=QXwefd3z8IU)  
50. Asyncio vs Threading vs Multiprocessing : r/learnpython \- Reddit, accessed July 5, 2025, [https://www.reddit.com/r/learnpython/comments/1fhry6u/asyncio\_vs\_threading\_vs\_multiprocessing/](https://www.reddit.com/r/learnpython/comments/1fhry6u/asyncio_vs_threading_vs_multiprocessing/)  
51. How to perform efficient list deduplication \- LabEx, accessed July 5, 2025, [https://labex.io/tutorials/python-how-to-perform-efficient-list-deduplication-436784](https://labex.io/tutorials/python-how-to-perform-efficient-list-deduplication-436784)  
52. dedupeio/dedupe: :id: A python library for accurate and scalable fuzzy matching, record deduplication and entity-resolution. \- GitHub, accessed July 5, 2025, [https://github.com/dedupeio/dedupe](https://github.com/dedupeio/dedupe)  
53. Re-ranking | Machine Learning \- Google for Developers, accessed July 5, 2025, [https://developers.google.com/machine-learning/recommendation/dnn/re-ranking](https://developers.google.com/machine-learning/recommendation/dnn/re-ranking)  
54. A Dummies guide to implementing Re-Ranking — Code walkthrough | by Rajesh Rajamani | primepartnerstech | Medium, accessed July 5, 2025, [https://medium.com/primepartnerstech/a-dummies-guide-to-implementing-re-ranking-code-walkthrough-c7d6705b6c22](https://medium.com/primepartnerstech/a-dummies-guide-to-implementing-re-ranking-code-walkthrough-c7d6705b6c22)  
55. Re-Ranking Algorithms in Vector Databases: An In-Depth Analysis \- Bishal Bose \- Medium, accessed July 5, 2025, [https://bishalbose294.medium.com/re-ranking-algorithms-in-vector-databases-in-depth-analysis-b3560b1ebd6f](https://bishalbose294.medium.com/re-ranking-algorithms-in-vector-databases-in-depth-analysis-b3560b1ebd6f)  
56. rerankers: A Lightweight Python Library to Unify Ranking Methods \- arXiv, accessed July 5, 2025, [https://arxiv.org/html/2408.17344v2](https://arxiv.org/html/2408.17344v2)  
57. RankGPT as a Re-Ranking Agent for RAG (Tutorial) \- DataCamp, accessed July 5, 2025, [https://www.datacamp.com/tutorial/rankgpt-rag-reranking-agent](https://www.datacamp.com/tutorial/rankgpt-rag-reranking-agent)  
58. brave-search·PyPI, accessed July 5, 2025, [https://pypi.org/project/brave-search/](https://pypi.org/project/brave-search/)  
59. Brave Search API, accessed July 5, 2025, [https://brave.com/search/api/](https://brave.com/search/api/)  
60. Libraries and Samples | Programmable Search Engine \- Google for Developers, accessed July 5, 2025, [https://developers.google.com/custom-search/v1/libraries](https://developers.google.com/custom-search/v1/libraries)  
61. Custom Search JSON API | Programmable Search Engine | Google ..., accessed July 5, 2025, [https://developers.google.com/custom-search/v1/overview](https://developers.google.com/custom-search/v1/overview)  
62. Web scraping using HTTPX in Python, covering setup, advanced features, comparisons with Requests, and more. \- GitHub, accessed July 5, 2025, [https://github.com/luminati-io/httpx-web-scraping](https://github.com/luminati-io/httpx-web-scraping)  
63. Web Scraping With HTTPX and Python in 2025 \- Bright Data, accessed July 5, 2025, [https://brightdata.com/blog/web-data/web-scraping-with-httpx](https://brightdata.com/blog/web-data/web-scraping-with-httpx)  
64. How to Web Scrape with HTTPX and Python \- Scrapfly, accessed July 5, 2025, [https://scrapfly.io/blog/web-scraping-with-python-httpx/](https://scrapfly.io/blog/web-scraping-with-python-httpx/)  
65. Difference between BeautifulSoup and Scrapy crawler \- GeeksforGeeks, accessed July 5, 2025, [https://www.geeksforgeeks.org/python/difference-between-beautifulsoup-and-scrapy-crawler/](https://www.geeksforgeeks.org/python/difference-between-beautifulsoup-and-scrapy-crawler/)  
66. Scrapy vs. Beautiful Soup: A Comparison of Web Scraping Tools \- Oxylabs, accessed July 5, 2025, [https://oxylabs.io/blog/scrapy-vs-beautifulsoup](https://oxylabs.io/blog/scrapy-vs-beautifulsoup)  
67. Scrapy vs. Beautiful Soup for web scraping \- Apify Blog, accessed July 5, 2025, [https://blog.apify.com/beautiful-soup-vs-scrapy-web-scraping/](https://blog.apify.com/beautiful-soup-vs-scrapy-web-scraping/)  
68. Brave Search API documentation, accessed July 5, 2025, [https://api-dashboard.search.brave.com/app/documentation](https://api-dashboard.search.brave.com/app/documentation)  
69. Scrapy vs Playwright: Web Scraping Comparison Guide \- Bright Data, accessed July 5, 2025, [https://brightdata.com/blog/web-data/scrapy-vs-playwright](https://brightdata.com/blog/web-data/scrapy-vs-playwright)  
70. Scrapy vs. Selenium for Web Scraping \- Bright Data, accessed July 5, 2025, [https://brightdata.com/blog/web-data/scrapy-vs-selenium](https://brightdata.com/blog/web-data/scrapy-vs-selenium)