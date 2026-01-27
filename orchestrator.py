from ImageToTextExtracterAdapter import image_to_base64
from PdftoTextExtracterAdapter import extract_text_from_pdf_fast
from DocCatBase import BaseAIAdapter
from config import client
from prompt import prompt_image, prompt_pdf
import os
from pypdf import PdfWriter, PdfReader
import io
from PIL import Image


ORDER = ["PAY STUB", "MORTGAGE DEED", "W2 FORM", "INSURANCE POLICY", "CREDIT REPORT", "LOAN APPLICATION", "TAX RETURN", "APPRAISAL FORM"]


folder_path = r"POC\documents"
output_pdf = r"POC\output\sorted_bundle.pdf"

buckets = {c: [] for c in ORDER}
buckets["NEED TO VERIFY"] = []

adapter = BaseAIAdapter(client)

for name in os.listdir(folder_path):
    file_path = os.path.join(folder_path, name)
    print(file_path)

    if not os.path.isfile(file_path):
        continue

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
        model_input = image_to_base64(path=file_path)
        prompt = prompt_image(string=model_input)
        # print(model_input) 
    elif ext == ".pdf":
        model_input = extract_text_from_pdf_fast(pdf_path=file_path)
        prompt = prompt_pdf(string = model_input)
        # print(model_input)
    else:
        print(f"Skipping unsupported file: {file_path}")
        continue

    print(f"\nProcessing: {name} | ext={ext} | input_chars={len(model_input)}")

    response = adapter.execute(prompt=prompt)

    category = response.choices[0].message.content.strip().upper()
    print("Category:", category)

    if category in buckets:
        buckets[category].append(file_path)
    else:
        buckets["NEED TO VERIFY"].append(file_path)

print("\nBuckets:", buckets)




























































































# ORDER = ["PAY STUB", "MORTGAGE DEED", "W2 FORM", "INSURANCE POLICY"]
# path = r"POC\documents"
# output_pdf = r"POC\output\sorted_bundle.pdf"

# os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

# buckets = {c: [] for c in ORDER}
# buckets["NEED TO VERIFY"] = []

# print(os.listdir(path))



# for name in os.listdir(path):
#     path = os.path.join(path, name)
    
#     if not os.path.isfile(path):
#         continue

#     ext = os.path.splitext(path)[1].lower()
#     if ext in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#         base64_string = image_to_base64(path=path)
#         print(base64_string)
#     elif ext in [".pdf"]:
#         base64_string = extract_text_from_pdf_fast(pdf_path=path)
#         print(base64_string)
#     adapter = BaseAIAdapter(client, DocumentCategory)
#     print("hi")
#     print(base64_string)
#     response = adapter.execute(string=base64_string)
#     print("after this")
#     print(response)
#     category = response.choices[0].message.content.strip()
#     print(category)
#     if category in buckets:
#         buckets[category].append(path)
#         print(buckets)
#     else:
#         buckets["NEED TO VERIFY"].append(path)

# pdf_pages = [] 



def image_to_pdf_bytes(img_path: str) -> bytes:
    """Convert an image into a single-page PDF (bytes)."""
    img = Image.open(img_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PDF")
    return buf.getvalue()

writer = PdfWriter()

for cat in ORDER + ["NEED TO VERIFY"]:
    for file_path in buckets[cat]:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            reader = PdfReader(file_path)
            for page in reader.pages:
                writer.add_page(page)

        elif ext in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
            pdf_bytes = image_to_pdf_bytes(file_path)
            img_reader = PdfReader(io.BytesIO(pdf_bytes))
            writer.add_page(img_reader.pages[0])

        else:
            print(f"Skipping unsupported file: {file_path}")



if len(writer.pages) > 0:
    with open(output_pdf, "wb") as f:
        writer.write(f)
    print("✅ Saved:", output_pdf)
else:
    print("No files found to write.")

















# ext = os.path.splitext(path)[1].lower()
# if ext in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
#     for cat in ORDER + ["NEED TO VERIFY"]:
#         for img_path in buckets[cat]:
#             pdf_pages.append(Image.open(img_path).convert("RGB"))

# if pdf_pages:
#     first = pdf_pages[0]
#     rest = pdf_pages[1:]
#     first.save(output_pdf, save_all=True, append_images=rest)
#     print("✅ Saved:", output_pdf)
# else:
#     print("No images found.")


# list_ = [] 
# path = r"POC\documents"
# file_name = os.listdir(path)
# for i in file_name:
#     print(i)
#     image_path = path + f'\{i}'
#     print(image_path)
#     base64_string = image_to_base64(path=image_path)
#     adapter = BaseAIAdapter(client, DocumentCategory)
#     type_doc = adapter.execute(string=base64_string)
#     list_.append(type_doc)
    
#     if type_doc == "INSURANCE POLICY":
#         pass
#     elif type_doc == "PAY STUB":
#         pass
#     elif type_doc == "W2 FORM":
#         pass
#     elif type_doc == "MORTGAGE DEED":
#         pass
#     elif type_doc == "NEED TO VERIFY":
#         pass

# print(list_)


