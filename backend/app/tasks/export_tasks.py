import os
import uuid
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app
from app.utils.document_gen import build_docx_resume, build_html_resume

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "media", "exports")


@celery_app.task(bind=True, max_retries=3)
def export_resume_pdf(self, resume_data: dict, template: str = "modern") -> dict:
    """Generate a PDF resume. Returns file path info."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    filename = f"resume_{uuid.uuid4().hex[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(EXPORT_DIR, filename)

    html = build_html_resume(resume_data, template)

    try:
        _register_pdf_fonts_imported()
        from xhtml2pdf import pisa
        with open(filepath, "wb") as f:
            pisa_status = pisa.CreatePDF(html, dest=f, encoding="utf-8")
        if pisa_status.err:
            raise RuntimeError(f"PDF conversion error: {pisa_status.err}")
    except (ImportError, RuntimeError):
        html_path = filepath.replace(".pdf", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        filepath = html_path

    return {"filename": os.path.basename(filepath), "path": filepath}


def _register_pdf_fonts_imported() -> None:
    """Register Chinese fonts for CJK rendering in PDFs."""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        candidates = [
            ("C:/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
            ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "WenQuanYi Micro Hei"),
        ]
        for path, name in candidates:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(name, path, subfontIndex=0))
                except Exception:
                    pass
    except ImportError:
        pass


@celery_app.task(bind=True, max_retries=3)
def export_resume_docx(self, resume_data: dict, template: str = "classic") -> dict:
    """Generate a DOCX resume."""
    os.makedirs(EXPORT_DIR, exist_ok=True)

    filename = f"resume_{uuid.uuid4().hex[:8]}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.docx"
    filepath = os.path.join(EXPORT_DIR, filename)

    content = build_docx_resume(resume_data)
    with open(filepath, "wb") as f:
        f.write(content)

    return {"filename": filename, "path": filepath}


@celery_app.task
def cleanup_old_exports(days: int = 7) -> int:
    """Delete export files older than N days."""
    if not os.path.exists(EXPORT_DIR):
        return 0

    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    count = 0
    for fname in os.listdir(EXPORT_DIR):
        fpath = os.path.join(EXPORT_DIR, fname)
        if os.path.getmtime(fpath) < cutoff:
            os.remove(fpath)
            count += 1
    return count
