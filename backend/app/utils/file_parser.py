"""Parse PDF and DOCX resume files into text, then use AI to extract structured data."""
import io
import json
import re

from app.ai.base import chat


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except ImportError:
        return "PDF解析库未安装"


def parse_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return "DOCX解析库未安装"


def extract_resume_structure(raw_text: str) -> dict:
    """Use DeepSeek AI to extract structured resume data from raw text."""
    if not raw_text.strip() or len(raw_text) < 20:
        return {}

    prompt = f"""请从以下简历文本中提取结构化数据，输出JSON格式。

原始简历文本：
{raw_text[:4000]}

请提取以下字段（如果文本中没有则设为空字符串或空数组）：
{{
  "name": "姓名",
  "email": "邮箱",
  "phone": "电话",
  "summary": "个人总结/自我评价",
  "target_position": "目标职位",
  "education": [
    {{"school": "学校名称", "degree": "学位", "major": "专业", "start_date": "开始时间", "end_date": "结束时间", "gpa": "GPA(如有)", "description": "描述"}}
  ],
  "work_experiences": [
    {{"company": "公司名称", "title": "职位", "location": "地点", "start_date": "开始时间", "end_date": "结束时间", "description": "工作描述"}}
  ],
  "projects": [
    {{"name": "项目名称", "role": "角色", "description": "项目描述", "tech_stack": ["技术1", "技术2"]}}
  ],
  "skills": [
    {{"category": "分类(如:编程语言/框架/工具)", "name": "技能名称", "level": "熟练程度(入门/熟练/精通/专家)"}}
  ]
}}

只输出JSON，不要markdown包裹。"""

    try:
        response = chat([{"role": "user", "content": prompt}], temperature=0.2, max_tokens=4096)
    except Exception:
        return {}

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group(1))
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', response, re.DOTALL)
                result = json.loads(match.group(0)) if match else {}
        else:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            result = json.loads(match.group(0)) if match else {}

    return result
