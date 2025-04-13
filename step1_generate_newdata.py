import os
import json
import shutil
import re
import soundfile as sf

SOURCE_DIR = "N:/XIV_Voices/Data"  # Original folder
NEW_DATA_DIR = "data/OrigData"  # Destination for filtered JSONs & converted WAVs
ORIGINAL_OGG_DIR = "data/OriginalOggs"  # Backup folder for original .ogg files
FILTER_PATTERN = re.compile(r"Arc[^a-z]|_NAME_|_FIRSTNAME_")

def copy_and_convert_files():
    total_files = 0
    converted_files = 0

    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)

                with open(json_path, "r", encoding="utf-8") as f:
                    contents = json.load(f)
                    json_text = json.dumps(contents)

                if FILTER_PATTERN.search(json_text):
                    total_files += 1

                    rel_path = os.path.relpath(root, SOURCE_DIR)
                    new_json_path = os.path.join(NEW_DATA_DIR, rel_path, file)
                    os.makedirs(os.path.dirname(new_json_path), exist_ok=True)
                    shutil.copy2(json_path, new_json_path)
                    print(f"Copied JSON: {json_path} -> {new_json_path}")

                    ogg_file = file.replace(".json", ".ogg")
                    ogg_path = os.path.join(root, ogg_file)

                    if os.path.exists(ogg_path):
                        # Backup original .ogg
                        original_ogg_backup = os.path.join(ORIGINAL_OGG_DIR, rel_path, ogg_file)
                        os.makedirs(os.path.dirname(original_ogg_backup), exist_ok=True)
                        shutil.copy2(ogg_path, original_ogg_backup)
                        print(f"Backed up original OGG: {ogg_path} -> {original_ogg_backup}")

                        # Convert .ogg to .wav
                        wav_path = os.path.join(NEW_DATA_DIR, rel_path, ogg_file.replace(".ogg", ".wav"))
                        os.makedirs(os.path.dirname(wav_path), exist_ok=True)
                        convert_ogg_to_wav(ogg_path, wav_path)
                        converted_files += 1
                        print(f"Converted OGG to WAV: {ogg_path} -> {wav_path}")

    print(f"Finished Step 1: {total_files} JSON files copied, {converted_files} OGG files converted.")

def convert_ogg_to_wav(ogg_path, wav_path):
    data, samplerate = sf.read(ogg_path)
    sf.write(wav_path, data, samplerate)

if __name__ == "__main__":
    print("Starting Step 1: Copying and converting files to NewData...")
    os.makedirs(NEW_DATA_DIR, exist_ok=True)
    os.makedirs(ORIGINAL_OGG_DIR, exist_ok=True)
    copy_and_convert_files()
    print("OrigData is ready. Run step2_generate_customdata.py")
