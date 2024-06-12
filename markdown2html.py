#!/usr/bin/python3
"""
    Markdown to HTML conversion script
"""
if __name__ == "__main__":
    import sys
    from os import path
    import re
    import hashlib

    tags_map = {"#": "h1", "##": "h2", "###": "h3", "####": "h4", "#####": "h5", "######": "h6", "-": "ul", "*": "ol"}

    if len(sys.argv) < 3:
        sys.stderr.write("Usage: ./markdown2html.py README.md README.html\n")
        exit(1)

    if not path.exists(sys.argv[1]) or not str(sys.argv[1]).endswith(".md"):
        sys.stderr.write("Missing " + sys.argv[1] + '\n')
        exit(1)

    def convert_heading(line_split):
        tag = tags_map[line_split[0]]
        formatted_line = line.replace("{} ".format(line_split[0]), "<{}>".format(tag))
        formatted_line = formatted_line.rstrip() + ("</{}>\n".format(tag))
        fw.write(formatted_line)

    def apply_inline_formatting(line, pattern):
        is_open = False
        while pattern in line:
            if not is_open:
                line = line.replace(pattern, "<b>" if pattern == "**" else "<em>", 1)
                is_open = True
            else:
                line = line.replace(pattern, "</b>" if pattern == "**" else "</em>", 1)
                is_open = False
        return line

    def convert_md5_links(line):
        while "[[" in line and "]]" in line:
            start = line.index("[[")
            end = line.index("]]", start)
            to_hash = line[start + 2:end]
            hashed = hashlib.md5(to_hash.encode()).hexdigest()
            line = line.replace(f"[[{to_hash}]]", hashed)
        return line

    def convert_case_insensitive_links(line):
        while '((' in line and '))' in line:
            start = line.index("((")
            end = line.index("))", start)
            original_text = line[start + 2:end]
            cleaned_text = original_text.replace('c', '').replace('C', '')
            line = line.replace(f"(({original_text}))", cleaned_text)
        return line 

    with open(sys.argv[1], 'r') as fr, open(sys.argv[2], 'w') as fw:
        in_list = False
        in_paragraph = False
        lines = fr.readlines()
        for idx, line in enumerate(lines):
            if "**" in line:
                line = apply_inline_formatting(line, "**")
            if "__" in line:
                line = apply_inline_formatting(line, "__")
            if "[[" in line and "]]" in line:
                line = convert_md5_links(line)
            if "((" in line and "))" in line:
                line = convert_case_insensitive_links(line)

            line_split = line.split(' ')
            if line_split[0] in tags_map:
                if line_split[0].startswith('#'):
                    convert_heading(line_split)
                elif line_split[0].startswith("-") or line_split[0].startswith("*"):
                    tag = tags_map[line_split[0]]
                    if not in_list:
                        fw.write("<{}>\n".format(tag))
                        in_list = line_split[0]
                    item = line.replace(f"{line_split[0]} ", "<li>")[:-1] + "</li>\n"
                    fw.write(item)
                    if idx == len(lines) - 1 or not lines[idx + 1].startswith(f"{in_list} "):
                        fw.write("</{}>\n".format(tag))
                        in_list = False
            else:
                if line.strip():
                    if not in_paragraph:
                        fw.write("<p>\n")
                        in_paragraph = True
                    fw.write(line)
                    if idx != len(lines) - 1 and lines[idx + 1].strip() and lines[idx + 1].split(' ')[0] not in tags_map:
                        fw.write("<br/>\n")
                    else:
                        fw.write("</p>\n")
                        in_paragraph = False
        exit(0)
