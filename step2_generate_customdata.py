import os
import json
import re
import random
from f5_tts.api import F5TTS

# === CONFIGURATION ===
SPECIFIED_NAME = "v'zicksa"  # Set the replacement name here
NEW_DATA_DIR = "data/OrigData"         # Source folder from Step 1
CUSTOM_DATA_DIR = "data/CustomData"   # Step 2 output folder
# Regex pattern to detect relevant lines
FILTER_PATTERN = re.compile(r"Arc(?=[^a-z])|_NAME_|_FIRSTNAME_")
# Initialize TTS API
f5tts = F5TTS()

def get_ellipsis_suffix(text_length):
    if text_length < 10:
        return " ..."
    elif text_length < 20:
        return " ..."
    elif text_length < 40:
        return " ..."
    elif text_length < 60:
        return ""
    else:
        return ""

def find_suitable_wav(original_wav_path, min_size_kb=350):
    """Find a suitable WAV file in the same folder:
    - If original is smaller than 150KB, find one over 250KB
    - If no file over 250KB exists, use the largest one in the folder
    """
    original_size_kb = os.path.getsize(original_wav_path) / 1024
    
    print(f"Original file: {os.path.basename(original_wav_path)} is {original_size_kb:.2f}KB")
    
    # If original file is already big enough, use it
    if original_size_kb >= 250:
        print(f"Using original file as it's larger than 150KB")
        return original_wav_path
    
    # Get all wav files in the same directory
    directory = os.path.dirname(original_wav_path)
    wav_files = [os.path.join(directory, f) for f in os.listdir(directory) 
                if f.endswith('.wav') and os.path.isfile(os.path.join(directory, f))]
    
    # Find files over min_size_kb
    suitable_files = [f for f in wav_files if os.path.getsize(f) / 1024 >= min_size_kb]
    
    if suitable_files:
        # Choose a random file from suitable ones
        chosen_file = random.choice(suitable_files)
        chosen_size_kb = os.path.getsize(chosen_file) / 1024
        print(f"Found better file: {os.path.basename(chosen_file)} ({chosen_size_kb:.2f}KB)")
        return chosen_file
    else:
        # If no suitable file found, use the largest one
        if wav_files:
            largest_file = max(wav_files, key=os.path.getsize)
            if largest_file != original_wav_path:
                largest_size_kb = os.path.getsize(largest_file) / 1024
                print(f"No files over {min_size_kb}KB found. Using largest: {os.path.basename(largest_file)} ({largest_size_kb:.2f}KB)")
                return largest_file
    
    # If we get here, either:
    # 1. No better alternatives were found
    # 2. Original file was the largest available
    print(f"Using original file: {os.path.basename(original_wav_path)}")
    return original_wav_path


def process_jsons_and_generate():
    processed_files = 0
    skipped_files = 0
    for root, _, files in os.walk(NEW_DATA_DIR):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                with open(json_path, "r", encoding="utf-8") as f:
                    contents = json.load(f)
                sentence = contents.get("sentence", "")
                if not FILTER_PATTERN.search(sentence):
                    continue  # Skip if pattern not matched
                
                # Goodbye, Warrior of Our Friend
                sentence = re.sub(r"\bWarrior of\s+(?:_NAME_|_FIRSTNAME_|Arc)(?=[^a-zA-Z]|$)", "Warrior of Light", sentence)

                # Remove comma and space before the matched pattern (to avoid awkward pauses)
                cleaned_sentence = re.sub(r",\s+(?=" + FILTER_PATTERN.pattern + r")", " ", sentence)

                # Replace the filtered pattern with the specified name
                gen_text = FILTER_PATTERN.sub(SPECIFIED_NAME, cleaned_sentence)

                if gen_text.endswith("."):
                    gen_text = gen_text.strip()[:-1]
                gen_text = re.sub(r'^[^\w\s]+', '', gen_text.strip())

                text_len = len(gen_text.strip())

                if text_len < 10:
                    speedv = 0.4
                elif text_len < 20:
                    speedv = 0.5
                elif text_len < 40:
                    speedv = 0.6
                elif text_len < 60:
                    speedv = 0.8
                else:
                    speedv = 0.9

                gen_text += get_ellipsis_suffix(len(gen_text.strip()))
                gen_text = gen_text.replace("!", ".")

                rel_path = os.path.relpath(root, NEW_DATA_DIR)
                ref_wav_path_original = os.path.join(root, file.replace(".json", ".wav"))
                new_wav_path = os.path.join(CUSTOM_DATA_DIR, rel_path, file.replace(".json", ".wav"))

                # Skip generation if file already exists
                if os.path.exists(new_wav_path):
                    print(f"Skipping {file} - Output WAV already exists.")
                    skipped_files += 1
                    continue

                ref_wav_path = find_suitable_wav(ref_wav_path_original, 250)

                if ref_wav_path != ref_wav_path_original:
                    print(f"Using alternative reference WAV: {os.path.basename(ref_wav_path)}")

                os.makedirs(os.path.dirname(new_wav_path), exist_ok=True)

                print(f"Generating speech for: {file}")
                wav, sr, spec = f5tts.infer(
                    ref_file=ref_wav_path,
                    ref_text="",
                    gen_text=gen_text,
                    file_wave=new_wav_path,
                    seed=None,
                    nfe_step=32,
                    speed=speedv,
                )

                new_json_path = os.path.join(CUSTOM_DATA_DIR, rel_path, file)
                os.makedirs(os.path.dirname(new_json_path), exist_ok=True)
                # Load original JSON again to append metadata
                with open(json_path, "r", encoding="utf-8") as f:
                    original_data = json.load(f)

                # Add generation parameters
                original_data["generation_parameters"] = {
                    "ref_file": ref_wav_path,
                    "ref_text": "",
                    "gen_text": gen_text,
                    "file_wave": new_wav_path,
                    "seed": None,
                    "nfe_step": 32,
                    "speed": speedv,
                }

                # Add reference WAV path if it's not the original
                if ref_wav_path != ref_wav_path_original:
                    original_data["reference_wav_used"] = ref_wav_path

                # Save updated JSON to CustomData
                new_json_path = os.path.join(CUSTOM_DATA_DIR, rel_path, file)
                os.makedirs(os.path.dirname(new_json_path), exist_ok=True)
                with open(new_json_path, "w", encoding="utf-8") as f:
                    json.dump(original_data, f, ensure_ascii=False, indent=2)

                processed_files += 1
                print(f"Processed {file} - New WAV saved to {new_wav_path}")

    print(f"Finished Step 2: {processed_files} files processed, {skipped_files} skipped (already exist).")


# === RUN SCRIPT ===
if __name__ == "__main__":
    print(f"🚀 Starting Step 2: Generating new audio via API (Replacing *NAME* with '{SPECIFIED_NAME}')...")
    os.makedirs(CUSTOM_DATA_DIR, exist_ok=True)  # Ensure base folder exists
    process_jsons_and_generate()
    print("CustomData is ready. Run step3_convert_wav_to_ogg.py next!")