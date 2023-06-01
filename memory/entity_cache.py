from typing import Any, Dict, List

from langchain.memory.chat_memory import BaseChatMemory
from langchain.schema import BaseMessage, get_buffer_string


import logging
from abc import ABC, abstractmethod
from itertools import islice
from typing import Any, Dict, Iterable, List, Optional
from dotenv import load_dotenv
from pathlib import Path

from memory.prompt import (
    ENTITY_EXTRACTION_PROMPT,
    ENTITY_SUMMARIZATION_PROMPT,
)

from pydantic import Field

from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory


from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseMessage, get_buffer_string
from langchain.base_language import BaseLanguageModel

from memory.redis_ops import redis_client
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_REGION, INDEX
from initialization import embeddings


import os
import sys
import redis
import asyncio
import threading




logger = logging.getLogger(__name__)


import pinecone

pinecone.init(api_key=PINECONE_API_KEY, enviroment=PINECONE_REGION) # One time init


class BaseEntityStore(ABC):
    @abstractmethod
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get entity value from store."""
        pass

    @abstractmethod
    def set(self, key: str, value: Optional[str]) -> None:
        """Set entity value in store."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete entity value from store."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if entity exists in store."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all entities from store."""
        pass



class PineconeEntityStore(BaseEntityStore):
    def __init__(
        self,
        index_name: str = INDEX,  
        namespace: Optional[str] = None,
        usrNumber: Optional[str] = None,
        embeddings: Optional[str] = embeddings,
        redis_client: Optional[redis.StrictRedis] = redis_client,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)


        # Pinecone RC2
        # from initialization import embeddings, client
        # from pinecone import Vector

        # indexes = client.list_indexes()
        
        # if index_name not in indexes:
            # create the index if it doesn't exist
            # client.create_index(index_name, dimension=1536)
        
        # try:
            # self.index = client.get_index(index_name)
        # except ConnectionError as e:
            # print("ConnectionError occurred!")
            # print("Checking indexes again:")
            # print("Current indexes: ", client.list_indexes())
            # print("Current index info: ", client.describe_index(index_name))
            # raise e


        self.index = pinecone.Index(INDEX)

        self.embeddings = embeddings 
        self.namespace = usrNumber


        if usrNumber is not None and redis_client is not None:
            self.redis_cache = RedisCache(usrNumber, redis_client)
        else:
            self.redis_cache = None

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        # Check for cached value first
        if self.redis_cache:
            cached_value = self.redis_cache.get(key)
            if cached_value is not None:
                print(f"Using cached result for key '{key}': {cached_value}")
                return cached_value


        query_embedding = self.embeddings.embed_query(key)
        query_response = self.index.query(
            top_k=1,
            include_values=True,
            include_metadata=True,
            vector=query_embedding,
            namespace=self.namespace,
        )


        if len(query_response.matches) > 0:
            for result in query_response.matches:
                value = result.metadata["metadata"]  # Extracting inner metadata string
                print(f"Found result for key '{key}': {value}")

                # Cache the result
                if self.redis_cache:
                    self.redis_cache.set(key, value)

                return value
            print(f"No result found for key '{key}'")
            return default


        # Pinecone RC2
        # query_embedding = self.embeddings.embed_query(key)
        # query_response = self.index.query(
            # top_k=1,
            # include_values=True,
            # include_metadata=True,
            # sparse_values = None, # optional sparse values of the query vector
            # values=query_embedding,
            # namespace=self.namespace,
        # )

        # Pinecone RC2
        # query_response itself is a list of QueryResult objects
        # for result in query_response:
            # value = result.metadata.get("metadata", default)
            # print(f"Found result for key '{key}': {value}")


            # Cache the result
            # if self.redis_cache:
                # self.redis_cache.set(key, value)

            # return value
        # print(f"No result found for key '{key}'")
        # return default

    def set(self, key: str, value: Optional[str]) -> None:
        if not value:
            return self.delete(key)

        if "new information" in value.lower():
            print(f"Skipping upsert for key '{key}' as value contains 'new information': {value}")
            return

        entity_embedding = self.embeddings.embed_query(value)
        self.index.upsert(vectors=[(key, entity_embedding, {"metadata": value})], namespace=self.namespace)
        print(f"Upserted value '{value}' for key '{key}'")


    def delete(self, key: str) -> None:
        self.index.delete(ids=[key], namespace=self.namespace)
        print(f"Deleted key '{key}'")

    def exists(self, key: str) -> bool:
        query_embedding = self.embeddings.embed_query(key)
        query_response = self.index.query(
            top_k=1,
            include_values=False,
            include_metadata=False,
            vector=query_embedding,
            namespace=self.namespace,
        )

        query_result = query_response.matches
        print(f"Key '{key}' exists: {bool(query_result)}")
        return bool(query_result)

    def clear(self) -> None:
        self.index.delete_all(namespace=self.namespace)
        print("Cleared all entries")

    def batch_upsert(self, data: List[tuple[str, str]]) -> None:
        vectors = []
        for key, value in data:
            if "new information" in value.lower():
                print(f"Skipping upsert for key '{key}' as value contains 'new information': {value}")
                continue
            entity_embedding = self.embeddings.embed_query(value)
            vectors.append((key, entity_embedding, {"metadata": value}))
        if vectors:
            self.index.upsert(vectors=vectors, namespace=self.namespace)
            print(f"Upserted {len(vectors)} values")
        
class RedisCache:
    def __init__(self, usrNumber: str, redis_client: redis.StrictRedis):
        self.client = redis_client
        self.usrNumber = usrNumber

    def get(self, key: str) -> Optional[str]:
        cache_key = f"{self.usrNumber}:{key}"
        value = self.client.get(cache_key)
        if value is not None:
            return value.decode()
        return None

    def set(self, key: str, value: str, ttl: int = 300) -> None:
        cache_key = f"{self.usrNumber}:{key}"
        self.client.set(cache_key, value, ex=ttl)

    def delete(self, key: str) -> None:
        cache_key = f"{self.usrNumber}:{key}"
        self.client.delete(cache_key)


class ConversationEntityCache(BaseChatMemory):
    """Buffer for storing conversation memory."""

    human_prefix: Optional[str] = None
    ai_prefix: Optional[str] = None
    llm: BaseLanguageModel
    entity_extraction_prompt: BasePromptTemplate = ENTITY_EXTRACTION_PROMPT
    entity_summarization_prompt: BasePromptTemplate = ENTITY_SUMMARIZATION_PROMPT
    entity_cache: List[str] = []    
    entity_store: BaseEntityStore = Field(default_factory=PineconeEntityStore)


    memory_key: str = "history"  #: :meta private:
    k: int = 3

    def __init__(
        self,
        human_name: str,
        bot_name: str,
        usrNumber: Optional[str] = None,  # Add this argument
        redis_client: Optional[redis.StrictRedis] = redis_client,  # Add this argument
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.human_prefix = human_name
        self.ai_prefix = bot_name  

        # Update the PineconeEntityStore with the provided namespace
        if usrNumber is not None:
            self.entity_store.namespace = usrNumber
        if redis_client is not None:
            self.entity_store.redis_cache = RedisCache(usrNumber, redis_client)



    @property
    def buffer(self) -> List[BaseMessage]:
        """String buffer of memory."""
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.
        :meta private:
        """
        return [self.memory_key]



    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        chain = LLMChain(llm=self.llm, prompt=self.entity_extraction_prompt)
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        buffer_string = get_buffer_string(
            self.buffer[-self.k * 2 :],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        output = chain.predict(
            history=buffer_string,
            input=inputs[prompt_input_key],
        )
        if output.strip() == "NONE":
            entities = []
        else:
            entities = [w.strip() for w in output.split(",")]
        entity_summaries = {}
        for entity in entities:
            entity_summaries[entity] = self.entity_store.get(entity, "")
        self.entity_cache = entities

        if self.return_messages:
            buffer: Any = self.buffer[-self.k * 2 :]
        else:
            buffer = buffer_string
        return {
            self.memory_key: buffer,
            "entities": entity_summaries,
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        super().save_context(inputs, outputs)

        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key

        buffer_string = get_buffer_string(
            self.buffer[-self.k * 2 :],
            human_prefix=self.human_prefix,
            ai_prefix=self.ai_prefix,
        )
        input_data = inputs[prompt_input_key]
        chain = LLMChain(llm=self.llm, prompt=self.entity_summarization_prompt)

        self.start_async_save_context(chain, buffer_string, input_data)

    def start_async_save_context(self, chain, buffer_string, input_data):
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.store_vectors(chain, buffer_string, input_data))
            loop.close()

        thread = threading.Thread(target=run_async)
        thread.start()

    async def store_vectors(self, chain, buffer_string, input_data):
        """Stores vectors for entities asynchronously."""

        for entity in self.entity_cache:
            existing_summary = self.entity_store.get(entity, "")
            output = chain.predict(
                summary=existing_summary,
                entity=entity,
                history=buffer_string,
                input=input_data,
            )
            self.entity_store.set(entity, output.strip())

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
        self.entity_store.clear()
