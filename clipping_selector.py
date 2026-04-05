

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