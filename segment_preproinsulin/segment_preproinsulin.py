import re
import sys
import os
import glob

EXPECTED_PREPROINSULIN_LENGTH = 110

SEGMENTS_MAP = [
    (0, 24, 24, "lsinsulin-seq-clean.txt"),
    (24, 54, 30, "binsulin-seq-clean.txt"),
    (54, 89, 35, "cinsulin-seq-clean.txt"),
    (89, 110, 21, "ainsulin-seq-clean.txt"),
]

def process_and_segment_file(file_name):
    
    try:
        with open(file_name, "r") as f:
            dirty_text = f.read()

        metadata_pattern = re.compile(r"(ORIGIN\s*\d+\s*)|(\s*\d+\s*)|(//)|([\n\r])")
        intermediate_text = re.sub(metadata_pattern, "", dirty_text)
        cleaned_sequence = re.sub(r"\s+", "", intermediate_text)

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
        return
    except Exception as e:
        print(f"An unexpected error occurred during reading/cleaning: {e}")
        return

    sequence_length = len(cleaned_sequence)

    print("\n--- Initial Cleaning Report ---")
    print(f"File Processed: {file_name}")
    print(f"Full Cleaned Sequence Length: {sequence_length}")

    if sequence_length != EXPECTED_PREPROINSULIN_LENGTH:
        print(f"Warning: The length ({sequence_length}) does not match the expected length of {EXPECTED_PREPROINSULIN_LENGTH}. Segmentation skipped.")
        return
    
    base_name, ext = os.path.splitext(file_name)
    full_clean_name = base_name + "-clean" + ext
    with open(full_clean_name, "w") as f_full:
        f_full.write(cleaned_sequence)
    print(f"Full cleaned sequence saved to: {full_clean_name}")
    
    print("\n--- Segmentation Report ---")
    
    all_segments_ok = True
    
    for start, end, expected_len, output_file in SEGMENTS_MAP:
        segment = cleaned_sequence[start:end]
        segment_len = len(segment)
        
        try:
            with open(output_file, "w") as f_segment:
                f_segment.write(segment)
                
            status = "OK"
            if segment_len != expected_len:
                status = "WARNING"
                all_segments_ok = False
            
            print(f"Saved: {output_file} (Length: {segment_len} / Expected: {expected_len}) - {status}")

        except Exception as e:
            print(f"Error saving {output_file}: {e}")
            all_segments_ok = False
            
    if all_segments_ok:
        print("\nAll segments created and verified successfully.")
    else:
        print("\nErrors or length mismatches detected during segmentation.")


if len(sys.argv) == 1:
    available_files = glob.glob("*.txt")
    available_files = [f for f in available_files if not f.endswith("-clean.txt") and not f.endswith("-clean.txt")]
    
    if not available_files:
        print("\nNo unprocessed '.txt' files found.")
        sys.exit(0)

    print("\nAvailable '.txt' files for processing:")
    for i, file_name in enumerate(available_files):
        print(f"  [{i+1}] {file_name}")
    
    print("---")
    try:
        selection = input("Enter the NUMBER of the file to process (or Q to quit): ").lower()
        
        if selection == 'q':
            sys.exit(0)
            
        index = int(selection) - 1
        
        if 0 <= index < len(available_files):
            FILE_TO_PROCESS = available_files[index]
            process_and_segment_file(FILE_TO_PROCESS)
        else:
            print("Invalid selection.")
            sys.exit(1)
            
    except ValueError:
        print("Invalid input. Please enter a number or 'Q'.")
        sys.exit(1)
        
elif len(sys.argv) == 2:
    FILE_TO_PROCESS = sys.argv[1]
    process_and_segment_file(FILE_TO_PROCESS)
    
else:
    print("Error: Provide zero or one argument.")
    print("Usage 1 (Interactive): python segment_preproinsulin.py")
    print("Usage 2 (Direct): python segment_preproinsulin.py file_name.txt")
    sys.exit(1)