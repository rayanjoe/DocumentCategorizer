import instructor
from azureopenai.config import client as azure_client
client = instructor.from_openai(azure_client)
from pydantic import BaseModel, Field
from ImageToTextExtracterAdapter import image_to_base64


image_path = r"C:\Users\darshan.lingegowda\Downloads\insurance.png"

base64_string = image_to_base64(path=image_path)


class DocumentCategory(BaseModel):
    category: str = Field(..., description="The category of the document")

response = client.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Categorize the document as [ PAY STUB, MORTGAGE DEED, W2 FORM, INSURANCE POLICY]"
                },
                {
                    "type": "image_url",
                    "image_url": base64_string
                }
            ]
        }
    ],
    response_model=DocumentCategory
)

print(f'Category: {response.category}')
