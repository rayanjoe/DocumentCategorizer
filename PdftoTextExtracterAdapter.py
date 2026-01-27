import fitz
# def extract_text_from_pdf_fast(pdf_path) -> str:
#     try:
#         doc = fitz.open(pdf_path)
#         text = ""
#         for i in range(min(2, doc.page_count)):
#             text += doc.load_page(i).get_text("text") + "\n"
#             print("This is inside the pdf adap"+text)
#         return text
#     except Exception:
#         return ""
    
    
import fitz
import os

def extract_text_from_pdf_fast(pdf_path) -> str:
    try:
        print("extract_text_from_pdf_fast called with:", pdf_path)
        print("exists?", os.path.exists(pdf_path), "size:", os.path.getsize(pdf_path) if os.path.exists(pdf_path) else "NA")

        doc = fitz.open(pdf_path)
        print("page_count:", doc.page_count)

        text_parts = []
        for i in range(min(2, doc.page_count)):
            page = doc.load_page(i)
            page_text = page.get_text("text")
            print(f"page {i} text len:", len(page_text))
            text_parts.append(page_text)

        text = "\n".join(text_parts).strip()
        print("TOTAL extracted len:", len(text))
        return text

    except Exception as e:
        print("PDF extract failed:", repr(e))
        return ""
