def split_into_chunks(lst, num_chunks):
    chunk_size = (len(lst) + num_chunks - 1) // num_chunks
    chunks = [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]
    return chunks

print(split_into_chunks(["hello", "world","fs", "fadf", "...", "dffa","fdfsafds", "afdsa"], 5))

