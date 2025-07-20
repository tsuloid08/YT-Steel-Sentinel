#!/usr/bin/env python3
import yt_dlp
import tempfile
import os
import glob

def test_ytdlp():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short video for testing
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_base = temp_file.name
    
    print(f"Temp base: {temp_base}")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_base + '.%(ext)s',
        'quiet': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Extracting info...")
            info = ydl.extract_info(url, download=True)
            
            print(f"Info ext: {info.get('ext', 'NO_EXT')}")
            print(f"Info title: {info.get('title', 'NO_TITLE')}")
            
            expected_file = f"{temp_base}.{info['ext']}"
            print(f"Expected file: {expected_file}")
            
            # Check with glob
            found_files = glob.glob(f"{temp_base}.*")
            print(f"Found files: {found_files}")
            
            # Check directory contents
            temp_dir = os.path.dirname(temp_base)
            dir_contents = os.listdir(temp_dir)
            print(f"Temp dir contents: {[f for f in dir_contents if temp_base.split('/')[-1] in f]}")
            
            if os.path.exists(expected_file):
                size = os.path.getsize(expected_file)
                print(f"File exists! Size: {size} bytes")
                # Clean up
                os.remove(expected_file)
                print("File cleaned up")
            else:
                print("File does not exist!")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ytdlp()