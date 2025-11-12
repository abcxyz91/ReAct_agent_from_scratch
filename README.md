# ReAct Agent 🤖

A Python-based ReAct (Reasoning and Acting) agent that combines language model reasoning with tool execution to solve complex tasks. The agent operates in a loop of Thought → Action → Observation until it reaches a final answer.

## 🌟 Features

- **Intelligent Reasoning**: Uses OpenAI's GPT models to reason through problems step-by-step
- **Multiple Tools**: Includes 6 tools for various tasks
- **Flexible Architecture**: Easy to extend with custom tools and actions
- **Comprehensive Testing**: Full test coverage with pytest

## 🛠️ Available Tools

1. **calculator** - Perform mathematical computations
2. **search_internet** - Search the web using Serper.dev API
3. **scrape_content** - Extract clean text content from web pages
4. **get_weather** - Retrieve current weather information
5. **read_file_content** - Read various file formats (.txt, .md, .csv, .pdf, .docx)
6. **write_file_content** - Write or overwrite content to files

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Serper.dev API key (for web search)
- WeatherAPI key (for weather information)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd react-agent
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
```

### Getting API Keys

- **OpenAI API Key**: Sign up at [platform.openai.com](https://platform.openai.com)
- **Serper API Key**: Get a free key at [serper.dev](https://serper.dev)
- **Weather API Key**: Sign up at [weatherapi.com](https://weatherapi.com)

## 💻 Usage

### Basic Usage

Run the agent interactively:
```bash
python main.py
```

Then enter your questions at the prompt:
```
Enter your question: What is 25% of 160?
Enter your question: Find the current gold price per ounce and convert it to VND
Enter your question: What's the weather in Tokyo?
Enter your question: exit
```
### Customizing the Agent

You can customize the model and temperature:
```python
agent = Agent(
    system=system_prompt,
    model="gpt-4",  # Use GPT-4 instead of GPT-3.5
    temperature=0.7  # Adjust creativity (0.0 = deterministic, 1.0 = creative)
)
```

## 📝 Example Sessions

### Example 1: Simple Calculation
```
User: What is 25% of 160?

Thought: I need to calculate 25 percent of 160.
Action: calculator: 0.25 * 160
PAUSE

Observation: 40

Answer: 40
```

### Example 2: Web Search + Calculation
```
User: Find the current gold price per ounce and convert it to VND if 1 USD = 25,000 VND.

Thought: First, I need to find the gold price per ounce in USD.
Action: search_internet: current gold price per ounce USD
PAUSE

Observation: The current gold price is 2,350 USD per ounce.

Thought: Now I should multiply 2,350 by 25,000 to convert it into VND.
Action: calculator: 2350 * 25000
PAUSE

Observation: 58,750,000

Answer: The current gold price is approximately 58.75 million VND per ounce.
```

### Example 3: Web Scraping
```
User: Summarize the main points from https://example.com/article

Thought: I have a direct URL, so I should scrape it.
Action: scrape_content: https://example.com/article
PAUSE

Observation: [Full article text here]

Answer: The article discusses...
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest test_tools.py -v

# Run with coverage report
pytest test_tools.py --cov=tools --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 📁 Project Structure

```
react-agent/
│
├── main.py              # Main agent class and execution loop
├── system_prompt.py     # ReAct system prompt and examples
├── tools.py             # Tool implementations
├── test_tools.py        # Comprehensive test suite
├── requirements.txt     # Python dependencies
├── .env                 # API keys (create this file)
└── README.md           # This file
```

## 🔧 Adding Custom Tools

To add a new tool:

1. **Define the tool function in `tools.py`**:
```python
def my_custom_tool(input: str) -> str:
    """
    Description of what your tool does.
    Input: Description of expected input format.
    """
    try:
        # Your tool logic here
        result = process_input(input)
        return str(result)
    except Exception as e:
        return f"Error in my_custom_tool: {e}"
```

2. **Register the tool in `known_actions` dictionary**:
```python
known_actions = {
    "calculator": calculator,
    "search_internet": search_internet,
    # ... other tools ...
    "my_custom_tool": my_custom_tool,  # Add your tool here
}
```

3. **Update the system prompt in `system_prompt.py`**:
```python
## 7. my_custom_tool
Description of when to use this tool.
Example:
Action: my_custom_tool: <input>
```

4. **Write tests in `test_tools.py`**:
```python
class TestMyCustomTool:
    def test_basic_functionality(self):
        result = my_custom_tool("test input")
        assert "expected output" in result
```

## ⚙️ Configuration

### Model Selection
Edit `main.py` to change the default model:
```python
agent = Agent(system=system_prompt, model="gpt-4")  # Use GPT-4
```

### Temperature Settings
Adjust the temperature for different behaviors:
- `0.0`: Deterministic, focused responses
- `0.7`: Balanced creativity and consistency
- `1.0`: More creative and varied responses

### Max Turns
Adjust the maximum reasoning loops in `agent.run()`:
```python
result = agent.run(user_query, max_turns=10)  # Allow up to 10 tool uses
```

## 🐛 Troubleshooting

### API Key Issues
```
Error: SERPER_API_KEY not found in environment variables
```
**Solution**: Make sure your `.env` file exists and contains all required API keys.

### Module Import Errors
```
ModuleNotFoundError: No module named 'openai'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

### File Permission Errors
```
Error: Permission denied to write file
```
**Solution**: Ensure you have write permissions for the target directory.

## 📚 Resources

- [ReAct Paper](https://arxiv.org/abs/2210.03629) - Original research paper
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Serper.dev Documentation](https://serper.dev/docs)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ReAct framework by Yao et al.
- OpenAI for providing the GPT API
- All the open-source libraries used in this project

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Made with ❤️ using Python and OpenAI