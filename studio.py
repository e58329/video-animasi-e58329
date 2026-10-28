import os
import subprocess
import yaml
import asyncio
import edge_tts
from pydub import AudioSegment
from pathlib import Path

def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0

def generate_audio(text, base_name, audio_file):
    print(f"🎙️ Membuat suara Ardi...")
    raw_audio = f"raw_{base_name}.mp3"
    
    async def _generate():
        communicate = edge_tts.Communicate(text, "id-ID-ArdiNeural")
        await communicate.save(raw_audio)

    asyncio.run(_generate())
    
    pitch = 0.85
    cmd_pitch = (
        f'ffmpeg -y -i {raw_audio} '
        f'-af "asetrate=24000*{pitch},aresample=24000,atempo={1/pitch}" '
        f'-c:a libmp3lame {audio_file}'
    )
    subprocess.run(cmd_pitch, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return get_audio_duration(audio_file)

def process_episode(yaml_path):
    base_name = Path(yaml_path).stem
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    
    # Perbaikan: Membaca format dict di dalam points
    full_text = data["question"] + " "
    for section in data.get("sections", []):
        full_text += section["heading"] + ". "
        for point in section["points"]:
            # Cek apakah 'point' berupa dictionary (format baru) atau string (format lama)
            if isinstance(point, dict):
                full_text += point.get("text", "") + " "
            else:
                full_text += point + " "
    full_text += data["conclusion"]
    
    audio_file = f"audio_{base_name}.mp3"
    audio_duration = generate_audio(full_text, base_name, audio_file)
    
    data['audio_duration'] = audio_duration
    temp_yaml = "temp_" + Path(yaml_path).name
    with open(temp_yaml, 'w') as f:
        yaml.dump(data, f)
    
    video_manim = "ExplainerScene.mp4"
    if os.path.exists(video_manim):
        os.remove(video_manim)
        
    print(f"🎥 Merender Manim...")
    subprocess.run(f"python pipeline/render.py {temp_yaml}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(video_manim):
        temp_combined = "temp_combined.mp4"
        print("🔗 Menggabungkan video dan audio...")
        cmd_merge = f'ffmpeg -y -i "{video_manim}" -i "{audio_file}" -c:v copy -c:a aac -shortest "{temp_combined}"'
        subprocess.run(cmd_merge, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        out_name = f"final_{base_name}.mp4"
        print("🔥 Meminta auto-subs membakar subtitle (Mohon tunggu)...")
        
        cmd_autosubs = f'auto-subs transcribe "{temp_combined}" --model small --burn -o "{out_name}"'
        subprocess.run(cmd_autosubs, shell=True)
        
        if os.path.exists(temp_combined): os.remove(temp_combined)
        if os.path.exists(video_manim): os.remove(video_manim)
        print(f"🚀 Selesai: {out_name}")
    else:
        print("❌ Gagal merender Manim.")
    
    os.remove(temp_yaml)

if __name__ == "__main__":
    for file in Path("content").glob("*.yaml"):
        print(f"\n======================================")
        print(f"🚀 MEMPROSES: {file.name}")
        print(f"======================================")
        process_episode(str(file))
