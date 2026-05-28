"""Resume document generation — PDF via HTML template + weasyprint, DOCX via python-docx."""
import html as html_mod
from datetime import datetime


def _esc(text: str) -> str:
    if not text:
        return ""
    return html_mod.escape(str(text), quote=True)


TEMPLATE_STYLES = {
    "modern": {
        "font_family": "'Microsoft YaHei', 'PingFang SC', 'Noto Sans SC', sans-serif",
        "primary_color": "#2563eb",
        "bg_header": "#f8fafc",
        "section_style": "underline",
    },
    "classic": {
        "font_family": "'SimSun', 'STSong', 'Noto Serif SC', serif",
        "primary_color": "#1a1a1a",
        "bg_header": "transparent",
        "section_style": "bold-line",
    },
    "compact": {
        "font_family": "'Microsoft YaHei', 'PingFang SC', sans-serif",
        "primary_color": "#374151",
        "bg_header": "transparent",
        "section_style": "minimal",
    },
}


def build_html_resume(resume_data: dict, template: str = "modern") -> str:
    style = TEMPLATE_STYLES.get(template, TEMPLATE_STYLES["modern"])
    primary = style["primary_color"]

    basic = resume_data.get("basic_info") or {}
    skills = resume_data.get("skills") or []
    education = resume_data.get("education") or []
    experiences = resume_data.get("work_experiences") or resume_data.get("work_experience") or []
    projects = resume_data.get("projects") or []
    summary = resume_data.get("summary") or ""
    # target_position can be top-level or nested in job_target
    target_position = resume_data.get("target_position") or (resume_data.get("job_target") or {}).get("target_position") or ""

    city = basic.get("city") or basic.get("address") or ""

    # --- Target Position ---
    target_html = ""
    if target_position:
        target_html = f'<div class="target"><p>求职目标：{_esc(target_position)}</p></div>'

    # --- Skills ---
    skills_html = ""
    if skills:
        skill_groups: dict[str, list[str]] = {}
        for s in skills:
            cat = s.get("category", "其他")
            name = _esc(s.get("name", ""))
            level = _esc(s.get("level", ""))
            label = f"{name}" + (f" ({level})" if level else "")
            skill_groups.setdefault(cat, []).append(label)
        skills_html = '<div class="section"><h2>专业技能</h2>'
        for cat, names in skill_groups.items():
            skills_html += f'<p><strong>{_esc(cat)}</strong>：{", ".join(names)}</p>'
        skills_html += "</div>"

    # --- Education ---
    education_html = ""
    if education:
        education_html = '<div class="section"><h2>教育背景</h2>'
        for edu in education:
            education_html += f'<div class="item"><h3>{_esc(edu.get("school",""))} — {_esc(edu.get("major",""))}</h3>'
            degree = _esc(edu.get("degree", ""))
            start = _esc(str(edu.get("start_date", "")))
            end = _esc(str(edu.get("end_date", "")))
            education_html += f'<p class="meta">{degree} | {start} ~ {end}</p>'
            if edu.get("description"):
                education_html += f'<p>{_esc(edu["description"])}</p>'
            education_html += "</div>"
        education_html += "</div>"

    # --- Work Experience ---
    experience_html = ""
    if experiences:
        experience_html = '<div class="section"><h2>工作经历</h2>'
        for exp in experiences:
            company = _esc(exp.get("company", ""))
            title = _esc(exp.get("title", ""))
            location = _esc(exp.get("location", ""))
            start = _esc(str(exp.get("start_date", "")))
            end = _esc(str(exp.get("end_date", ""))) or "至今"
            header = f"{company} — {title}"
            if location:
                header += f" ({location})"
            item_html = f'<div class="item"><h3>{header}</h3>'
            item_html += f'<p class="meta">{start} ~ {end}</p>'
            if exp.get("description"):
                item_html += f'<p>{_esc(exp["description"])}</p>'
            highlights = exp.get("highlights") or []
            if highlights:
                item_html += "<ul>" + "".join(f"<li>{_esc(str(h))}</li>" for h in highlights) + "</ul>"
            item_html += "</div>"
            experience_html += item_html
        experience_html += "</div>"

    # --- Projects ---
    projects_html = ""
    if projects:
        projects_html = '<div class="section"><h2>项目经历</h2>'
        for proj in projects:
            name = _esc(proj.get("name", ""))
            role = _esc(proj.get("role", ""))
            projects_html += f'<div class="item"><h3>{name}</h3>'
            if role:
                projects_html += f'<p class="meta">角色：{role}</p>'
            start = _esc(str(proj.get("start_date", "")))
            end = _esc(str(proj.get("end_date", "")))
            if start or end:
                projects_html += f'<p class="meta">{start} ~ {end}</p>'
            if proj.get("tech_stack"):
                projects_html += f'<p class="meta">技术栈：{_esc(", ".join(proj["tech_stack"]))}</p>'
            if proj.get("description"):
                projects_html += f'<p>{_esc(proj["description"])}</p>'
            highlights = proj.get("highlights") or []
            if highlights:
                projects_html += "<ul>" + "".join(f"<li>{_esc(str(h))}</li>" for h in highlights) + "</ul>"
            projects_html += "</div>"
        projects_html += "</div>"

    css_section = "h2 { border-bottom: 2px solid " + primary + "; }" if style["section_style"] == "underline" else \
        "h2 { border-bottom: 1px solid #999; }" if style["section_style"] == "bold-line" else \
        "h2 { font-weight: 600; margin-top: 24px; text-transform: uppercase; letter-spacing: 1px; }"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: {style['font_family']}; max-width: 800px; margin: 0 auto; padding: 40px 44px; color: #222; font-size: 14px; line-height: 1.8; }}
  h1 {{ font-size: 28px; margin-bottom: 8px; text-align: center; font-weight: 700; }}
  h2 {{ font-size: 15px; color: {primary}; padding-bottom: 4px; margin-top: 28px; margin-bottom: 12px; }}
  h3 {{ font-size: 14px; margin-bottom: 2px; font-weight: 600; }}
  .header {{ text-align: center; margin-bottom: 28px; background: {style['bg_header']}; padding: 20px; border-radius: 6px; }}
  .target {{ text-align: center; margin-bottom: 20px; font-size: 15px; color: {primary}; font-weight: 500; }}
  .meta {{ font-size: 12px; color: #666; margin: 2px 0; }}
  .item {{ margin-bottom: 16px; }}
  .item p {{ margin: 4px 0; }}
  ul {{ margin: 6px 0; padding-left: 22px; }}
  li {{ font-size: 13px; margin-bottom: 3px; line-height: 1.6; }}
  {css_section}
</style>
</head>
<body>
<div class="header">
  <h1>{_esc(basic.get("name", ""))}</h1>
  <p class="meta">{_esc(basic.get("phone", ""))} | {_esc(basic.get("email", ""))}{' | ' + _esc(city) if city else ''}</p>
</div>
{target_html}
{resume_data.get('summary') and f'<div class="section"><h2>个人简介</h2><p>{_esc(resume_data["summary"])}</p></div>' or ''}
{experience_html}
{projects_html}
{education_html}
{skills_html}
{resume_data.get('chat_highlights') and f'<div class="section"><h2>AI 建议精华</h2><p style="white-space:pre-wrap;font-size:13px;">{_esc(resume_data["chat_highlights"])}</p></div>' or ''}
<p style="text-align:center;margin-top:40px;color:#bbb;font-size:11px;">生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")} · AI Career Copilot</p>
</body>
</html>"""
    return html


def build_docx_resume(resume_data: dict) -> bytes:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    # Set narrower margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)

    style = doc.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(10.5)
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.line_spacing = 1.5

    basic = resume_data.get("basic_info") or {}
    skills = resume_data.get("skills") or []
    city = basic.get("city") or basic.get("address") or ""

    # Header
    name_para = doc.add_paragraph()
    name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = name_para.add_run(basic.get("name", "") or "未命名")
    run.bold = True
    run.font.size = Pt(20)

    contact = doc.add_paragraph()
    contact.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_parts = []
    if basic.get("phone"):
        contact_parts.append(basic["phone"])
    if basic.get("email"):
        contact_parts.append(basic["email"])
    if city:
        contact_parts.append(city)
    contact.add_run(" | ".join(contact_parts)).font.size = Pt(9)

    # Separator line
    sep = doc.add_paragraph()
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sep.add_run("─" * 40).font.size = Pt(6)

    # Target Position
    if resume_data.get("target_position"):
        tp = doc.add_paragraph()
        tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = tp.add_run(f'求职目标：{resume_data["target_position"]}')
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(37, 99, 235)

    def add_section_heading(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(37, 99, 235)
        # Add underline border
        pPr = p._p.get_or_add_pPr()
        from docx.oxml.ns import qn
        pBdr = pPr.makeelement(qn('w:pBdr'), {})
        bottom = pBdr.makeelement(qn('w:bottom'), {
            qn('w:val'): 'single',
            qn('w:sz'): '4',
            qn('w:space'): '1',
            qn('w:color'): '2563eb',
        })
        pBdr.append(bottom)
        pPr.append(pBdr)

    # Summary
    if resume_data.get("summary"):
        add_section_heading("个人简介")
        p = doc.add_paragraph(resume_data["summary"])
        p.paragraph_format.line_spacing = 1.6

    # Work Experience
    experiences = resume_data.get("work_experiences") or resume_data.get("work_experience") or []
    if experiences:
        add_section_heading("工作经历")
        for exp in experiences:
            p = doc.add_paragraph()
            run = p.add_run(f'{exp.get("company", "")} — {exp.get("title", "")}')
            run.bold = True
            run.font.size = Pt(11)
            loc = exp.get("location", "")
            if loc:
                p.add_run(f" ({loc})").font.size = Pt(9)
            date_str = f'{exp.get("start_date", "")} ~ {exp.get("end_date", "") or "至今"}'
            dp = doc.add_paragraph(date_str)
            dp.runs[0].font.size = Pt(9)
            dp.runs[0].font.color.rgb = RGBColor(128, 128, 128)
            if exp.get("description"):
                desc = doc.add_paragraph(exp["description"])
                desc.paragraph_format.line_spacing = 1.6
            highlights = exp.get("highlights") or []
            for h in highlights:
                doc.add_paragraph(str(h), style="List Bullet")

    # Projects
    projects = resume_data.get("projects") or []
    if projects:
        add_section_heading("项目经历")
        for proj in projects:
            p = doc.add_paragraph()
            run = p.add_run(proj.get("name", ""))
            run.bold = True
            run.font.size = Pt(11)
            if proj.get("role"):
                p.add_run(f' — {proj["role"]}').font.size = Pt(9)
            date_parts = []
            if proj.get("start_date"):
                date_parts.append(str(proj["start_date"]))
            if proj.get("end_date"):
                date_parts.append(str(proj["end_date"]))
            if date_parts:
                dp = doc.add_paragraph(" ~ ".join(date_parts))
                dp.runs[0].font.size = Pt(9)
                dp.runs[0].font.color.rgb = RGBColor(128, 128, 128)
            if proj.get("tech_stack"):
                ts = doc.add_paragraph(f'技术栈：{", ".join(proj["tech_stack"])}')
                ts.runs[0].font.size = Pt(9)
            if proj.get("description"):
                desc = doc.add_paragraph(proj["description"])
                desc.paragraph_format.line_spacing = 1.6
            highlights = proj.get("highlights") or []
            for h in highlights:
                doc.add_paragraph(str(h), style="List Bullet")

    # Education
    education = resume_data.get("education") or []
    if education:
        add_section_heading("教育背景")
        for edu in education:
            date_str = f'{edu.get("start_date", "")} ~ {edu.get("end_date", "")}'
            line = f'{edu.get("school", "")} — {edu.get("major", "")} ({edu.get("degree", "")})  {date_str}'
            p = doc.add_paragraph(line)
            p.paragraph_format.line_spacing = 1.5
            if edu.get("description"):
                doc.add_paragraph(edu["description"])

    # Skills
    if skills:
        add_section_heading("专业技能")
        for s in skills:
            name = s.get("name", "")
            cat = s.get("category", "")
            level = s.get("level", "")
            label = f'{name}' + (f' ({level})' if level else '') + (f' — {cat}' if cat else '')
            doc.add_paragraph(label, style="List Bullet")

    # Chat highlights
    if resume_data.get("chat_highlights"):
        add_section_heading("AI 建议精华")
        doc.add_paragraph(resume_data["chat_highlights"])

    from io import BytesIO
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()
