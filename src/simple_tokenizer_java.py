def simple_tokenize_java(src: str):
    """
    Remove // and /* */ comments and split only on whitespace.
    Returns consecutive non-whitespace runs as tokens.
    Note: this does not handle things inside strings (but we do not have those in the dataset)
    """
    tokens = []
    cur = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        nxt = src[i + 1] if i + 1 < n else ''

        # line comment: //
        if ch == '/' and nxt == '/':
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 2
            while i < n and src[i] != '\n':
                i += 1
            continue

        # block comment: /* ... */
        if ch == '/' and nxt == '*':
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 2
            while i + 1 < n and not (src[i] == '*' and src[i + 1] == '/'):
                i += 1
            i = i + 2 if i + 1 < n else n
            continue

        # whitespace splits tokens
        if ch in (' ', '\t', '\r', '\n'):
            if cur:
                tokens.append(''.join(cur)); cur = []
            i += 1
            continue

        # accumulate non-whitespace chars
        cur.append(ch)
        i += 1

    if cur:
        tokens.append(''.join(cur))
    return tokens
