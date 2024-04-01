# OpenAI-API-Terminal-Chatbot
An OpenAI powered chatbot, powered by your own API key. Simple. Streaming. 

Select from GPT-3.5-Turbo or GPT-4-Turbo from within the app

Costing is estimated and shown at the bottom of every response.

To keep costs down, restart conversations when topics change with the !thanks command.

## Requirements
1. install python3.10 at least
2. run the following: `pip install openai tiktoken`
3. fill in your own API within your envrionment variable named OPEN_AI_KEY
4. modify the 'identity' variable within the code to change identity if you wish
5. run `python OpenAI-API-Terminal.py`

NOTE: This bot uses the newest OpenAI python package and therefore the newer api call. If it's not working for you, you may have had openai installed already and need to update: `pip install upgrade openai`

## Features
💬 Ask something and press enter to chat. Conversation history is maintained until you wipe it with !thanks.

⌨️ !code - Enter Multi-line input mode. Good for providing code samples.

🧠 !thanks -- Clear chat history

🔁 !gpt3 or !gpt4 -- Model selection

👋 !exit -- Quit

## Screenshots

![Screenshot Of My App](screenshot.png)
