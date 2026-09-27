import os
import glob


def split_text_into_chunks(input_file, output_folder, chunk_size=150):
    """
    Split a transcript into chunks based on word count.
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    print(f"\nProcessing: {input_file}")

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


# ============================================================
# PROCESS ALL SPEECH TRANSCRIPTS
# ============================================================

parties = ['NDA','Mahagathbandhan']

for party in parties:

    input_folder = f'/Users/ctrl2/Desktop/oelp_hindi/transcripts/{party}'
    output_base = f'/Users/ctrl2/Desktop/oelp_hindi/chunks/speeches/{party}'

    transcript_files = glob.glob(
        os.path.join(input_folder, '*.txt')
    )

    print(f"\n{'=' * 60}")
    print(f"{party}: Found {len(transcript_files)} transcripts")
    print(f"{'=' * 60}")

    for transcript_file in transcript_files:

        # Get transcript filename without .txt
        speech_name = os.path.splitext(
            os.path.basename(transcript_file)
        )[0]

        output_folder = os.path.join(
            output_base,
            speech_name
        )

        split_text_into_chunks(
            input_file=transcript_file,
            output_folder=output_folder,
            chunk_size=150
        )