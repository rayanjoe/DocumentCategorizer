# from pdf2image import convert_from_path

# import pytesseract
 
# # Convert only the first page to an image

# pages = convert_from_path("Form_15AC.pdf",
#                           300, first_page=0, last_page=1)
 
# # OCR the first page


# import pytesseract

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# text = pytesseract.image_to_string(pages[0])

# print(text)


# import pdfplumber
# from pdf2image import convert_from_path
# import pytesseract
 
# def read_first_page(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         first_page = pdf.pages[0]
#         text = first_page.extract_text()
#         if text and text.strip():
#             return text
#         else:
#             # Fallback to OCR
#             pages = convert_from_path(pdf_path, 300, first_page=0, last_page=0)
#             return pytesseract.image_to_string(pages[0])
 
# print(read_first_page("document.pdf"))

from pdf2image import convert_from_path
import base64
import io
 
def pdf_first_page_to_base64(pdf_path: str) -> str:
    # Convert only the first page to an image (300 DPI for clarity)
    pages = convert_from_path(pdf_path, dpi=300, first_page=0, last_page=10)
    # Get the first page as a PIL image
    print(pages)
    # Save image to bytes buffer
    buffer = io.BytesIO()
    pages.save(buffer, format="PNG")
    # Encode to base64
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str
 
# Example usage
base64_image = pdf_first_page_to_base64("Form_15AC.pdf")
print(base64_image[:200])  # Print first 200 chars of base64 string