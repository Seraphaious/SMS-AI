from langchain.agents import Tool
from langchain.tools import BaseTool, StructuredTool
from langchain.utilities import WikipediaAPIWrapper


def wikipedia_tool_func(input=""):
    wikipedia = WikipediaAPIWrapper()
    results = wikipedia.run(input)
    return results

wikipedia_tool = Tool(
    name="wikipedia", 
    func=wikipedia_tool_func,
    description="Useful for when you need to look up a topic, country or person on wikipedia, only use when the user mentions 'use wikipedia'"
)

tools = [wikipedia_tool]
