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
Sebastian is a customizable AI assistant based on the Langchain framework and Python GSM Modem. It can be configured to have a specific personality and follows predefined goals. It utilizes Pinecone for vector storage of entities, Redis for caching and storing user data, and a GSM modem as the interface between SMS messages (UDH and long messages Supported) and a LLM. Sebastian can be deployed on a Raspberry Pi to provide an easily accessible personal assistant.

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

The project includes a feature called 'Conversational Modes', which forms part of the user data. You can modify the handle_sms function to flag certain words and switch to different modes. This was initially used for directly accessing another LLM locally.

Feel free to explore and modify the rest of the code, including the prompts and tools as per your requirements.

## Best Practice 
For continuous operation, add this application and the redis-server to your system processes. 

In the code i have included the implementation of Pinecone RC2 (Which is a lot faster) and the stable build, RC2 does not run on my Rasberry PI so is hashed out but can easily be activated again as it works on other enviroments. 

## To do
The objective of this project is to create a personal AI assistant that becomes more tailored to individual users over time, aiding in practical tasks and personal goals. Our future plans include:
- Add more useful tools 
- Refining the prompts for the agent and entity extraction/summarization
- Offload computing to a dedicated server which can use open source LLMs to process the conversations

## Credits
- Credit to [Langchain](https://github.com/hwchase17/langchain) for the framework