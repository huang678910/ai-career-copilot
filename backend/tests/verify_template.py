"""Verify the new template has all expected features."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from app.utils.document_gen import build_html_resume

data = {
    "basic_info": {"name": "张三", "email": "zhang@test.com", "phone": "13800000000", "city": "北京"},
    "target_position": "高级后端工程师",
    "summary": "8年后端开发经验。",
    "skills": [{"category": "后端", "name": "Python", "level": "精通"}],
    "education": [{"school": "清华大学", "degree": "硕士", "major": "计算机", "start_date": "2015-09-01", "end_date": "2018-07-01"}],
    "work_experiences": [{"company": "字节跳动", "title": "后端工程师", "start_date": "2019-03-01", "end_date": "", "description": "后端开发"}],
}

html = build_html_resume(data, "professional")

features = [
    ("header-bar", ".header-bar"),
    ("photo-box", ".photo-box"),
    ("accent-dot", ".accent-dot"),
    ("target-box", ".target-box"),
    ("summary-box", ".summary-box"),
    ("skills-table", ".skills-table"),
    ("item-header", ".item-header"),
    ("item-sub", ".item-sub"),
    ("tech-tag", ".tech-tag"),
    ("section-footer", ".section-footer"),
]

all_ok = True
for name, css_class in features:
    found = css_class.lstrip(".") in html or css_class in html
    status = "OK" if found else "MISSING"
    if not found:
        all_ok = False
    print(f"[{status}] {name} ({css_class})")

# Check old template issues are gone
bad = []
if "display: flex" in html:
    bad.append("display: flex still present")
if "max-width" in html:
    bad.append("max-width still present")
if bad:
    all_ok = False
    for b in bad:
        print(f"[BAD] {b}")
else:
    print("[OK] No legacy CSS issues")

print(f"\nAll features present: {all_ok}")
print(f"HTML size: {len(html)} bytes")
