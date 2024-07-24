# Web Scraper to RAG LLM

This project serves as the MVP of a SaaS solution that scrapes all sub-URLs from a given URL and uses the retrieved content as context for creating chatbots with knowledge about the contents. It utilizes Retrieval-Augmented Generation (RAG) techniques to enhance the chatbot's capabilities.

## Architecture
The architecture of the application is illustrated below:

<div align="center">
  <img height="650" alt="Diagram" src="diagram.png">
</div>

## Functionality

Upon receiving a URL, the application is capable of scraping the content of all sub-URLs within the domain. All scraped content is stored in PINECONE, an online vector database.

Using this information, we create an endpoint to answer questions based on the scraped content. 

## Usage

This project was used with the official Lambda Forge documentation and is now powering the official Lambda Forge Telegram bot. You can interact with the bot here:

<div align="center">
  <a href="https://web.telegram.org/a/#6950159714">
    @LambdaForgeBot
  </a>
</div>

<br>

