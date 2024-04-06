import argparse
import os
import time

import tiktoken
from dotenv import load_dotenv
from openai import OpenAI


def check_ollama():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--ollama", action="store_true", help="Use Ollama instead of OpenAI"
    )

    args = parser.parse_args()

    if args.ollama:
        return True
    else:
        return False


class ModelConfig:
    def __init__(self):
        if check_ollama():
            self.client = OpenAI(
                api_key="OLLAMA_FTW", base_url="http://localhost:11434/v1"
            )
            self.model = os.environ["OLLAMA_MODEL"]
        else:
            self.client = OpenAI(api_key=os.environ["OPEN_AI_KEY"])
            self.model = "gpt-3.5-turbo-0125"

        self.identity = {
            "role": "system",
            "content": "You are a helpful and friendly chat bot. You are a programming expert of all programming languages. Respond to my message as effectively as you can. Use Markdown formatting and ensure code is in codeblocks.",
        }
        self.history = [self.identity]
        self.modelTemp = 0.5
        self.totalCost = 0
        self.totalTokens = 0
        self.model_max_tokens = 16000
        self.num_tokens = 0
        self.prompt_token_count = 0
        self.costing = "placeholder"
        self.ollama = check_ollama()
        self.name = os.environ["ASSISTANT_NAME"]


class TerminalGptBot:
    def __init__(self):
        self.config = ModelConfig()

    def calculateCost(self):
        if self.config.model == "gpt-4-0125-preview":
            cost_per_token = 0.02 / 1000
        elif self.config.model == "gpt-3.5-turbo-0125":
            cost_per_token = 0.001 / 1000
        elif self.config.ollama:
            cost_per_token = 0.000 / 1000
        self.config.totalTokens = self.num_tokens_from_messages(self.config.history) - 4
        self.config.totalCost = self.config.totalTokens * cost_per_token
        self.config.costing = f"🪙 ${self.config.totalCost:.4f} - 🎟️ {self.config.totalTokens} - 🤖 {self.config.model}"

    def num_tokens_from_messages(self, messages):
        model = self.config.model
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
            except KeyError:
                encoding = "Infinite"
        if model == "gpt-3.5-turbo-0301":
            number_tokens = 0
            for message in messages:
                number_tokens += 4
                for key, value in message.items():
                    number_tokens += len(encoding.encode(value))
                    if key == "name":
                        number_tokens += -1
            number_tokens += 2
            return number_tokens
        elif self.config.ollama:
            return 0
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
    See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def stream_openai(self, prompt):
        fullMessage = ""
        user_response_obj = {"role": "user", "content": prompt}
        self.config.history.append(user_response_obj)
        self.config.prompt_token_count = self.num_tokens_from_messages(
            self.config.history
        )
        response = self.config.client.chat.completions.create(
            model=self.config.model,
            messages=self.config.history,
            temperature=self.config.modelTemp,
            stream=True,
        )
        print(f"\n\033[94m{self.config.name}\x1b[0m")
        fullMessage = ""
        for data in response:
            for choice in data.choices:
                if choice.delta and choice.delta.content:
                    chunk = choice.delta.content
                    print(chunk, end="")
                    fullMessage += chunk
        self.config.history.append({"role": "assistant", "content": fullMessage})
        return fullMessage

    def resetConvoHistory(self):
        self.config.history = [self.config.identity]

    def makeBanner(self):
        os.system("cls" if os.name == "nt" else "clear")
        banner = f"\n\033[94m{self.config.name}\x1b[0m is now online with {self.config.model}.\n\x1b[90m💬 Ask something and press enter to chat.\n⌨️ !code - Enter Multi-line input mode. Good for providing code samples.\n🧠 !thanks -- Clear chat history\n🔁 !gpt3 or !gpt4 -- Model selection\n👋 !exit -- Quit\x1b[0m"
        return banner

    def run(self):
        print(self.makeBanner())
        while True:
            user_input = input("\n\x1b[32mYou\x1b[0m \n")
            if user_input == "!thanks":
                self.resetConvoHistory()
                os.system("cls" if os.name == "nt" else "clear")
                print(
                    f"\n\x1b[90mConversation history cleared. -- Model: {self.config.model}\x1b[0m"
                )
                continue
            elif user_input == "!code":
                user_input_lines = []
                print(
                    "\x1b[90mEnter or paste your message. Type 'eof' as the final line when you're done:\x1b[0m"
                )
                while True:
                    line = input()
                    if line == "eof":
                        break
                    user_input_lines.append(line)
                user_input = "\n".join(user_input_lines)
                self.calculateCost()
                print(
                    f"\n\n\x1b[90m{self.config.costing} -- '!thanks' to start a new conversation."
                )
            elif user_input == "!gpt3":
                if self.config.ollama:
                    print(
                        "\x1b[90mOllama is being used, therefore OpenAI models are not available."
                    )
                else:
                    self.config.model = "gpt-3.5-turbo-0125"
                    print(f"\x1b[90mModel set to {self.config.model}.")
                continue
            elif user_input == "!gpt4":
                if self.config.ollama:
                    print(
                        "\x1b[90mOllama is being used, therefore OpenAI models are not available."
                    )
                else:
                    self.config.model = "gpt-4-0125-preview"
                    print(f"\x1b[90mModel set to {self.config.model}.")
            elif user_input == "!exit":
                self.config.history.clear()
                print(f"\033[94m{self.config.name}:\x1b[0m See you later!")
                time.sleep(1)
                break
            else:
                try:
                    self.stream_openai(user_input)
                    self.calculateCost()
                    print(
                        f"\n\n\x1b[90m{self.config.costing} -- '!thanks' to start a new conversation."
                    )
                except Exception as e:
                    error = str(e)
                    print(f"Shoot..Something went wrong or timed out. Error{error}")


def main():
    load_dotenv()
    chatbot = TerminalGptBot()
    chatbot.run()


if __name__ == "__main__":
    main()
