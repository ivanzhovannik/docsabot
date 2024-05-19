import logging
from functools import lru_cache
from fastapi import Depends
from openai import OpenAI, AsyncOpenAI
from typing import Annotated, Union

from config.config import settings


logger = logging.getLogger(__name__)

# Define singleton handler to use it as an app dependency
@lru_cache
def get_openai_client() -> Union[OpenAI, AsyncOpenAI]:
    api_key = settings.OPENAI.API_KEY
    asynchronous = settings.openai.asynchronous
    if asynchronous:
        logger.info("Using Asynchronous Mode")
        return AsyncOpenAI(api_key=api_key)
    else:
        logger.info("Using Synchronous Mode")
        return OpenAI(api_key=api_key)
    

OpenAIClientDependency = Annotated[Union[OpenAI, AsyncOpenAI], Depends(get_openai_client)]