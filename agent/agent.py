from langchain.agents import AgentExecutor
from langchain.agents.structured_chat.base import StructuredChatAgent
from memory.entity_cache import ConversationEntityCache
from langchain import LLMChain



from agent.tools import tools
from agent import prompt
from initialization import turbo_llm


agents = {}

def get_conversational_agent(usrNumber, user_name, user_obj, bot_personality, bot_name):
    if usrNumber not in agents:
        agents[usrNumber] = create_conversational_agent(user_name, user_obj, bot_personality, bot_name, usrNumber)
    return agents[usrNumber]


def create_conversational_agent(user_name, user_obj, bot_personality, bot_name, usrNumber):
    

    memory = ConversationEntityCache(
        usrNumber=usrNumber, memory_key="chat_history", llm=turbo_llm, 
        input_key="input", human_name=user_name, bot_name=bot_name, return_messages=True,
    )

    tool_names = [tool.name for tool in tools]
    llm_chain = LLMChain(llm=turbo_llm, prompt=prompt.prompt)
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
    return agent



