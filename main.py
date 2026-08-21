import os
import requests
import asyncio
import nest_asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

# Asyncio fix for running in certain environments
nest_asyncio.apply()

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHANNEL_OR_CHAT_ID"

# --- STEP 1: SCRIPT GENERATION ---
def generate_crime_script():
    print("Generating crime script...")
    prompt = "Write a 40-second suspenseful true crime script about an unsolved mystery. Short sentences, dark tone. No emojis."
    url = f"https://text.pollinations.ai/{prompt}"
    response = requests.get(url)
    script_text = response.text
    print("Script Generated:\n", script_text)
    return script_text

# --- STEP 2: VOICE GENERATION (Edge-TTS) ---
async def generate_audio(text, output_file="crime_audio.mp3"):
    print("Generating dark voiceover...")
    # 'en-US-ChristopherNeural' is a deep, serious voice
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_file)
    print("Audio saved!")

# --- STEP 3: IMAGE GENERATION ---
def generate_image(script_text, output_file="crimeon_bg.jpg"):
    print("Generating dark aesthetic image...")
    # LLM se image prompt banwate hain based on script, par abhi simple dark theme use karenge
    prompt = "dark eerie true crime documentary aesthetic, yellow police tape, fog, cinematic lighting, vertical 9:16"
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1920&nologo=true"
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print("Image saved!")
    else:
        print("Image generation failed.")

# --- STEP 4: VIDEO ASSEMBLY (MoviePy) ---
def create_video(image_path, audio_path, output_path="crimeon_daily_short.mp4"):
    print("Merging Audio and Image into Video...")
    
    # Load audio
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Load image and set duration equal to audio
    image_clip = ImageClip(image_path).set_duration(duration)
    
    # Add audio to image
    video = image_clip.set_audio(audio_clip)
    
    # Render video at 24 FPS
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    print("Video rendered successfully!")
    return output_path

# --- STEP 5: POST TO TELEGRAM ---
def post_to_telegram(video_path, caption):
    print("Uploading to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    
    with open(video_path, 'rb') as video_file:
        payload = {'chat_id': CHAT_ID, 'caption': caption}
        files = {'video': video_file}
        response = requests.post(url, data=payload, files=files)
        
    if response.status_code == 200:
        print("Successfully posted to Telegram!")
    else:
        print("Failed to post:", response.text)

# --- MAIN AUTOMATION FLOW ---
def main():
    try:
        # 1. Generate text
        script = generate_crime_script()
        
        # 2. Generate voice
        asyncio.run(generate_audio(script, "crime_audio.mp3"))
        
        # 3. Generate visual
        generate_image(script, "crimeon_bg.jpg")
        
        # 4. Create Video
        final_video = create_video("crimeon_bg.jpg", "crime_audio.mp3", "crimeon_daily_short.mp4")
        
        # 5. Send to Telegram
        caption = "🔪 Today's Mystery File...\n\n#TrueCrime #Mystery #Shorts"
        post_to_telegram(final_video, caption)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
