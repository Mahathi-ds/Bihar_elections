import os


def split_text_into_chunks(input_file, output_folder, chunk_size=300):
    """
    Split a text file into chunks based on word count.
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"\nProcessing: {input_file}")
    print(f"Text length: {len(text)} characters")

    words = text.split()

    print(f"Total words: {len(words)}")

    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = ' '.join(words[i:i + chunk_size])

        if len(chunk.strip()) > 50:
            chunks.append(chunk)

    os.makedirs(output_folder, exist_ok=True)

    for idx, chunk in enumerate(chunks, start=1):

        chunk_file = os.path.join(
            output_folder,
            f'chunk_{idx}.txt'
        )

        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunk)

    print(f"Created {len(chunks)} chunks")
    print(f"Saved to: {output_folder}")



# AIADMK


split_text_into_chunks(
    input_file='../data/cleaned_manifesto/AIADMK.txt',
    output_folder='../data/chunks/manifesto/AIADMK',
    chunk_size=300
)

#DMK

split_text_into_chunks(
    input_file='../data/cleaned_manifesto/DMK.txt',
    output_folder='../data/chunks/manifesto/DMK',
    chunk_size=300
)
# TVK


split_text_into_chunks(
    input_file='../data/cleaned_manifesto/TVK.txt',
    output_folder='../data/chunks/manifesto/TVK',
    chunk_size=300
)