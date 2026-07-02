const fs = require("fs");
const fp = "backend/app/utils/document_gen.py";
let c = fs.readFileSync(fp, "utf8");
// Increase top padding of header cell from 18px to 32px
c = c.replace(
  'padding:18px 22px;color:#fff',
  'padding:30px 22px 14px 22px;color:#fff'
);
// Also undo the padding-top we just added to body (revert previous bad fix)
c = c.replace(
  'body style="padding-top:18mm;font-family:CJK',
  'body style="font-family:CJK'
);
fs.writeFileSync(fp, c, "utf8");
console.log("DONE");
