const fs = require("fs");
const fp = "backend/app/utils/document_gen.py";
let c = fs.readFileSync(fp, "utf8");
// Need to add margin-top to body to push content below @page margin area
c = c.replace(
  'body style="font-family:CJK',
  'body style="padding-top:18mm;font-family:CJK'
);
fs.writeFileSync(fp, c, "utf8");
console.log("DONE");
