from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_REGION, INDEX
from langchain.chat_models import ChatOpenAI
from config import OPENAI_API_KEY
from langchain.agents import AgentExecutor
from langchain.agents.structured_chat.base import StructuredChatAgent

from memory.entity_cache import ConversationEntityCache
from initialization import wizard_7b, manticore_13b, turbo_llm, memory_llm, detail_llm
from agent.tools import tools
from langchain import LLMChain


agents = {}
usrNumber = "+447851043000"
user_name = "Ben"
bot_name = "Dover"
user_obj = """To help with homework"""
bot_personality = """Funny"""



while True:

        usrMessage = input("Enter your message (type 'exit' to quit): ").lower()
        if usrMessage == "exit":
            break

        from agent import prompt

        memory = ConversationEntityCache(
            usrNumber=usrNumber, memory_key="chat_history", llm=memory_llm, 
            input_key="input", human_name=user_name, bot_name=bot_name, return_messages=True,
        )

        tool_names = [tool.name for tool in tools]
        llm_chain = LLMChain(llm=detail_llm, prompt=prompt.prompt)
        agent = StructuredChatAgent(llm_chain=llm_chain, allowed_tools=tool_names)

        agent = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            max_iterations=3,
            verbose=True,
            early_stopping_method="generate",
            memory=memory,
            agent_kwargs={
                'input_variables': ["input", "chat_history", "entities",  "agent_scratchpad",
                                    "user_name", "user_obj", "bot_personality", "bot_name"],
            },
        )


        usrMessage = agent({
                'input': usrMessage,
                'usrNumber': usrNumber,
                'user_name': user_name,
                'user_obj': user_obj,
                'bot_personality': bot_personality,
                'bot_name': bot_name
            })



print("Goodbye!")