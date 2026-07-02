const fs = require("fs");
const fp = "backend/app/utils/document_gen.py";
let c = fs.readFileSync(fp, "utf8");
c = c.replace('@page { size: A4; }', '@page { size: A4; margin: 18mm 20mm; }');
c = c.replace('18mm 20mm 12mm 20mm', 'width:100%;margin:0');
c = c.replace('<div style="padding:12px 22px 15px 22px;">', '');
c = c.replace('parts.append("</div>")', '');
fs.writeFileSync(fp, c, "utf8");
console.log("DONE");
