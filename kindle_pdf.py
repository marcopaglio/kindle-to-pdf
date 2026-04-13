import re
import unicodedata
from tqdm import tqdm
from rapidfuzz import fuzz

# ------------------------------------------------------------
# Text utilities
# ------------------------------------------------------------

def normalize_text(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.lower()
    s = re.sub(r'[\W_]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def sliding_windows(words, window_size, step=1):
    for i in range(0, len(words) - window_size + 1, step):
        yield i, " ".join(words[i:i + window_size])


def fuzzy_find_in_page(page_text, highlight_text, threshold=80):
    page_norm = normalize_text(page_text)
    hl_norm = normalize_text(highlight_text)

    if not page_norm or not hl_norm:
        return None, 0

    page_words = page_norm.split()
    hl_words = hl_norm.split()

    window_size = max(len(hl_words), 5)

    best_score = 0
    best_window = None

    for _, window in sliding_windows(page_words, window_size, step=1):
        score = fuzz.partial_ratio(hl_norm, window)
        if score > best_score:
            best_score = score
            best_window = window

    if best_score >= threshold:
        return best_window, best_score

    return None, best_score


def search_keywords(page, text, max_words=6):
    words = text.split()
    for i in range(len(words)):
        query = " ".join(words[i:i + max_words])
        if not query:
            continue
        quads = page.search_for(query, quads=True)
        if quads:
            return quads
    return None


# -------------------------
# Duplication tools
# -------------------------

def extract_keywords(text, min_len=4):
    words = normalize_text(text).split()
    return set(w for w in words if len(w) >= min_len)


def rects_overlap(r1, r2):
    return r1.intersects(r2)


def is_already_highlighted(page, quads, existing_rects):
    for quad in quads:
        for er in existing_rects:
            if rects_overlap(quad.rect, er):
                return True
    return False


# ------------------------------------------------------------
# Kindle clippings parser
# ------------------------------------------------------------

def parse_clippings(content):
    entries = content.split('==========')
    highlights = []

    for entry in entries:
        lines = [l.strip() for l in entry.strip().split('\n') if l.strip()]
        if len(lines) < 3:
            continue

        metadata = lines[1]
        page_match = re.search(r'pagina (\d+)', metadata, re.IGNORECASE)
        if not page_match:
            continue

        text = " ".join(lines[2:])
        text = re.sub(r'\s+', ' ', text).replace('\u00a0', ' ').strip()

        highlights.append({
            "page": int(page_match.group(1)),
            "content": text
        })

    return highlights


# ------------------------------------------------------------
# Checker of validity
# ------------------------------------------------------------


def is_valid_match(highlight_text, matched_window,
                   min_coverage=1.0,
                   min_len_ratio=1.0):

    hl_norm = normalize_text(highlight_text)
    win_norm = normalize_text(matched_window)

    hl_words = hl_norm.split()
    win_words = set(win_norm.split())

    if not hl_words:
        return False

    # 1. Coverage lessicale
    common_words = [w for w in hl_words if w in win_words]
    coverage = len(common_words) / len(hl_words)

    if coverage < min_coverage:
        return False

    # 2. Lunghezza relativa
    len_ratio = len(win_norm) / len(hl_norm)
    if len_ratio < min_len_ratio:
        return False

    # 3. Controllo inizio/fine
    start_ok = hl_words[0] in win_words
    end_ok = hl_words[-1] in win_words

    if not (start_ok or end_ok):
        return False

    return True



# ------------------------------------------------------------
# Change page number
# ------------------------------------------------------------

def check_page_indexing(doc, highlights):
    for i, hl in enumerate(highlights):
        print(f"\nSearching correspondences for \"{hl['content']}\"...", end="")
        highlight_page = hl["page"]
    
        for page_index, page in enumerate(doc):
            page_number = page_index + 1
            print(f"\n...at page {page_number} of the document", end="")
    
            # Try exact match first (fast)
            quads = page.search_for(hl["content"], quads=True)
            if quads:
                print(": FOUND.")
                offset = highlight_page - page_number
                return offset
            



# ------------------------------------------------------------
# Search and highlight
# ------------------------------------------------------------

def search_and_highlight(doc, highlights, offset):
    processed = set()
    duplicates = []
    remaining = []
    
    for page_index, page in enumerate(tqdm(doc, desc="Processing pages")):
        page_number = page_index + 1
        page_text = page.get_text()
        
        used_words_on_page = set()
        existing_rects = []
        
        # Reverse ordering (necessary for duplicates) 
        # and filter by current page (offset occurs)
        reverse_page_highlights = [
            (i, hl) for i, hl in enumerate(highlights)
            if hl["page"] - offset == page_number and i not in processed
        ][::-1]

        for i, hl in reverse_page_highlights:
            
            # Try exact match first (fast)
            quads = page.search_for(hl["content"], quads=True)
            
            # Fuzzy fallback
            if not quads:
                match, score = fuzzy_find_in_page(page_text, hl["content"])
                if match and is_valid_match(hl["content"], match):
                    quads = search_keywords(page, match)
            
            if quads:
                hl_keywords = extract_keywords(hl["content"])
                
                # Discard duplicated highlights
                if (any(word in used_words_on_page for word in hl_keywords) 
                    and is_already_highlighted(page, quads, existing_rects)):
                    duplicates.append(hl)
                    processed.add(i)
                    continue
                
                # Apply highlights
                annot = page.add_highlight_annot(quads)
                annot.update()
                processed.add(i)
                used_words_on_page.update(hl_keywords)
                for quad in quads:
                    existing_rects.append(quad.rect)


    for i, hl in enumerate(highlights):
        if i not in processed:
            remaining.append(hl)
            
    return processed, duplicates, remaining

