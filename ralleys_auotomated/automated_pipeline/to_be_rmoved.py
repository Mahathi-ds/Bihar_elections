from pathlib import Path

results_folder = Path("results/rally_results/NDA/qwen")
chunks_folder = Path("chunks/speeches/NDA")

# Extract video names from detailed CSV filenames
results_names = {
    file.name.removesuffix("_detailed.csv")
    for file in results_folder.glob("*_detailed.csv")
    if file.is_file()
}

# Extract folder names from chunks
chunks_names = {
    folder.name
    for folder in chunks_folder.iterdir()
    if folder.is_dir()
}

# Files in results without matching chunk folders
extra_results = sorted(results_names - chunks_names)

# Chunk folders without matching result files
missing_results = sorted(chunks_names - results_names)

print("\nResults files without matching chunk folders:")
for name in extra_results:
    print(name + "_detailed.csv")

print("\nChunk folders without matching results files:")
for name in missing_results:
    print(name)

print("\n========== COUNTS ==========")
print("Results CSV files:", len(results_names))
print("Chunk folders:", len(chunks_names))
print("Extra results:", len(extra_results))
print("Missing results:", len(missing_results))