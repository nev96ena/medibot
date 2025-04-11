import streamlit as st
import os
import time
from typing import TypedDict, Dict, Any, List, Literal
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.chat_models import ChatOllama
from langchain_community.utilities import SQLDatabase
from langgraph.graph import StateGraph, END
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from sqlalchemy import create_engine, text
import traceback

class AgentState(TypedDict):
    question: str
    chat_history: List[BaseMessage]
    question_type: Literal["sql", "rag", "general"] = None
    sql_query: str = None
    sql_result: Any = None
    rag_result: str = None
    final_answer: str = None
    error: str = None

@st.cache_resource
def initialize_agent_resources():
    resources = {}
    #LLM 
    ollama_model_name = "mistral:7b"
    try:
        resources['llm'] = ChatOllama(model=ollama_model_name, temperature=0.2)
    except Exception as e:
        st.error(f"Fatal Error initializing LLM: {e}")
        st.stop()
    
    # Database
    DATABASE_URL = "postgresql://nevenar:nevena123@localhost:5432/mydb"
    resources['db_engine'] = None
    resources['db'] = None
    resources['db_schema'] = "Schema not available."
    try:
        engine = create_engine(DATABASE_URL)
        db_conn = SQLDatabase(engine=engine)
        resources['db_engine'] = engine
        resources['db'] = db_conn
        table_names = db_conn.get_usable_table_names()
        relevant_tables = ['institutions', 'doctors']
        resources['db_schema'] = db_conn.get_table_info(relevant_tables)
    except Exception as e:
        st.warning(f"SQL Warning: DB connection/schema failed: {e}.")
        resources['db'] = None
        resources['db_engine'] = None
    
    #RAG 
    persist_directory = '../vector_store/db_chroma'
    model_name_embeddings = "sentence-transformers/all-MiniLM-L6-v2"
    resources['qa_chain'] = None
    if not os.path.exists(persist_directory):
        st.warning(f"RAG Warning: ChromaDB directory '{persist_directory}' not found. RAG tool will not work.")
    else:
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name_embeddings, model_kwargs={'device': 'cpu'}, encode_kwargs={'normalize_embeddings': False}
            )
            vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
            retriever = vectordb.as_retriever(search_kwargs={"k": 3})
            resources['qa_chain'] = RetrievalQA.from_chain_type(
                llm=resources['llm'], chain_type="stuff", retriever=retriever, return_source_documents=False
            )
        except Exception as e:
            st.warning(f"RAG Warning: Failed to load ChromaDB/Retriever/QA Chain: {e}. RAG tool may not work.")
    return resources

#Chat history 
def format_history_for_prompt(chat_history: List[BaseMessage]) -> str:
    history_str = ""
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            history_str += f"Human: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            history_str += f"Assistant: {msg.content}\n"
    return history_str.strip()

#graph 
def get_compiled_graph_app():

    resources = initialize_agent_resources()
    llm = resources.get('llm')
    db = resources.get('db')
    db_engine = resources.get('db_engine')
    db_schema = resources.get('db_schema')
    qa_chain = resources.get('qa_chain')

    if not llm:
        print("LLM not initialized. Cannot proceed.")
        return None

    classification_prompt_template = """Given the user question, chat history, and the database schema, classify the question into one of three categories: 'sql', 'rag', or 'general'. Use the history for context.

        Chat History:
        {chat_history}

        Database Schema (Doctors and Institutions):
        {schema}

        User Question: {question}

        Categories:
        - 'sql': The question asks for specific information *only* about doctors or institutions based on the schema (e.g., names, specializations, addresses, counts). Consider the history for pronoun resolution (e.g., 'their specialization').
        - 'rag': The question asks about general medical topics, diseases, symptoms, causes, treatments, prevention, wellness, etc. These answers are likely found in general medical summaries, not the specific database schema provided. Consider history for follow-up questions on medical topics.
        - 'general': The question is a greeting, small talk, asks about the AI itself, or is completely unrelated to medicine or the specific doctors/institutions in the database.

        Classification (respond with only 'sql', 'rag', or 'general'):"""

    classification_prompt = ChatPromptTemplate.from_template(classification_prompt_template)

    classification_chain = (
        RunnablePassthrough.assign(
            schema=lambda x: db_schema if db_schema else "Schema not available.",
            chat_history_str=lambda x: format_history_for_prompt(x.get("chat_history", []))
        )
        | classification_prompt
        | llm
        | StrOutputParser()
    )

# Classify query
    def classify_question_node(state: AgentState) -> Dict[str, Any]:
        question = state["question"]
        chat_history = state.get("chat_history", [])
        error = None
        try:
            classification_result = classification_chain.invoke({
                "question": question,
                "chat_history": chat_history
            }).strip().lower()

            print(f"Classification result: '{classification_result}'")
            if classification_result not in ["sql", "rag", "general"]:
                print(f"Warning: Unexpected classification result '{classification_result}'. Applying fallback logic.")
                if "doctor" in question.lower() or "institution" in question.lower() or "clinic" in question.lower() or "hospital" in question.lower():
                    classification_result = "sql"
                elif "symptom" in question.lower() or "disease" in question.lower() or "treatment" in question.lower() or "cause" in question.lower():
                    classification_result = "rag"
                else:
                    classification_result = "general"
                print(f"Fallback classification: '{classification_result}'")

            if classification_result == "sql" and not db:
                print("SQL classification chosen, but DB connection failed. Routing to general.")
                classification_result = "general"
                error = "Database connection is unavailable."
            elif classification_result == "rag" and not qa_chain:
                print("RAG classification chosen, but RAG chain initialization failed. Routing to general.")
                classification_result = "general"
                error = "RAG system is unavailable."

            return {"question_type": classification_result, "error": error}
        except Exception as e:
            print(f"Error during classification: {e}\n{traceback.format_exc()}")
            return {"question_type": "general", "error": f"Failed to classify question: {e}"}

   #SQL nodes 
    def generate_sql_node(state: AgentState) -> Dict[str, Any]:
        question = state["question"]

        if not db_schema:
            return {"error": "DB schema not available for SQL generation."}

        sql_prompt_template = """You are an expert in SQL. Write a SQL query based on the following question and schema. Do NOT use chat history for SQL generation, only the current question.

            Database Schema:
            {schema}

            Question:
            {question}

            Instructions:
            - Use PostgreSQL syntax.
            - Relevant tables: `doctors`, `institutions`. Do NOT prefix table names.
            - Use `ILIKE '%query%'` for case-insensitive text matching (e.g., `full_name`, `specialization`).
            - Join `doctors` and `institutions` using `doctors.institution_id = institutions.id` if needed.
            - Return only the raw SQL query, no explanations or markdown.

            SQL Query:"""
        sql_prompt = ChatPromptTemplate.from_template(sql_prompt_template)

        sql_generation_chain = (
            RunnablePassthrough.assign(schema=lambda x: db_schema)
            | sql_prompt
            | llm.bind(stop=["\nSQLResult:"])
            | StrOutputParser()
        )

        try:
            sql_query = sql_generation_chain.invoke({"question": question})
            sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()
            if not sql_query:
                raise ValueError("LLM failed to generate a valid-looking SQL query.")
            print(f"Generated SQL: {sql_query}")
            return {"sql_query": sql_query, "error": None}
        except Exception as e:
            print(f"Error during generating SQL: {e}\n{traceback.format_exc()}")
            return {"error": f"Failed to generate SQL: {e}"}

    def execute_sql_node(state: AgentState) -> Dict[str, Any]:
        if state.get("error"):
            print("Skipping SQL execution due to previous error.")
            return {}

        sql_query_raw = state.get("sql_query")
        if not sql_query_raw:
            return {"error": "No SQL query was found in state."}

        sql_query_cleaned = sql_query_raw.strip().replace("```sql", "").replace("```", "").strip()
        sql_query_cleaned = sql_query_cleaned.replace('\r\n', '\n').replace('\r', '\n')
        sql_query_cleaned = ' '.join(sql_query_cleaned.split())
        if sql_query_cleaned.endswith(';'):
            sql_query_cleaned = sql_query_cleaned[:-1]
        sql_query = sql_query_cleaned
        print(f"Executing SQL: {sql_query}")

        DATABASE_URL_NODE = "postgresql://nevenar:nevena123@localhost:5432/mydb"
        local_engine = None
        try:
            local_engine = create_engine(DATABASE_URL_NODE)
            with local_engine.connect() as connection:
                result_proxy = connection.execute(text(sql_query))
                fetched_results = result_proxy.fetchall()
                connection.close()

            if fetched_results:
                max_rows = 10
                formatted_results = [tuple(row) for row in fetched_results[:max_rows]]
                result_str = str(formatted_results)
                if len(fetched_results) > max_rows:
                    result_str += f"\n... (results truncated, total {len(fetched_results)} rows found)"
                print(f"SQL Result (truncated): {result_str}")
            else:
                result_str = "[]"
                print("SQL Result: No rows returned.")

            return {"sql_result": result_str, "error": None}

        except Exception as e:
            error_message = f"SQL Execution Error: {str(e)}"
            print(error_message)
            return {"error": error_message, "sql_result": None}
        finally:
            if local_engine:
                local_engine.dispose()

    def generate_answer_node_sql(state: AgentState) -> Dict[str, Any]:
        question = state["question"]
        chat_history = state.get("chat_history", [])
        sql_result = state.get("sql_result", "No result obtained from database.")
        error = state.get("error")

        prompt_input = {
            "question": question,
            "chat_history": format_history_for_prompt(chat_history),
            "sql_result": sql_result if not error else f"An error occurred: {error}",
        }

        answer_prompt_sql_template = """You are a helpful assistant. Based on the chat history, the user's question, and the result from the database query (or an error message), provide a final answer in natural language. If an error occurred, explain the problem conversationally.

            Chat History:
            {chat_history}

            User Question: {question}

            Database Result or Error:
            {sql_result}

            Final Answer (respond conversationally in the same language as the question):"""
        answer_prompt_sql = ChatPromptTemplate.from_template(answer_prompt_sql_template)

        answer_generation_chain_sql = answer_prompt_sql | llm | StrOutputParser()

        try:
            final_answer = answer_generation_chain_sql.invoke(prompt_input)
            print(f"Final Answer (SQL Path):\n{final_answer}")
            return {"final_answer": final_answer}
        except Exception as e:
            print(f"Error generating final answer (SQL): {e}\n{traceback.format_exc()}")
            return {"final_answer": f"Failed to generate the final answer. Error: {e}"}


    # RAG nodes 
    def execute_rag_node(state: AgentState) -> Dict[str, Any]:
        question = state["question"]

        if not qa_chain:
            print("RAG chain not initialized. Cannot execute RAG.")
            return {"error": "RAG system is unavailable.", "rag_result": None}

        try:
            print(f"Executing RAG for question: {question}")
            rag_response = qa_chain.invoke({"query": question})
            rag_result = rag_response.get('result', 'No specific information found in medical summaries.')
            print(f"RAG Result: {rag_result}")
            return {"rag_result": rag_result, "error": None}
        except Exception as e:
            print(f"Error during RAG execution: {e}\n{traceback.format_exc()}")
            return {"error": f"Failed during RAG execution: {e}", "rag_result": None}

    def generate_answer_node_rag(state: AgentState) -> Dict[str, Any]:
        question = state["question"]
        chat_history = state.get("chat_history", [])
        rag_result = state.get("rag_result", "No information retrieved.")
        error = state.get("error")

        prompt_input = {
            "question": question,
            "chat_history": format_history_for_prompt(chat_history),
            "rag_result": rag_result if not error else f"An error occurred during information retrieval: {error}",
        }

        answer_prompt_rag_template = """You are a helpful assistant. Based on the chat history, the user's question, and the retrieved information from medical documents (or an error message), provide a final answer in natural language. If an error occurred or no relevant information was found, state that clearly but politely.

            Chat History:
            {chat_history}

            User Question: {question}

            Retrieved Information or Error:
            {rag_result}

            Final Answer (respond conversationally in the same language as the question):"""
        answer_prompt_rag = ChatPromptTemplate.from_template(answer_prompt_rag_template)

        answer_generation_chain_rag = answer_prompt_rag | llm | StrOutputParser()

        try:
            final_answer = answer_generation_chain_rag.invoke(prompt_input)
            print(f"Final Answer (RAG Path):\n{final_answer}")
            return {"final_answer": final_answer}
        except Exception as e:
            print(f"Error generating final answer (RAG): {e}\n{traceback.format_exc()}")
            return {"final_answer": f"Failed to generate the final answer. Error: {e}"}

    # General node 
    def generate_answer_node_general(state: AgentState) -> Dict[str, Any]:
        question = state["question"]
        chat_history = state.get("chat_history", [])
        error = state.get("error")

        prompt_input = {
            "question": question,
            "chat_history": format_history_for_prompt(chat_history),
            "error": error if error else ""
        }

        prompt_text_template = ""
        if error:
            prompt_text_template = """You are a helpful assistant. Answer the user based on the chat history and the user's question. An internal error occurred processing the request: "{error}". Apologize and inform the user you couldn't fully process it due to an internal issue.

            Chat History:
            {chat_history}

            User Question: {question}

            Answer:"""
        else:
            prompt_text_template = """You are a helpful assistant. Answer the user's question directly and conversationally, using the chat history for context if needed.

            Chat History:
            {chat_history}

            User Question: {question}

            Answer:"""

        general_answer_prompt = ChatPromptTemplate.from_template(prompt_text_template)
        general_answer_chain = general_answer_prompt | llm | StrOutputParser()

        try:
            final_answer = general_answer_chain.invoke(prompt_input)
            print(f"Final Answer (General/Fallback Path):\n{final_answer}")
            return {"final_answer": final_answer}
        except Exception as e:
            print(f"Error generating final answer (General): {e}\n{traceback.format_exc()}")
            return {"final_answer": f"Failed to generate general/fallback answer. Error: {e}"}

    # Build graph

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("classify_question", classify_question_node)
    graph_builder.add_node("generate_sql", generate_sql_node)
    graph_builder.add_node("execute_sql", execute_sql_node)
    graph_builder.add_node("generate_answer_sql", generate_answer_node_sql)
    graph_builder.add_node("execute_rag", execute_rag_node)
    graph_builder.add_node("generate_answer_rag", generate_answer_node_rag) # New node
    graph_builder.add_node("generate_answer_general", generate_answer_node_general)

    graph_builder.set_entry_point("classify_question")

    def route_after_classification(state: AgentState) -> Literal["generate_sql", "execute_rag", "generate_answer_general"]:
         q_type = state.get("question_type")
         error = state.get("error")
         print(f"Routing decision based on type: {q_type}, error: {error}")
         if error and "classification" in error.lower(): return "generate_answer_general"
         if q_type == "sql": return "generate_sql"
         if q_type == "rag": return "execute_rag"
         return "generate_answer_general"

    graph_builder.add_conditional_edges("classify_question", route_after_classification, {
        "generate_sql": "generate_sql",
        "execute_rag": "execute_rag",
        "generate_answer_general": "generate_answer_general"
    })

    graph_builder.add_edge("generate_sql", "execute_sql")
    graph_builder.add_edge("execute_sql", "generate_answer_sql")
    graph_builder.add_edge("generate_answer_sql", END)

    graph_builder.add_edge("execute_rag", "generate_answer_rag") 
    graph_builder.add_edge("generate_answer_rag", END) 
    
    graph_builder.add_edge("generate_answer_general", END)

    try:
        app = graph_builder.compile()
        print("Graph compiled successfully.")
        return app
    except Exception as e:
        print(f"Error compiling graph: {e}\n{traceback.format_exc()}")
        st.error(f"Failed to compile the agent graph: {e}")
        st.stop()