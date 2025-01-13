from langchain_community.llms import Ollama

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

class LLM:
    
    # Local LLM implementation
    model = Ollama(model="llama3:latest")

    # Creating the LLM runnable
    template_messages = [
        ("system", "{system}"),
        MessagesPlaceholder(variable_name="history", optional=True),
        ("human", "{input}"),
    ]
    prompt_template = ChatPromptTemplate.from_messages(template_messages)
    runnable = (prompt_template | model | StrOutputParser())

    def __init__(self) -> None:
        self.store = {}

        self.with_message_history = RunnableWithMessageHistory(
            self.runnable,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def answer(self, text, system_message, session_id=str(0)):
        return self.with_message_history.invoke(input={"system" : system_message,
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



