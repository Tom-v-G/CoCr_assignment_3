from langchain_community.llms import Ollama

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import ResponseSchema, PydanticOutputParser
from langchain_core.output_parsers import StrOutputParser
# from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from pydantic import BaseModel, Field
from typing import Union

import regex as re

# Local LLM implementation
class LLM:
    
   
    template_messages = [
        ("system", "{system}"),
        # SystemMessage("{format_instructions}"),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{input}"),
    ]

    # print(template_messages)

    model = Ollama(model="llama3:latest")
    
    # output parser stuff
    
    class Joke(BaseModel):
        """Joke to tell the user"""
        setup: str = Field(description="The setup of a the joke")
        punchline: str = Field(description="The punchline to the joke")
    
    class MovieRating(BaseModel):
        """Suggest a movie and provide a rating"""
        movie: str = Field(description="the movie")
        rating: str = Field(description="your rating of the movie")

    # class FinalResponse(BaseModel):
    #     final_output: Union[Joke, MovieRating]
        
    
    # output_parser = PydanticOutputParser(pydantic_object=Joke)
    # format_instructions = output_parser.get_format_instructions()
    # print(format_instructions)
    # # print(format_instructions)

    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # response_schemas = [
    #     # ResponseSchema(
    #     #     name="text", 
    #     #     description="Human readable answer to the user's question"
    #     # ),
    #     # ResponseSchema(
    #     #     name="difficulty",
    #     #     description="Difficulty of the question asked by the user. Should be a number between 0 and 10.",
    #     # ),
    # ]
    # output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    # format_instructions = output_parser.get_format_instructions()
    # print(format_instructions)

    prompt_template = ChatPromptTemplate.from_messages(template_messages)
    # print(prompt_template)
    # prompt_template = ChatPromptTemplate(
    #     messages=template_messages,
        # input_variables=["input", "system"]
        # partial_variables={"format_instructions": format_instructions},
        # validate_template=True,
    # )

    # print(prompt_template)
    # prompt = ChatPromptTemplate(
    # template="answer the users question as best as possible.\n{format_instructions}\n{question}",
    # input_variables=["question"],
    # partial_variables={"format_instructions": format_instructions},
    # print(prompt_template + '\n')
    # runnable = (prompt_template | model ) # | output_parser)
    runnable = (prompt_template | model | StrOutputParser())

    def __init__(self) -> None:
        self.store = {}

        self.with_message_history = RunnableWithMessageHistory(
            self.runnable,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        # print(self.with_message_history)

    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def answer(self, text, system_message, session_id=str(0)):
        # print(self.with_message_history)
        return self.with_message_history.invoke(input={"system" : system_message,
                                                    #    "format_instructions" : self.format_instructions,
                                                       "input": text}, 
                                                config={"configurable": {"session_id": session_id}})


if __name__ == '__main__':
    
    llm = LLM()


    system_message = """You are a D&D 5e dungeonmaster. Start a new text-based rpg adventure. Describe the setting and the player character. Also fill in the blanks in the python dictionary below:
    player = { 
        name= ,
        level= ,
        strength= ,
        dexterity= ,
        constitution= ,
        intelligence= ,
        wisdom= ,
        charisma= ,
    }
    """
    for i in range (1):
        text = input('\n')
        print(llm.answer("", system_message, session_id=str(20)))
    
    while(True):
        system_message = """You are the assistant of a D&D 5e dungeonmaster. Based on a the human input, choose which one of the following scenario's is happening.
        The options are: 
        - Combat
        - Exploration
        - Conversation
        Format your output as a single word. Example:
        ```
        Combat
        ```
        """
        # while(True):
        text = input('\n')
        print(llm.answer(text, system_message, session_id=str(20)))

        system_message = """You are a D&D 5e dungeonmaster. Based on your last response, choose how the story continues."""
        print(llm.answer("", system_message, session_id=str(20)))



