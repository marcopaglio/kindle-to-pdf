import fitz
import sys

from clipping_selector import filter_clippings_pdf
from kindle_pdf import parse_clippings, check_page_indexing, search_and_highlight


def main(pdf_path, clippings_path):
    # 1. Open clippings text file
    with open(clippings_path, "r", encoding="utf-8-sig") as f:
        clippings_text = f.read()

    # 2. Filter clippings by pdf name
    pdf_name = pdf_path.rsplit(".", 1)[0] 
    # TODO: this not work if pdf has "." in the name. Es: hello.world.pdf
    filtered_clipping_text = filter_clippings_pdf(clippings_text, pdf_name)
    
    # 3. Save new clippings in kindle style
    clippings_output_path = pdf_name + "_Clippings.txt"
    with open(clippings_output_path, 'w', encoding="utf-8-sig") as output:
        output.write(filtered_clipping_text)
    print(f"\nFiltered clippings saved to: {clippings_output_path}")


    # 4. Convert clipping in document-friendly highlights
    highlights = parse_clippings(filtered_clipping_text)
    print(f"Found {len(highlights)} highlights in clippings")
    
    # 5. Check index page offset
    doc = fitz.open(pdf_path)
    offset = check_page_indexing(doc, highlights)
    print(f"\nCalculated offset is: {offset}")
                         
    # 6. Search and highlight
    processed, remaining = search_and_highlight(doc, highlights, offset)
    print(f"\nHighlights applied: {len(processed)} / {len(highlights)}")
    

    # 7. Save highlighted pdf
    pdf_output_path = pdf_name + "_annotated.pdf"
    doc.save(pdf_output_path)
    print(f"\nAnnotated PDF saved to: {pdf_output_path}")

    # 8. Save not found highlights
    remaining_output_path = pdf_name + "_notFound.txt"
    with open(remaining_output_path, 'w', encoding="utf-8-sig") as output:
        output.write(f"Highlights applied: {len(processed)} / {len(highlights)}\n\n")
        for hl in remaining:
            output.write(f"- {hl['content'][:100]} at page {hl['page']-offset}\n")




if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python kindle_to_pdf.py \"input.pdf\" \"clippings.txt\"")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])