import os
from dotenv import load_dotenv
from retriever import load_vector_store
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

load_dotenv()

def build_chatbot():
    retriever = load_vector_store().as_retriever(search_type="similarity", k=3)

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.7
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""You are a helpful restaurant assistant. Use the context to answer the user question.

Context:
{context}

Question: {question}

Answer:"""
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain
