FastAPI Telegram ChatGPT Bot
============================

This project is built using ChatGPT-4.

Telegram bot integrated with ChatGPT, an AI language model. The bot is capable of processing user messages and generating AI-powered responses using ChatGPT. The bot provides multilingual support and can detect the language of the user's message to respond in the appropriate language. The bot also supports user authentication and data storage using a PostgreSQL database. The project is containerized using Docker and deployed with docker-compose. The codebase follows the principles of modular design and utilizes the aiogram library for Telegram bot development.

To run the bot using Docker:
===========================

- Clone the repository from GitHub to your local machine.
- create `.env` file environment variables (API keys, database URL, etc.).
- Run the command `docker-compose up --build` in the terminal to build and start the containers.

**Note:** Before running the bot, make sure that you have the necessary API keys and credentials for the external services used in the project, such as Telegram, OpenAI, and Google Cloud.

TODO: add more details
