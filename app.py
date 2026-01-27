import os
import io
import streamlit as st

from ImageToTextExtracterAdapter import image_to_base64
from PdftoTextExtracterAdapter import extract_text_from_pdf_fast
from DocCatBase import BaseAIAdapter
from config import client
from prompt import prompt_image, prompt_pdf

from pypdf import PdfWriter, PdfReader
from PIL import Image

FREDDIE_MAC_LOGO = "freddie-mac.png"
HEXACORP_LOGO = "hexacorplogo.png"
hexacorp_logo_diff = "logo-blue.png"

ORDER = ["PAY STUB", "MORTGAGE DEED", "W2 FORM", "INSURANCE POLICY", "CREDIT REPORT", "LOAN APPLICATION", "TAX RETURN", "APPRAISAL FORM"]

IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]
PDF_EXTS = [".pdf"]



def init_buckets():
    buckets = {c: [] for c in ORDER}
    buckets["NEED TO VERIFY"] = []
    return buckets


def image_to_pdf_bytes(img_bytes: bytes) -> bytes:
    """Convert an image (bytes) into a single-page PDF (bytes)."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PDF")
    return buf.getvalue()


def classify_file(adapter: BaseAIAdapter, file_name: str, file_bytes: bytes) -> str:
    """
    Classify a single uploaded file using your exact core logic:
    - Image: base64 -> prompt_image
    - PDF: extract_text_from_pdf_fast (needs path, so we handle via temp file) -> prompt_pdf
    """
    ext = os.path.splitext(file_name)[1].lower()

    if ext in IMAGE_EXTS:
        temp_path = save_temp_file(file_name, file_bytes)
        try:
            model_input = image_to_base64(path=temp_path)
            prompt = prompt_image(string=model_input)
        finally:
            safe_remove(temp_path)

    elif ext in PDF_EXTS:
        temp_path = save_temp_file(file_name, file_bytes)
        try:
            print(temp_path)
            model_input = extract_text_from_pdf_fast(pdf_path=temp_path)
            print("This is from the pdf elif")
            print(model_input)
            prompt = prompt_pdf(string=model_input)
        finally:
            safe_remove(temp_path)

    else:
        return "NEED TO VERIFY"
    
    print(prompt)
    response = adapter.execute(prompt=prompt)
    category = response.choices[0].message.content.strip().upper()
    return category


def save_temp_file(file_name: str, file_bytes: bytes) -> str:
    """Save uploaded bytes to a temp file and return the path."""
    temp_dir = "POC/_tmp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file_name)
    with open(temp_path, "wb") as f:
        f.write(file_bytes)
    return temp_path


def safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def add_pdf_to_writer(writer: PdfWriter, pdf_bytes: bytes) -> None:
    """Append all pages from a PDF (bytes) to PdfWriter."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    for page in reader.pages:
        writer.add_page(page)


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader


def category_title_page_pdf(category: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter

    logo_height = 0.6 * inch
    logo_y = h - 0.9 * inch  # top margin

    # Freddie Mac - left
    if os.path.exists(FREDDIE_MAC_LOGO):
        c.drawImage(
            ImageReader(FREDDIE_MAC_LOGO),
            x=0.75 * inch,
            y=logo_y,
            height=logo_height,
            preserveAspectRatio=True,
            mask="auto",
        )

    if os.path.exists(hexacorp_logo_diff):
        c.drawImage(
            ImageReader(hexacorp_logo_diff),
            x=w - 2.25 * inch,     # right aligned
            y=logo_y,
            height=logo_height,
            preserveAspectRatio=True,
            mask="auto",
        )
    c.setFont("Helvetica-Bold", 56)
    c.drawCentredString(w / 2, h / 2, category)

    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(w / 2, (h / 2) - 0.6 * inch, "Document Categorizer")

    c.showPage()
    c.save()
    return buf.getvalue()


def build_sorted_bundle_pdf(buckets: dict) -> bytes:
    writer = PdfWriter()

    for cat in ORDER + ["NEED TO VERIFY"]:
        items = buckets.get(cat, [])
        if not items:
            continue

        # ✅ Add category title page first
        title_pdf = category_title_page_pdf(cat)
        add_pdf_to_writer(writer, title_pdf)

        # ✅ Then add all docs for that category
        for item in items:
            file_name = item["file_name"]
            file_bytes = item["file_bytes"]
            ext = os.path.splitext(file_name)[1].lower()

            if ext in PDF_EXTS:
                add_pdf_to_writer(writer, file_bytes)
            elif ext in IMAGE_EXTS:
                pdf_bytes = image_to_pdf_bytes(file_bytes)
                add_pdf_to_writer(writer, pdf_bytes)
            else:
                # DOC/DOCX won't be included unless you convert them
                continue

    if len(writer.pages) == 0:
        return b""

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()



def process_uploads(uploaded_files) -> tuple[dict, bytes]:
    """
    Full pipeline:
    1) classify -> buckets
    2) build sorted pdf
    """
    buckets = init_buckets()
    adapter = BaseAIAdapter(client)

    for uf in uploaded_files:
        file_name = uf.name
        file_bytes = uf.getvalue()

        category = classify_file(adapter, file_name, file_bytes)
        print(category)

        if category in buckets:
            buckets[category].append({"file_name": file_name, "file_bytes": file_bytes})
            #print(buckets)
        else:
            buckets["NEED TO VERIFY"].append({"file_name": file_name, "file_bytes": file_bytes})

    pdf_bytes = build_sorted_bundle_pdf(buckets)
    
    return buckets, pdf_bytes


#streamlit
# st.set_page_config(page_title="Document Categorizer", layout="wide")
# st.title("📄 Document Categorizer → Sorted Bundle PDF")

# st.write(
#     "Upload images or PDFs. The app will classify each document and generate one merged PDF "
#     "in this order: **PAY STUB → MORTGAGE DEED → W2 FORM → INSURANCE POLICY**."
# )

# uploaded_files = st.file_uploader(
#     "Upload documents (images / PDFs)",
#     type=["png", "jpg", "jpeg", "webp", "tif", "tiff", "pdf"],
#     accept_multiple_files=True
# )

# if uploaded_files:
#     st.info(f"Files selected: {len(uploaded_files)}")

#     if st.button("Process & Generate PDF"):
#         with st.spinner("Classifying documents and generating PDF..."):
#             buckets, pdf_bytes = process_uploads(uploaded_files)

#         st.subheader("Buckets (classified results)")
#         for cat in ORDER + ["NEED TO VERIFY"]:
#             files_in_cat = [x["file_name"] for x in buckets[cat]]
#             st.write(f"**{cat}**: {len(files_in_cat)}")
#             if files_in_cat:
#                 st.caption(", ".join(files_in_cat))

#         if pdf_bytes:
#             st.success("✅ sorted_bundle.pdf generated!")
#             st.download_button(
#                 label="Download sorted_bundle.pdf",
#                 data=pdf_bytes,
#                 file_name="sorted_bundle.pdf",
#                 mime="application/pdf"
#             )
#         else:
#             st.error("No pages were generated. Please upload valid files.")
# else:
#     st.warning("Upload at least one document to begin.")


# 

import time
import streamlit as st
from io import BytesIO

# from your_backend_module import process_uploads   # <-- import your real backend function

st.set_page_config(page_title="Document Categorizer", layout="wide")


#ORDER = ["PAY STUB", "MORTGAGE DEED", "W2 FORM", "INSURANCE POLICY", "CREDIT REPORT", "LOAN APPLICATION", "TAX RETURN", "APPRAISAL FORM"]

# -----------------------------
# CSS (your styling + blue Process + uploader styling)
# -----------------------------
st.markdown(
    """
    <style>
      .top-header {
        background: #ffffff;
        padding: 14px 18px;
        border-radius: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.08);
        margin-bottom: 18px;
      }
      .center-box {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 24px 0;
      }
      .big-spinner {
        width: 110px; height: 110px;
        border: 12px solid rgba(34,197,94,0.25);
        border-top: 12px solid #22c55e;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 14px;
      }
      @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }

      /* Default button look (your original) */
      div.stButton > button {
        width: 100% !important;
        padding: 0.85rem 1rem !important;
        border-radius: 0.9rem !important;
        font-weight: 700 !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
      }

        /* BLUE Process button (high specificity) */
        .process-btn button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 1px solid #1d4ed8 !important;
        font-weight: 800 !important;
        }

        .process-btn button:hover {
        background-color: #1d4ed8 !important;
        border-color: #1e40af !important;
        }


      /* Download button GREEN (your original) */
      div.stDownloadButton > button {
        background-color: #16a34a !important;
        color: #ffffff !important;
        border: 1px solid #15803d !important;
        padding: 0.85rem 1rem !important;
        border-radius: 0.9rem !important;
        font-weight: 800 !important;
        width: 100% !important;
      }
      div.stDownloadButton > button:hover {
        background-color: #15803d !important;
        border-color: #166534 !important;
      }

      /* Uploader / Browse files styling */
      section[data-testid="stFileUploaderDropzone"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 14px !important;
        padding: 14px !important;
        background: #f9fafb !important;
      }
      section[data-testid="stFileUploaderDropzone"] button {
        border-radius: 12px !important;
        font-weight: 800 !important;
        padding: 0.55rem 0.9rem !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
      }
      section[data-testid="stFileUploaderDropzone"] button:hover {
        background: #f3f4f6 !important;
      }

      .footer { text-align:center; color:#6b7280; font-size:0.9rem; padding: 12px 0 6px 0; }

      .sidecard{
        border: 1px solid #e5e7eb;
        background: #ffffff;
        border-radius: 16px;
        padding: 14px 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      }
      .muted{ color:#6b7280; font-size:0.92rem; }
      .pill{
        display:inline-block; padding:4px 10px; border-radius:999px;
        background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8;
        font-weight:800; font-size:0.85rem; margin-right:6px; margin-bottom:6px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Session state
# -----------------------------
st.session_state.setdefault("processing", False)
st.session_state.setdefault("processed", False)
st.session_state.setdefault("processed_bytes", None)   # pdf bytes
st.session_state.setdefault("buckets", None)          # backend buckets dict
st.session_state.setdefault("last_upload_signature", None)
st.session_state.setdefault("uploader_key", 0)


# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="top-header">', unsafe_allow_html=True)
left, center, right = st.columns([1.6, 3.2, 1.6], vertical_alignment="center")
with left:
    st.image(FREDDIE_MAC_LOGO, width="stretch")
with center:
    st.markdown("<h1 style='text-align:center; margin: 0;'>Document Categorizer</h1>", unsafe_allow_html=True)
with right:
    st.image(HEXACORP_LOGO, width="stretch")
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Main layout
# -----------------------------
main_left, main_center, main_right = st.columns([1.2, 2.2, 1.2])

# -----------------------------
# CENTER PANEL
# -----------------------------
with main_center:
    col1, col2 = st.columns([4,1])
    with col1:
        st.markdown("## 📄 Document Processing")
    
    with col2:
                if st.button("Clear", type="primary"):
                    st.session_state.uploader_key += 1  # ✅ clears uploader UI
                    st.session_state.processing = False
                    st.session_state.processed = False
                    st.session_state.processed_bytes = None
                    st.session_state.buckets = None
                    st.session_state.last_upload_signature = None
                    st.rerun()

    uploaded_files = st.file_uploader(
        "Upload documents (PDF, DOC, DOCX, max 10MB each)",
        type=["pdf", "doc", "docx", "png", "jpg", "jpeg", "webp", "tif", "tiff", "pdf"],
        key="uploader",
        accept_multiple_files=True
    )

    # Reset state when the selected set changes
    if uploaded_files:
        signature = tuple((f.name, f.size) for f in uploaded_files)
        if signature != st.session_state.last_upload_signature:
            st.session_state.last_upload_signature = signature
            st.session_state.processing = False
            st.session_state.processed = False
            st.session_state.processed_bytes = None
            st.session_state.buckets = None

    if not uploaded_files:
        st.warning("Upload at least one document to begin.")
    else:
        st.success("Documents Uploaded")

        # ---------- PROCESSING ----------
        if st.session_state.processing:
            st.markdown(
                """
                <div class="center-box">
                  <div class="big-spinner"></div>
                  <div style="color:#16a34a; font-weight:800; font-size: 1.05rem;">
                    Classifying documents and generating PDF...
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ✅ Call YOUR backend
            print("new")
            print(uploaded_files)
            buckets, pdf_bytes = process_uploads(uploaded_files)

            st.session_state.buckets = buckets
            st.session_state.processed_bytes = pdf_bytes  # keep raw bytes (no conversion needed)
            st.session_state.processing = False
            st.session_state.processed = True
            st.rerun()

        # ---------- PROCESSED ----------
        elif st.session_state.processed:
            st.download_button(
                label="⬇️ Download Processed Documents",
                data=st.session_state.processed_bytes,   # your backend bytes
                file_name="sorted_bundle.pdf",
                mime="application/pdf",
                width="stretch",
            )

            st.markdown(
                """
                <div style="margin-top:12px; background:#ecfdf5; border:1px solid #bbf7d0;
                            padding:12px; border-radius:14px; text-align:center; color:#166534;
                            font-weight:800;">
                    ✓ sorted_bundle.pdf generated successfully!
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------- READY ----------
        else:
            col1, col2 = st.columns(2)

            
            st.markdown("<div class='process-btn'>", unsafe_allow_html=True)
            if st.button("Process Document"):
                    st.session_state.processing = True
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            
# -----------------------------
# RIGHT PANEL (Instructions + Config + Uploaded + Buckets)
# -----------------------------
with main_right:
    st.markdown(
        """
        <div class="sidecard">
          <h3 style="margin:0 0 8px 0;">📌 Instructions</h3>
          <div class="muted">
            <b>1)</b> Upload one or more documents.<br/>
            <b>2)</b> Click <span class="pill">Process Document</span> (blue).<br/>
            <b>3)</b> The backend runs <b>process_uploads(uploaded_files)</b> and returns:<br/>
            &nbsp;&nbsp;• <b>buckets</b>: classified file list per category<br/>
            &nbsp;&nbsp;• <b>pdf_bytes</b>: final <u>single</u> sorted bundle PDF<br/>
            <b>4)</b> Click the green download button to download <b>sorted_bundle.pdf</b>.
          </div>
          <hr style="border:none; border-top:1px solid #e5e7eb; margin:12px 0;" />
          <h3 style="margin:0 0 8px 0;">⚙️ Config Order</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    for c in ORDER:
        st.markdown(f"<span class='pill'>{c}</span>", unsafe_allow_html=True)
    st.markdown("<span class='pill'>NEED TO VERIFY</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📂 Uploaded Files")
    if uploaded_files:
        for f in uploaded_files:
            st.write(f"• {f.name}")
    else:
        st.caption("No files uploaded yet.")


# -----------------------------
# Footer
# -----------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown('<div class="footer">All rights reserved @hexacorp 2026</div>', unsafe_allow_html=True)
