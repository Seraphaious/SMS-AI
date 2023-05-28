![made-with-python](https://img.shields.io/badge/Made%20with-Python3-brightgreen)

<!-- LOGO -->
<br />
<h1>
<p align="center">
  <img src="https://github.com/Seraphaious/SMS-AI/blob/main/logo.png?raw=true" alt="Logo" width="400" height="400">
  <br>Sebastian
</h1>
  <p align="center">
    A customizable SMS AI Assistant with infinite and persistent memory.
    <br />
    </p>
</p>
<p align="center">
  <a href="#about-the-project">About The Project</a> •
  <a href="#Installing">How To Use</a> •
  <a href="#Usage">Usage</a> •
  <a href="#best-practice">Best Practice</a> •
  <a href="#to-do">To do</a> •
</p>  

<p align="center">
  
</p>                                                                                                                             
                                                                                                                                                      
## About The Project
Sebastian is a customizable AI assistant based on the Langchain framework, Python GSM Modem, and supports UDH (SMS exceeding 160 characters). The intention of this project was to create a personal assistant reminiscent of the 'Young Ladies Illustrated Primer', which, rather than simply assisting with administrative tasks, would help users build the skills they needed to progress towards their goals. What these goals are, are defined by the user.

This is achieved primarily through two means. The first is a local Redis DB that stores user input variables such as their name, the personality they would like the assistant to have, and their goal. As they are stored in Redis, they are persistent and these form part of the system prompt. The other method is through embeddings and vectorization. Using a custom version of entity memory from the Langchain framework, key information from conversations is extracted, embedded, and stored in a Pinecone namespace associated with the user number. In combination with a small local buffer window memory, this facilitates near-infinite memory which will, through frequent conversation, build up more unique and personal responses without running into token usage issues.

## Installing
This application was built using Python 3.10.11. While it should be compatible with future package updates from Langchain etc., we recommend using a virtual environment for streamlined package management.

Ensure everything is up to date:
```py
sudo apt-get update && sudo apt-get upgrade

sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev tar wget vim
```

Install Redis (Install setps will vary depending on OS, check Redis docs):
```py
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get install redis

```

Import from GitHub:
```py
git clone https://github.com/Seraphaious/SMS-AI.git
cd SMS-AI
pip install -r requirements.txt
python main.py
```



## Usage
This code is designed to work in conjunction with a 4G SMS modem. We recommend using the OSTENT WCDMA Modem available on Alibaba. For testing purposes, you can use debug.py, which replicates most functionalities without requiring an SMS Modem.

Local models: Althought they struggle to follow agent prompts, are supported. To use them: `export MODEL_PATH=/path/to/your/model/directory` and in `initialization.py` set `INITIALIZE_MODELS = True`. 

Setting enviroment variables: Create a .env file inside add:
`OPENAI_API_KEY`
`PINECONE_API_KEY`
`PINECONE_REGION`
`PORT`
`BAUD_RATE`
`REDIS_HOST`
`REDIS_PORT`
`REDIS_DB`
`WHITELISTED_NUMBERS`
`PINECONE_INDEX`

The project includes a feature called 'Conversational Modes', which forms part of the user data. You can modify the handle_sms function to flag certain words and switch to different modes. This was initially used for directly accessing another LLM locally. There are also quality of life improvements, such as using UDH to concatenate longer SMS messages, using Redis to cache frequently accessed vectors, asynchronous upserting, and only accepting messages from whitelisted numbers.

## Best Practice 
For continuous operation, add this application and the redis-server to your system processes. 

In the code i have included the implementation of Pinecone RC2 (Which is a lot faster) and the stable build, RC2 does not run on my Rasberry PI so is hashed out but can easily be activated again as it works on other enviroments. 

If you want to reset your Pinecone index and Redis DB information, you can send 'My creation was a mistake', and all variables will be deleted and the setup reinitialized.

## To do
This project is, in theory, production ready. User data is partitioned based on the number, both in Redis and Pinecone, and it would be simple enough to add multi-threading with a few modems, each handling a certain amount of users. The main barriers are API costs and bottlenecks when using OpenAI and the already aligned models which detract from truly unique user experiences. In the future, I hope these can be overcome by:
- Offloading computing to a dedicated server which can use open-source LLMs to process the conversations.
- I would also like to add more useful tools.
- More work could also be done on refining the prompts for the agent and entity extraction/summarization, even fine-tuning a model specifically for this to improve speed.

## Credits
- Credit to [Langchain](https://github.com/hwchase17/langchain) for the framework
- Credit to Neal Stephenson for the fantastic book "Diamond Age" which gave me the idea