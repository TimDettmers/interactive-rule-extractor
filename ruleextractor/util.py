
def search_left(values, start_idx, query_set):
    while start_idx >= 0:
        if values[start_idx] in query_set:
            break
        start_idx -=1
    return start_idx

def search_right(values, start_idx, query_set):
    while start_idx < len(values):
        if values[start_idx] in query_set:
            break
        start_idx +=1
    return start_idx

def merge_idx(values, idx):
    value = values[idx]
    left_idx = idx
    right_idx = idx
    indices = []
    while left_idx > 0:
        left_idx -= 1
        if value == values[left_idx]: indices.insert(0, left_idx)
        else: break
    indices.append(idx)

    while right_idx < len(values)-1:
        right_idx += 1
        if value == values[right_idx]: indices.append(right_idx)
        else: break

    return indices

def merge_indicies_to_text(values_words, indicies):
    return ' '.join(values_words[indicies[0]:indicies[-1]+1])

def get_idx_of_query_tokens(values, query_tokens):
    indices = []
    for token in query_tokens:
        indices += [i for i, x in enumerate(values) if x == token]
    indices = list(set(indices))
    indices.sort()
    prev_idx = None
    start_idx = None
    end_idx = None
    for idx in indices:
        if prev_idx is not None:
            if idx == prev_idx +1:
                if start_idx is None: start_idx = prev_idx
                end_idx = idx
            else:
                if start_idx is not None:
                    if end_idx is not None and end_idx - start_idx + 1== len(query_tokens):
                        return start_idx, end_idx
                    else:
                        start_idx = None

        prev_idx = idx
    if end_idx == None: return -1, -1
    if end_idx - start_idx +1 == len(query_tokens):
        return start_idx, end_idx



