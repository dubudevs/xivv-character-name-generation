import os
import sys
import traceback
import soundfile as sf
import logging
import subprocess

# === CONFIGURATION ===
CUSTOM_DATA_DIR = "data/CustomData"
CONVERTED_DATA_DIR = "data/FinalOggData"
MAX_PATH_LENGTH = 260
LOG_FILE = "conversion_errors.log"

# === SET UP LOGGING ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def flush_logs():
    for handler in logging.root.handlers:
        handler.flush()

def convert_wav_to_ogg(wav_path, ogg_path):
    """Convert a WAV file to OGG using ffmpeg instead of soundfile."""
    try:
        # Check Path Length
        if len(ogg_path) > 260:
            logging.error(f"Skipping (path too long): {ogg_path}")
            return False

        # Ensure directory exists
        try:
            os.makedirs(os.path.dirname(ogg_path), exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directory: {e}")
            return False

        print(f"Converting {wav_path} -> {ogg_path}")
        logging.info(f"Converting {wav_path} -> {ogg_path}")

        # Use ffmpeg for conversion instead of soundfile
        try:
            # Run ffmpeg with appropriate parameters
            result = subprocess.run(
                ['ffmpeg', '-i', wav_path, '-c:a', 'libopus', '-b:a', '64k', ogg_path],
                check=True,
                capture_output=True,
                text=True
            )
            print("Conversion successful")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg conversion failed for {wav_path}: {e.stderr}")
            print(f"FFmpeg error: {e.stderr}")
            return False
        except FileNotFoundError:
            logging.error("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
            print("FFmpeg not found. Please install FFmpeg and ensure it's in your PATH.")
            return False

    except Exception as e:
        logging.error(f"❌ Error converting {wav_path}:\n{traceback.format_exc()}")
        flush_logs()
        return False

def convert_custom_wav_to_ogg():
    converted_files = 0
    skipped_files = 0
    try:
        for root, _, files in os.walk(CUSTOM_DATA_DIR):
            for file in files:
                if file.endswith(".wav"):
                    try:
                        wav_path = os.path.join(root, file)
                        # Compute relative path & target location
                        rel_path = os.path.relpath(root, CUSTOM_DATA_DIR)
                        ogg_path = os.path.join(CONVERTED_DATA_DIR, rel_path, file.replace(".wav", ".ogg"))
                        
                        # Convert WAV to OGG
                        success = convert_wav_to_ogg(wav_path, ogg_path)
                        if success:
                            converted_files += 1
                            logging.info(f"✅ Converted {converted_files}: {wav_path} -> {ogg_path}")
                        else:
                            skipped_files += 1
                            print(f"Skipped file {wav_path}")
                    except Exception as e:
                        logging.error(f"Error processing file {file}:\n{traceback.format_exc()}")
                        skipped_files += 1
                    flush_logs()
                    
                    # Print progress every 100 files
                    if converted_files % 100 == 0 and converted_files > 0:
                        logging.info(f"Progress: {converted_files} files converted, {skipped_files} skipped")
                        
        logging.info(f"🎉 Finished: {converted_files} files converted; {skipped_files} skipped.")
        flush_logs()
    except Exception as e:
        logging.error(f"🚨 Fatal error in conversion loop:\n{traceback.format_exc()}")
        flush_logs()

# === RUN SCRIPT ===
if __name__ == "__main__":
    logging.info("🚀 Starting WAV to OGG conversion using FFmpeg...")
    os.makedirs(CONVERTED_DATA_DIR, exist_ok=True)
    
    # Check if ffmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logging.info("FFmpeg is available and will be used for conversion")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("FFmpeg not found or not working properly. Please install FFmpeg.")
        print("Error: FFmpeg not found or not working properly. Please install FFmpeg.")
        sys.exit(1)
        
    convert_custom_wav_to_ogg()
    logging.info("✅ Conversion script finished.")
    flush_logs()