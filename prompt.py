def prompt_pdf(string):
    return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Task:
Categorize the document into EXACTLY ONE of the following options:
- PAY STUB
- MORTGAGE DEED
- W2 FORM
- INSURANCE POLICY
- CREDIT REPORT
- LOAN APPLICATION
- TAX RETURN
- APPRAISAL FORM

Rules:
- Read the added text properly and answer don't hallucinate. If the proof are there, then respons
- Respond with ONLY ONE option from the list above.
- Output must be EXACT text (uppercase).
- Do NOT include explanations, punctuation, symbols, or extra words.
- Do NOT use markdown.
- If unsure, choose the closest matching option.
                        """
                        
                    },
                    {
                        "type": "text",
                        "text": string
                    }
                ]
            }
        ]


def prompt_image(string):
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Task:
Categorize the document into EXACTLY ONE of the following options:
- PAY STUB
- MORTGAGE DEED
- W2 FORM
- INSURANCE POLICY
- CREDIT REPORT
- LOAN APPLICATION
- TAX RETURN
- APPRAISAL FORM

Rules:
- Read the added text properly and answer don't hallucinate. If the proof are there, then respons
- Respond with ONLY ONE option from the list above.
- Output must be EXACT text (uppercase).
- Do NOT include explanations, punctuation, symbols, or extra words.
- Do NOT use markdown.
- If unsure, choose the closest matching option."""
                },
                {
                    "type": "image_url",
                    "image_url": string
                }
            ]
        }
    ]