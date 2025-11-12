import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
import requests
from tools import (
    calculator,
    search_internet,
    scrape_content,
    get_weather,
    read_file_content,
    write_file_content,
    _parse_file_args
)


# =========================
# Test _parse_file_args Helper
# =========================

class TestParseFileArgs:
    """Tests for the _parse_file_args helper function."""
    
    def test_valid_input(self):
        """Test parsing valid input with file path and content."""
        input_str = '"output.txt", "Hello World"'
        file_path, content = _parse_file_args(input_str)
        assert file_path == "output.txt"
        assert content == "Hello World"
    
    def test_valid_input_with_spaces(self):
        """Test parsing with extra whitespace."""
        input_str = '  "notes.txt"  ,  "Some notes here"  '
        file_path, content = _parse_file_args(input_str)
        assert file_path == "notes.txt"
        assert content == "Some notes here"
    
    def test_multiline_content(self):
        """Test parsing content with newlines."""
        input_str = '"report.txt", "Line 1\nLine 2\nLine 3"'
        file_path, content = _parse_file_args(input_str)
        assert file_path == "report.txt"
        assert content == "Line 1\nLine 2\nLine 3"
    
    def test_invalid_format_missing_quotes(self):
        """Test that invalid format raises ValueError."""
        input_str = 'file.txt, content'
        with pytest.raises(ValueError, match="Invalid format"):
            _parse_file_args(input_str)
    
    def test_invalid_format_single_argument(self):
        """Test that single argument raises ValueError."""
        input_str = '"file.txt"'
        with pytest.raises(ValueError, match="Invalid format"):
            _parse_file_args(input_str)


# =========================
# Test calculator
# =========================

class TestCalculator:
    """Tests for the calculator function."""
    
    def test_basic_addition(self):
        """Test simple addition."""
        result = calculator("2 + 2")
        assert result == "4"
    
    def test_basic_subtraction(self):
        """Test simple subtraction."""
        result = calculator("10 - 3")
        assert result == "7"
    
    def test_basic_multiplication(self):
        """Test simple multiplication."""
        result = calculator("5 * 4")
        assert result == "20"
    
    def test_basic_division(self):
        """Test simple division."""
        result = calculator("20 / 4")
        assert result == "5.0"
    
    def test_complex_expression(self):
        """Test complex mathematical expression."""
        result = calculator("2 * (10 + 5)")
        assert result == "30"
    
    def test_percentage_calculation(self):
        """Test percentage calculation."""
        result = calculator("0.25 * 160")
        assert result == "40.0"
    
    def test_power_operation(self):
        """Test power operation."""
        result = calculator("2 ** 3")
        assert result == "8"
    
    def test_invalid_expression(self):
        """Test that invalid expression returns error message."""
        result = calculator("2 + + 2")
        assert "Error evaluating expression" in result
    
    def test_division_by_zero(self):
        """Test division by zero returns error."""
        result = calculator("5 / 0")
        assert "Error evaluating expression" in result


# =========================
# Test search_internet
# =========================

class TestSearchInternet:
    """Tests for the search_internet function."""
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_successful_search(self, mock_post):
        """Test successful internet search with results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Test Result 1",
                    "snippet": "This is a test snippet 1",
                    "link": "https://example.com/1"
                },
                {
                    "title": "Test Result 2",
                    "snippet": "This is a test snippet 2",
                    "link": "https://example.com/2"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = search_internet("test query")
        
        assert "Test Result 1" in result
        assert "Test Result 2" in result
        assert "https://example.com/1" in result
        assert "This is a test snippet 1" in result
        mock_post.assert_called_once()
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_no_results_found(self, mock_post):
        """Test when no search results are returned."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic": []}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = search_internet("nonexistent query")
        
        assert "No relevant information" in result
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_missing_organic_key(self, mock_post):
        """Test when API response doesn't have organic results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = search_internet("test query")
        
        assert "No relevant information" in result
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test when SERPER_API_KEY is not set."""
        result = search_internet("test query")
        assert "SERPER_API_KEY not found" in result
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_request_exception(self, mock_post):
        """Test handling of request exceptions."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = search_internet("test query")
        
        assert "Error making request to Serper API" in result
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Error")
        mock_post.return_value = mock_response
        
        result = search_internet("test query")
        
        assert "Error making request to Serper API" in result


# =========================
# Test scrape_content
# =========================

class TestScrapeContent:
    """Tests for the scrape_content function."""
    
    @patch('tools.requests.get')
    def test_successful_scrape(self, mock_get):
        """Test successful content scraping."""
        html_content = """
        <html>
            <body>
                <script>console.log('test');</script>
                <style>.test { color: red; }</style>
                <header>Header content</header>
                <nav>Navigation</nav>
                <p>This is the main content.</p>
                <p>Another paragraph.</p>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.content = html_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_content("https://example.com")
        
        assert "This is the main content." in result
        assert "Another paragraph." in result
        assert "console.log" not in result  # Scripts should be removed
        assert "Header content" not in result  # Headers should be removed
        assert "Footer content" not in result  # Footers should be removed
    
    @patch('tools.requests.get')
    def test_content_truncation(self, mock_get):
        """Test that content is truncated to 8000 characters."""
        long_content = "<html><body>" + "a" * 10000 + "</body></html>"
        mock_response = MagicMock()
        mock_response.content = long_content.encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = scrape_content("https://example.com")
        
        assert len(result) <= 8000
    
    @patch('tools.requests.get')
    def test_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = scrape_content("https://example.com")
        
        assert "Error retrieving content" in result
        assert "HTTP Status Code" in result
    
    @patch('tools.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection errors."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        result = scrape_content("https://example.com")
        
        assert "Error connecting to URL" in result
    
    @patch('tools.requests.get')
    def test_timeout_error(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = scrape_content("https://example.com")
        
        assert "Error connecting to URL" in result
    
    @patch('tools.requests.get')
    def test_user_agent_header(self, mock_get):
        """Test that custom User-Agent header is sent."""
        mock_response = MagicMock()
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        scrape_content("https://example.com")
        
        # Check that requests.get was called with User-Agent header
        call_args = mock_get.call_args
        assert 'headers' in call_args[1]
        assert 'User-Agent' in call_args[1]['headers']


# =========================
# Test get_weather
# =========================

class TestGetWeather:
    """Tests for the get_weather function."""
    
    @patch('tools.requests.get')
    @patch.dict(os.environ, {'WEATHER_API_KEY': 'test_weather_key'})
    def test_successful_weather_fetch(self, mock_get):
        """Test successful weather data retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temp_c": 22.5,
                "condition": {
                    "text": "Partly cloudy"
                }
            }
        }
        mock_get.return_value = mock_response
        
        result = get_weather("Tokyo")
        
        assert "Tokyo" in result
        assert "22.5" in result
        assert "Partly cloudy" in result
    
    @patch('tools.requests.get')
    @patch.dict(os.environ, {'WEATHER_API_KEY': 'test_weather_key'})
    def test_weather_not_found(self, mock_get):
        """Test when weather information is not available."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        
        result = get_weather("InvalidCity")
        
        assert "Weather information not found" in result
    
    @patch('tools.requests.get')
    @patch.dict(os.environ, {'WEATHER_API_KEY': 'test_weather_key'})
    def test_weather_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        result = get_weather("Paris")
        
        assert "Error retrieving weather data" in result
    
    @patch('tools.requests.get')
    @patch.dict(os.environ, {'WEATHER_API_KEY': 'test_weather_key'})
    def test_weather_timeout(self, mock_get):
        """Test handling of timeout errors."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        result = get_weather("London")
        
        assert "Error retrieving weather data" in result


# =========================
# Test read_file_content
# =========================

class TestReadFileContent:
    """Tests for the read_file_content function."""
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        result = read_file_content("nonexistent_file.txt")
        assert "File not found" in result
    
    @patch('builtins.open', new_callable=mock_open, read_data="Hello World\nThis is a test file.")
    @patch('os.path.isfile', return_value=True)
    def test_read_txt_file(self, mock_isfile, mock_file):
        """Test reading a .txt file."""
        result = read_file_content("test.txt")
        assert "Hello World" in result
        assert "This is a test file." in result
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Markdown Header\n\nThis is markdown content.")
    @patch('os.path.isfile', return_value=True)
    def test_read_md_file(self, mock_isfile, mock_file):
        """Test reading a .md file."""
        result = read_file_content("test.md")
        assert "# Markdown Header" in result
        assert "This is markdown content." in result
    
    @patch('builtins.open', new_callable=mock_open, read_data="name,age\nJohn,30\nJane,25")
    @patch('os.path.isfile', return_value=True)
    def test_read_csv_file(self, mock_isfile, mock_file):
        """Test reading a .csv file."""
        result = read_file_content("test.csv")
        assert "name,age" in result
        assert "John,30" in result
    
    @patch('os.path.isfile', return_value=True)
    def test_unsupported_file_type(self, mock_isfile):
        """Test handling of unsupported file types."""
        result = read_file_content("test.xyz")
        assert "Unsupported file type" in result
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('os.path.isfile', return_value=True)
    def test_permission_error(self, mock_isfile, mock_file):
        """Test handling of permission errors."""
        result = read_file_content("protected.txt")
        assert "Permission denied" in result
    
    @patch('tools.pdfplumber.open')
    @patch('os.path.isfile', return_value=True)
    def test_read_pdf_file(self, mock_isfile, mock_pdf):
        """Test reading a PDF file."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "PDF content here"
        mock_pdf_context = MagicMock()
        mock_pdf_context.__enter__.return_value.pages = [mock_page]
        mock_pdf.return_value = mock_pdf_context
        
        result = read_file_content("test.pdf")
        assert "PDF content here" in result
    
    @patch('tools.docx.Document')
    @patch('os.path.isfile', return_value=True)
    def test_read_docx_file(self, mock_isfile, mock_doc):
        """Test reading a DOCX file."""
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph"
        
        mock_document = MagicMock()
        mock_document.paragraphs = [mock_para1, mock_para2]
        mock_doc.return_value = mock_document
        
        result = read_file_content("test.docx")
        assert "First paragraph" in result
        assert "Second paragraph" in result


# =========================
# Test write_file_content
# =========================

class TestWriteFileContent:
    """Tests for the write_file_content function."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='test_dir')
    def test_successful_write(self, mock_dirname, mock_makedirs, mock_file):
        """Test successful file write operation."""
        result = write_file_content('"output.txt", "Test content"')
        
        assert "Content written to output.txt successfully" in result
        mock_file.assert_called_once_with("output.txt", "w", encoding="utf-8")
        mock_file().write.assert_called_once_with("Test content")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='nested/path')
    def test_create_nested_directory(self, mock_dirname, mock_makedirs, mock_file):
        """Test that nested directories are created."""
        write_file_content('"nested/path/file.txt", "Content"')
        
        mock_makedirs.assert_called_once_with('nested/path', exist_ok=True)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='test_dir')
    def test_write_multiline_content(self, mock_dirname, mock_makedirs, mock_file):
        """Test writing multiline content."""
        result = write_file_content('"notes.txt", "Line 1\nLine 2\nLine 3"')
        
        assert "Content written to notes.txt successfully" in result
        mock_file().write.assert_called_once_with("Line 1\nLine 2\nLine 3")
    
    def test_invalid_input_format(self):
        """Test handling of invalid input format."""
        result = write_file_content('invalid input')
        assert "Error: Invalid format" in result
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='test_dir')
    def test_permission_error(self, mock_dirname, mock_makedirs, mock_file):
        """Test handling of permission errors."""
        result = write_file_content('"protected.txt", "Content"')
        assert "Permission denied" in result
    
    @patch('builtins.open', side_effect=IOError("Disk full"))
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='test_dir')
    def test_io_error(self, mock_dirname, mock_makedirs, mock_file):
        """Test handling of IO errors."""
        result = write_file_content('"test.txt", "Content"')
        assert "Error writing to file" in result


# =========================
# Test Integration Scenarios
# =========================

class TestIntegrationScenarios:
    """Integration tests that combine multiple functions."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.dirname', return_value='')
    def test_calculator_and_write(self, mock_dirname, mock_makedirs, mock_file):
        """Test calculating and writing result to file."""
        calc_result = calculator("100 * 0.25")
        assert calc_result == "25.0"
        
        write_result = write_file_content(f'"result.txt", "The answer is {calc_result}"')
        assert "Content written to result.txt successfully" in write_result
    
    @patch('tools.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key'})
    def test_search_returns_urls_for_scraping(self, mock_post):
        """Test that search results include URLs that can be scraped."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Article Title",
                    "snippet": "Article snippet",
                    "link": "https://example.com/article"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        result = search_internet("test article")
        
        assert "https://example.com/article" in result
        assert "Article Title" in result