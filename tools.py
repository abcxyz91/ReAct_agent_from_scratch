import os, re
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import Union
import requests, docx, pdfplumber

_ = load_dotenv()
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

# --- Helper Function to Parse Write Arguments ---
def _parse_file_args(input_str: str) -> tuple[str, str]:
    """
    Parses the single-string input from the agent into (file_path, content).
    Expected format: "path/to/file.txt", "The content to write."
    """
    # Regex to find two quoted strings, separated by a comma
    # re.DOTALL means '.' will match newlines, so content can span multiple lines
    match = re.match(r'\s*"(.*?)"\s*,\s*"(.*)"\s*$', input_str, re.DOTALL)
    
    if not match:
        raise ValueError("Invalid format. Expected: \"<file_path>\", \"<content>\"")
        
    file_path, content = match.groups()
    return file_path, content


def calculator(expression: str) -> str:
    """
    Evaluates a single, simple mathematical expression.
    Input: A string-formatted mathematical operation (e.g., "2 * (10 + 5)").
    """
    try:
        # Use Union for type checker, but cast to str for the agent
        result: Union[float, int, str] = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"
    

def search_internet(query: str) -> str:
    """
    Performs a web search using Serper.dev API and returns the top 5 results.
    Input: A string-based search query.
    """
    try:
        api_key = os.environ.get("SERPER_API_KEY")
        if not api_key:
            return "Error: SERPER_API_KEY not found in environment variables"
            
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": 5
        }
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        # Check if "organic" key exists AND is not empty
        organic_results = data.get("organic")
        if not organic_results:
            return "No relevant information or search results found."
            
        # Format the results into a concise string for LLM consumption
        formatted_results = "\n".join(
            [f"- {res.get('title', 'No title')}: {res.get('snippet', 'No description')} <{res.get('link', '#')}>"
             for res in organic_results]
        )

        return formatted_results

    except requests.exceptions.RequestException as e:
        return f"Error making request to Serper API: {e}"
    except Exception as e:
        return f"Error during internet search: {e}"
    

def scrape_content(url: str) -> str:
    """
    Fetches the clean, visible text content from a single URL.
    Input: A single, valid URL (e.g., "https://example.com/article").
    """    
    # Custom User-Agent to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Fetch the page with a custom header
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Catches 4xx/5xx errors
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script, style, and comments elements to clean up the content
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.decompose()
            
        # Get all visible text and join it, removing excessive whitespace and newlines
        clean_text = soup.get_text(separator=" ", strip=True)
        
        # Limit the output to the first 8000 characters to avoid overwhelming the LLM
        return clean_text[:8000] 

    except requests.exceptions.HTTPError as e:
        return f"Error retrieving content (HTTP Status Code): {e}"
    except requests.exceptions.RequestException as e:
        return f"Error connecting to URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred during scraping: {e}"
    

def get_weather(location: str) -> str:
    """
    Fetches the current weather for a specific location.
    Input: A single string of the location (e.g., "Tokyo" or "Paris, France").
    """
    try:
        api_key = os.environ.get("WEATHER_API_KEY")
        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}", timeout=10)
        data = response.json()
        if "current" in data:
            temp_c = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            return f"The current temperature in {location} is {temp_c}°C with {condition}."
        else:
            return "Weather information not found."
    except Exception as e:
        return f"Error retrieving weather data: {e}"
    

def read_file_content(file_path: str) -> str:
    """
    Reads and returns the content of a local file (limited to 8000 chars).
    Input: A single string of the file path (e.g., "notes.txt" or "folder/report.md").
    """
    if not os.path.isfile(file_path):
        return f"File not found: {file_path}"
    ext = os.path.splitext(file_path)[1].lower()

    text = ""

    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        elif ext == ".docx":
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
        else:
            return f"Unsupported file type: {ext}"
        return text.strip()
    
    except FileNotFoundError:
        return f"Error: File not found at path: {file_path}"
    except PermissionError:
        return f"Error: Permission denied to read file: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"


def write_file_content(input: str) -> str:
    """
    Writes content to a local file, OVERWRITING any existing content.
    Input: A single string with the file path AND content, in the format:
    "path/to/file.txt", "The content to write."
    """
    try:
        file_path, content = _parse_file_args(input)

        # Automatically create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Content written to {file_path} successfully."
    except ValueError as e: # Catch parsing errors
        return f"Error: {e}"
    except PermissionError:
        return f"Error: Permission denied to write to file: {file_path}"
    except Exception as e:
        return f"Error writing to file: {e}"
    
known_actions = {
    "calculator": calculator,
    "search_internet": search_internet,
    "scrape_content": scrape_content,
    "get_weather": get_weather,
    "read_file_content": read_file_content,
    "write_file_content": write_file_content,
}