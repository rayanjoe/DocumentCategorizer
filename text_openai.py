from openai import AzureOpenAI


API_TYPE = "azure"
ENDPOINT = "https://azureopenaitest03.openai.azure.com/"
API_KEY = "rTHSjHFXMuCDucQjHTqybjReb2JqxeZbWBcFsZSuZ1uVAKdSX2FOJQQJ99BCACYeBjFXJ3w3AAABACOG6EYe"
API_VERSION = "2024-07-01-preview"



class MySimpleAgent:
    def __init__(
            self,
            model='gpt-4o-mini'
    ):
        self.model = model
        self.system_prompt = "you are a summarizing assistant"
        self.client = AzureOpenAI(
                        azure_endpoint=ENDPOINT,
                        api_key=API_KEY,
                        api_version=API_VERSION,
                      )

    def ask(
            self,
            user_prompt
    ):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        return response


if __name__ == "__main__":
    agent = MySimpleAgent()

    while True:
        user_input = input("HI I'm your agent Ask Anything...")
        if user_input == "exit":
            print("Have a great day! Bye")
            break

        response = agent.ask(user_input)
        print(response.choices[0].message.content)
