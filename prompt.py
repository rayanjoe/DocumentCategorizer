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
- LOAN PURCHASE STATEMENT
- UNKNOWN

Rules:
- Read the provided document text carefully.
- Choose a category ONLY if there is clear, direct evidence that the document matches that category.
- If the document does not clearly match any category, respond with UNKNOWN.
- Do NOT guess or choose a “closest” category.
- If the document is unrelated (e.g., ticket confirmation, receipt, email, invoice, generic form), respond UNKNOWN.
- Respond with ONLY ONE option from the list above.
- Output must be EXACT text (uppercase).
- Do NOT include explanations, punctuation, symbols, or extra words.
- Do NOT hallucinate missing information.

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
- LOAN PURCHASE STATEMENT

Rules:
- Read the provided document text carefully.
- Choose a category ONLY if there is clear, direct evidence that the document matches that category.
- If the document does not clearly match any category, respond with UNKNOWN.
- Do NOT guess or choose a “closest” category.
- If the document is unrelated (e.g., ticket confirmation, receipt, email, invoice, generic form), respond UNKNOWN.
- Respond with ONLY ONE option from the list above.
- Output must be EXACT text (uppercase).
- Do NOT include explanations, punctuation, symbols, or extra words.
- Do NOT hallucinate missing information."""
                },
                {
                    "type": "image_url",
                    "image_url": string
                }
            ]
        }
    ]
    
    
    
    
    
# - Read the added text properly and answer don't hallucinate. If the proof are there, then response
# - If 
# - Respond with ONLY ONE option from the list above.
# - Output must be EXACT text (uppercase).
# - Do NOT include explanations, punctuation, symbols, or extra words.
# - Do NOT use markdown.
# - If unsure, choose the closest matching option.