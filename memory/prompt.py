# flake8: noqa
from langchain.prompts.prompt import PromptTemplate


_DEFAULT_ENTITY_EXTRACTION_TEMPLATE = """You are an AI assistant reading the transcript of a conversation between an AI and a human. 

From the last line of conversation, extract key nouns and in addition to key conversational themes which may include, but are not limited to people, places, events, likes, dislikes, future plans, relations and concepts in their life which would be helpful in understanding them.

Do not extract common knoweldge. 

The conversation history is provided just in case of a coreference (e.g. "What do you know about him" where "him" is defined in a previous line) -- ignore items mentioned there that are not in the last line.

Return the output as a single comma-separated list, or NONE if there is nothing of note to return (e.g. the user is just issuing a greeting or having a simple conversation).

EXAMPLE
Conversation history:
Person #1: how's it going today?
AI: "It's going great! How about you?"
Person #1: good! busy working on Langchain. lots to do.
AI: "That sounds like a lot of work! What kind of things are you doing to make Langchain better?"
Last line:
Person #1: i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff.
Output: Langchain
END OF EXAMPLE

EXAMPLE
Conversation history:
Person #1: how's it going today?
AI: "It's going great! How about you?"
Person #1: good! busy working on Langchain. lots to do.
AI: "That sounds like a lot of work! What kind of things are you doing to make Langchain better?"
Last line:
Person #1: i'm trying to improve Langchain's interfaces, the UX, its integrations with various products the user might want ... a lot of stuff. I'm working with Person #2.
Output: Langchain, Person #2
END OF EXAMPLE

Conversation history (for reference only):
{history}
Last line of conversation (for extraction):
Human: {input}

Output:"""
ENTITY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_ENTITY_EXTRACTION_TEMPLATE
)

_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE = """You are an AI assistant helping a human keep track of important parts of their life. Update the summary of the provided entity in the "Entity" section based on the last line of your conversation with the human, you should refernece the human by name. If you are writing the summary for the first time, return a single sentence.
If there is already an existing summary of an enitity you should decide if the information is about the same or different topic. If there is nothing new to add to the summary, return the existing summary unchanged. When updating an existing summary, the summary should be updated, summerising both the existing and new summary, 
Where possible you should attibute the summary to a new noun, as opposed to constantly updating the existing ones. 

Full conversation history (for context):
{history}

Entity to summarize:
{entity}

Existing summary of {entity}:
{summary}

Last line of conversation:
Human: {input}
Updated summary: """

ENTITY_SUMMARIZATION_PROMPT = PromptTemplate(
    input_variables=["entity", "summary", "history", "input"],
    template=_DEFAULT_ENTITY_SUMMARIZATION_TEMPLATE,
)


