from vectorstore import get_vectorstore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate

def dummy_llm(temperature=0):
    def _llm(*args, **kwargs):
        return "Response from DummyLLM"
    return _llm

retrieval_qa_chat_prompt = PromptTemplate(
    input_variables=["context", "input"],
    template=""" 
    You are an assistant who retrieves relevant venue details based on a user's query.  
    Only use the provided context below to generate your response.  
    Do *not* use any external knowledge, and do *not* invent new venues or details.  
    Your answer must be exclusively based on the venues listed in the context. 

    Context: {context}  
    Query: {input}  

    Based on the retrieved context, return the most relevant venues that match the query.  
    Make sure to only use the venue names and details provided in the context.
    """,
)

def search_venues(query, embedding_model):
    vector_store = get_vectorstore(embedding_model)

    if not vector_store:
        print("Error: Vector store not loaded.")
        return {"error": "Vector store error."}

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    try:
        test_documents = retriever.invoke(query)
    except Exception as e:
        print(f"Retrieval error: {e}")
        return {"error": f"Retrieval error: {e}"}

    combine_docs_chain = create_stuff_documents_chain(dummy_llm(), retrieval_qa_chat_prompt)
    qa_chain = create_retrieval_chain(retriever, combine_docs_chain)

    try:
        result = qa_chain.invoke({"input": query, "context": test_documents})
    except Exception as e:
        print(f"QA chain invocation error: {e}")
        return {"error": f"Invocation error: {e}"}

    return result
