lines = open("app/utils/document_gen.py", "r", encoding="utf-8").readlines()
for i in [321, 323, 325]:
    if i < len(lines):
        lines[i] = lines[i].replace("clear\"/>\'))", 'clear\"/>\'))')  # nop, just fix syntax
        lines[i] = lines[i][:-1]  # remove trailing newline for processing
        if lines[i].endswith("/>))"):
            lines[i] = lines[i][:-4] + "/>'))\n"
        else:
            lines[i] = lines[i] + "\n"
open("app/utils/document_gen.py", "w", encoding="utf-8").writelines(lines)
print("Done fixing")
