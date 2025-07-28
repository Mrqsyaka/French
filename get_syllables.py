import csv

# Input and output filenames
known_syllables_file = "known_syllables.txt"

# Read existing known syllables into a set
known_syllables = set()
try:
    with open(known_syllables_file, "r", encoding="utf-8") as f:
        for line in f:
            syllable = line.strip()
            if syllable:  # Skip empty lines
                known_syllables.add(syllable)
    print(f"Loaded {len(known_syllables)} known syllables")
except FileNotFoundError:
    print("No existing known syllables file found, starting fresh")

# Keep track of original known syllables to identify new ones
original_known_syllables = known_syllables.copy()

input_path = "Lexique383.tsv"
output_path = "cv_cvc_entries.tsv"
ipa_map = str.maketrans({
    "E": "ɛ",
    "e": "e",
    "§": "ɔ̃",   # or "ɑ̃" depending on context
    "@": "ɑ̃",
    "5": "ɛ̃",
    "Z": "ʒ",
    "R": "ʁ",
    "S": "ʃ",
    "2": "ø",
    "9": "œ",
    "1": "ə",
    "°": "ə",    # schwa (empty vowel)
    "O": "ɔ",    # open-mid back rounded vowel
})
# First pass: collect all matching rows
matching_rows = []
seen_combinations = set()  # Track unique (ortho, phon) combinations

with open(input_path, encoding="utf-8") as f_in:
    # Read rows from the TSV input
    reader = csv.DictReader(f_in, delimiter="\t")

    # Iterate through every row
    for row in reader:
        # Access and clean the cvcv field (17th column)
        pattern = row["cvcv"].strip()

        # Only keep rows where the pattern is exactly "CV" or "CVC"
        if pattern in ("CV", "CVC"):
            # Get the syllable (using ortho field)
            syllable = row["ortho"].strip()

            # Skip if this syllable is already known
            if syllable in known_syllables:
                continue

            # Create a combination key for deduplication
            ortho_clean = row["ortho"]
            phon_clean = row["phon"].translate(ipa_map)
            combination_key = (ortho_clean, phon_clean)

            # Skip if we've already seen this exact combination
            if combination_key in seen_combinations:
                continue

            # Add to seen combinations
            seen_combinations.add(combination_key)

            # Add this new syllable to our known set to avoid duplicates in this session
            # known_syllables.add(syllable)

            # Add to our collection for sorting
            matching_rows.append(row)

# Sort by freqfilms2 (descending - highest frequency first)
matching_rows.sort(key=lambda x: float(x["freqfilms2"]) if x["freqfilms2"] else 0, reverse=True)

# Second pass: write sorted rows to output file
with open(output_path, "w", encoding="utf-8", newline="") as f_out:
    # Use a simple writer since we're only writing ortho and phon
    writer = csv.writer(f_out, delimiter="\t")

    for row in matching_rows:
        # Print the matching row dictionary to the console
        print(row["ortho"], row["phon"], f"freq: {row['freqfilms2']}")

        # Write the row to the output TSV file
        ortho_clean = row["ortho"]
        phon_clean = row["phon"].translate(ipa_map)
        writer.writerow([ortho_clean, phon_clean])

print("Finished: all CV and CVC patterns extracted and saved.")

# Update the known syllables file with new syllables found in this session
new_syllables = known_syllables - original_known_syllables
if new_syllables:
    with open(known_syllables_file, "w", encoding="utf-8") as f:
        # Write all known syllables back to the file
        for syllable in sorted(known_syllables):
            f.write(syllable + "\n")
    print(f"Updated known syllables file. Added {len(new_syllables)} new syllables")
else:
    print("No new syllables found in this session")