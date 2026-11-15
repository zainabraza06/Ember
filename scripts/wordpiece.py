"""BERT (uncased) WordPiece tokenizer used for the BGE embeddings, kept identical to scripts/semantic_core.js.
tests/test_semantic.py checks that both give the same token ids. Standard library only."""
import unicodedata

UNK, CLS, SEP, PAD = '[UNK]', '[CLS]', '[SEP]', '[PAD]'


def load_vocab(path):
    with open(path, encoding='utf-8') as f:
        return {line.rstrip('\n'): i for i, line in enumerate(f)}


def _is_punct(ch):
    cp = ord(ch)
    if 33 <= cp <= 47 or 58 <= cp <= 64 or 91 <= cp <= 96 or 123 <= cp <= 126:
        return True
    return unicodedata.category(ch).startswith('P')


def basic_tokens(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if cp == 0 or cp == 0xFFFD or (unicodedata.category(ch) in ('Cc', 'Cf') and ch not in '\t\n\r'):
            continue
        out.append(' ' if ch in '\t\n\r' or unicodedata.category(ch) == 'Zs' else ch)
    text = ''.join(out).lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    toks = []
    for word in text.split():
        cur = ''
        for ch in word:
            if _is_punct(ch):
                if cur:
                    toks.append(cur); cur = ''
                toks.append(ch)
            else:
                cur += ch
        if cur:
            toks.append(cur)
    return toks


def wordpiece(token, vocab):
    if len(token) > 100:
        return [UNK]
    pieces, start = [], 0
    while start < len(token):
        end, found = len(token), None
        while start < end:
            sub = token[start:end]
            if start > 0:
                sub = '##' + sub
            if sub in vocab:
                found = sub
                break
            end -= 1
        if found is None:
            return [UNK]
        pieces.append(found)
        start = end
    return pieces


def encode(text, vocab, max_len=128):
    """[CLS] pieces [SEP], truncated to max_len. Returns a list of token ids."""
    ids = [vocab[CLS]]
    for tok in basic_tokens(text):
        for p in wordpiece(tok, vocab):
            ids.append(vocab.get(p, vocab[UNK]))
    ids = ids[:max_len - 1] + [vocab[SEP]]
    return ids
