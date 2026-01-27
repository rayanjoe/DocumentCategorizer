# image_path = r"C:\Users\darshan.lingegowda\Downloads\paystub.jpg"
# image_path = r"C:\Users\darshan.lingegowda\Downloads\W2 Sample 1.png"
image_path = r"POC\documents\insurance.png"

import instructor
class BaseAIAdapter():
    def __init__(self, client):
        self.client = client
        pass
    
    def execute(self, prompt):
        #client = instructor.from_openai(self.client)
        client = self.client
        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages= prompt
    )
        return response

# print(response.choices[0].message.content)
