import sys


def filter_clippings_pdf(content, pdf_name):
    entries = content.split('==========')
    new_content = ""
    
    for entry in entries:
        if entry.find(pdf_name) == -1:
            continue
        
        if new_content == "":
            entry = entry.lstrip()
        
        new_content = new_content + entry + "=========="

    return new_content


def main(pdf_path, clippings_path):
    with open(clippings_path, "r", encoding="utf-8-sig") as f:
        clippings_text = f.read()
    pdf_name = pdf_path.rsplit(".", 1)[0]

    new_clipping_text = filter_clippings_pdf(clippings_text, pdf_name)
    
    pdf_clippings_name = pdf_name + "_Clippings.txt"
    with open(pdf_clippings_name, 'w', encoding="utf-8-sig") as output:
        output.write(new_clipping_text)
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python kindle_to_pdf.py input.pdf clippings.txt")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
