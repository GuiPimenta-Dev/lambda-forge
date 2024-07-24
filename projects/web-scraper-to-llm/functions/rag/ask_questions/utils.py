from langchain_community.vectorstores import Pinecone as VectorStore


def augment_prompt(index, embed_model, query: str):
    text_field = "text"

    vectorstore = VectorStore(index, embed_model.embed_query, text_field)
    # get top 3 results from knowledge base
    results = vectorstore.similarity_search(query, k=3)
    # get the text from the results
    source_knowledge = "\n".join([x.page_content for x in results])
    # feed into an augmented prompt
    augmented_prompt = f"""Using the contexts below, answer the query.

    Contexts:
    {source_knowledge}

    Query: {query}"""
    return augmented_prompt
