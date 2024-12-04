from langchain_community.llms import Ollama

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.runnables import RunnablePassthrough
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
# from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

import regex as re

# Local LLM implementation
class LLM:
    
    template_messages = [
            SystemMessage("{system}"),
            MessagesPlaceholder(variable_name="history", optional=True),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    
    # print(template_messages)

    model = Ollama(model="llama3:latest")
    
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

    # prompt_template = ChatPromptTemplate.from_messages(template_messages)
    prompt_template = ChatPromptTemplate(
        messages=template_messages,
        # partial_variables={"format_instructions": format_instructions},
        validate_template=True,
    )
    # prompt = PromptTemplate(
    # template="answer the users question as best as possible.\n{format_instructions}\n{question}",
    # input_variables=["question"],
    # partial_variables={"format_instructions": format_instructions},
    # )
    # print(prompt_template + '\n')
    runnable = (prompt_template | model) # | output_parser)

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
                                                       "input": text}, 
                                                config={"configurable": {"session_id": session_id}})


if __name__ == '__main__':
    
    # Create limericks
    llm = LLM()
    
    system_message = "You are a helpful assistant. Give short answers."
    for i in range (2):
        text = input('\n')
        print(llm.answer(text, system_message, session_id=str(20)))
    system_message = "You are an unhelpful assistant. Answers very sarcastically."
    while(True):
        text = input('\n')
        print(llm.answer(text, system_message, session_id=str(20)))


