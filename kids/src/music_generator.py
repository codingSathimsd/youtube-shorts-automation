import os
import random
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine, Square, Sawtooth
from datetime import datetime

# ── Musical building blocks ──────────────────────────────────────────────────

# Note frequencies (Hz) — C4 to B5 range, kid-friendly bright octaves
NOTES = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23,
    "G4": 392.00, "A4": 440.00, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46,
    "G5": 783.99, "A5": 880.00, "B5": 987.77,
    "REST": 0
}

# Kid-friendly scales (always sound happy and bright)
SCALES = {
    "C_major":      ["C4","D4","E4","F4","G4","A4","B4","C5"],
    "G_major":      ["G4","A4","B4","C5","D5","E5","F5","G5"],
    "F_major":      ["F4","G4","A4","B4","C5","D5","E5","F5"],
    "C_pentatonic": ["C4","D4","E4","G4","A4","C5","D5","E5"],
    "G_pentatonic": ["G4","A4","B4","D5","E5","G5","A5","B5"],
}

# Happy chord progressions (I-V-vi-IV feel)
CHORD_PROGRESSIONS = [
    ["C4","E4","G4"],   # C major
    ["G4","B4","D5"],   # G major
    ["A4","C5","E5"],   # A minor
    ["F4","A4","C5"],   # F major
]

# Moods mapped to musical parameters
MOODS = {
    "adventure": {
        "scale": "G_major",
        "tempo_bpm": 120,
        "melody_energy": "high",
        "chord_rhythm": "quarter",
        "description": "upbeat adventure"
    },
    "wonder": {
        "scale": "C_pentatonic",
        "tempo_bpm": 90,
        "melody_energy": "medium",
        "chord_rhythm": "half",
        "description": "dreamy wonder"
    },
    "excitement": {
        "scale": "C_major",
        "tempo_bpm": 135,
        "melody_energy": "high",
        "chord_rhythm": "quarter",
        "description": "exciting and lively"
    },
    "gentle": {
        "scale": "F_major",
        "tempo_bpm": 75,
        "melody_energy": "low",
        "chord_rhythm": "whole",
        "description": "soft and gentle"
    },
    "playful": {
        "scale": "G_pentatonic",
        "tempo_bpm": 110,
        "melody_energy": "medium",
        "chord_rhythm": "quarter",
        "description": "playful and fun"
    }
}

# ── Tone generation helpers ───────────────────────────────────────────────────

def make_tone(freq, duration_ms, volume_db=-20, wave="sine"):
    """Generate a single musical tone"""
    if freq == 0:  # REST
        return AudioSegment.silent(duration=duration_ms)
    if wave == "sine":
        tone = Sine(freq).to_audio_segment(duration=duration_ms)
    elif wave == "square":
        tone = Square(freq).to_audio_segment(duration=duration_ms)
    else:
        tone = Sine(freq).to_audio_segment(duration=duration_ms)

    # Apply fade in/out to remove clicks
    fade_ms = min(30, duration_ms // 4)
    tone = tone.fade_in(fade_ms).fade_out(fade_ms)
    tone = tone + volume_db
    return tone

def make_chord(notes, duration_ms, volume_db=-26):
    """Generate a chord by overlaying multiple tones"""
    chord = AudioSegment.silent(duration=duration_ms)
    for note_name in notes:
        freq = NOTES.get(note_name, 0)
        if freq > 0:
            tone = make_tone(freq, duration_ms, volume_db, wave="sine")
            chord = chord.overlay(tone)
    return chord

def apply_envelope(segment, attack_ms=20, decay_ms=50, sustain_db=-3, release_ms=100):
    """Apply ADSR-like envelope for more natural sound"""
    fade_in_ms = min(attack_ms, len(segment) // 4)
    fade_out_ms = min(release_ms, len(segment) // 4)
    return segment.fade_in(fade_in_ms).fade_out(fade_out_ms) + sustain_db

# ── Melody generation ─────────────────────────────────────────────────────────

def generate_melody_pattern(scale_notes, energy, num_bars=8):
    """Generate a melodic pattern based on energy level"""
    pattern = []
    seed = int(datetime.now().strftime("%j"))  # day-of-year seed = different every day
    rng = random.Random(seed)

    if energy == "high":
        # Faster notes, more movement
        note_choices = ["eighth", "eighth", "quarter", "eighth", "sixteenth"]
        rest_chance = 0.05
    elif energy == "medium":
        note_choices = ["quarter", "quarter", "half", "eighth", "quarter"]
        rest_chance = 0.10
    else:  # low
        note_choices = ["half", "quarter", "whole", "quarter"]
        rest_chance = 0.15

    # Build melodic phrase (8 bars x 4 beats)
    total_beats = num_bars * 4
    beats_used = 0
    prev_idx = len(scale_notes) // 2  # start from middle of scale

    while beats_used < total_beats:
        # Move stepwise mostly, occasional jumps
        move = rng.choices([-2,-1,-1,0,1,1,2], k=1)[0]
        next_idx = max(0, min(len(scale_notes)-1, prev_idx + move))

        # Occasional rest
        if rng.random() < rest_chance:
            note_name = "REST"
        else:
            note_name = scale_notes[next_idx]
            prev_idx = next_idx

        duration_type = rng.choice(note_choices)
        pattern.append((note_name, duration_type))

        beat_map = {"sixteenth": 0.25, "eighth": 0.5, "quarter": 1.0, "half": 2.0, "whole": 4.0}
        beats_used += beat_map.get(duration_type, 1.0)

    return pattern

def render_melody(pattern, tempo_bpm, volume_db=-18):
    """Convert melody pattern to audio"""
    beat_ms = int(60000 / tempo_bpm)  # ms per beat
    duration_map = {
        "sixteenth": beat_ms // 4,
        "eighth": beat_ms // 2,
        "quarter": beat_ms,
        "half": beat_ms * 2,
        "whole": beat_ms * 4
    }

    melody = AudioSegment.empty()
    for note_name, duration_type in pattern:
        dur = duration_map.get(duration_type, beat_ms)
        freq = NOTES.get(note_name, 0)
        tone = make_tone(freq, dur, volume_db, wave="sine")
        tone = apply_envelope(tone, attack_ms=15, release_ms=min(50, dur//3))
        melody += tone

    return melody

# ── Chord / bass generation ───────────────────────────────────────────────────

def generate_chord_track(progression, tempo_bpm, chord_rhythm, total_duration_ms, volume_db=-30):
    """Generate a chord backing track"""
    beat_ms = int(60000 / tempo_bpm)
    rhythm_map = {"quarter": beat_ms, "half": beat_ms*2, "whole": beat_ms*4}
    chord_dur = rhythm_map.get(chord_rhythm, beat_ms*2)

    chord_track = AudioSegment.silent(duration=0)
    while len(chord_track) < total_duration_ms:
        chord_notes = progression[len(chord_track) // chord_dur % len(progression)]
        chord = make_chord(chord_notes, chord_dur, volume_db)
        chord = apply_envelope(chord, attack_ms=30, release_ms=80)
        chord_track += chord

    return chord_track[:total_duration_ms]

def generate_bass_line(tempo_bpm, total_duration_ms, scale_notes, volume_db=-22):
    """Generate a simple bass line (root notes, one octave down)"""
    beat_ms = int(60000 / tempo_bpm)
    bass_pattern_ms = beat_ms * 2  # bass hits every 2 beats

    # Bass uses lower octave — halve the frequencies of first 4 scale notes
    bass_notes = [NOTES.get(n, 0) / 2 for n in scale_notes[:4]]

    bass_track = AudioSegment.silent(duration=0)
    seed = int(datetime.now().strftime("%j")) + 100
    rng = random.Random(seed)

    while len(bass_track) < total_duration_ms:
        freq = rng.choice(bass_notes)
        tone = make_tone(freq, bass_pattern_ms, volume_db, wave="sine")
        tone = apply_envelope(tone, attack_ms=10, release_ms=60)
        bass_track += tone

    return bass_track[:total_duration_ms]

# ── Percussion ────────────────────────────────────────────────────────────────

def make_kick(volume_db=-15):
    """Soft kick drum using sine sweep"""
    kick = Sine(80).to_audio_segment(duration=150)
    kick = kick + volume_db
    kick = kick.fade_out(100)
    return kick

def make_hihat(volume_db=-25):
    """Hi-hat using short noise burst"""
    # Simulate hi-hat with very high frequency sine
    hihat = Sine(8000).to_audio_segment(duration=40)
    hihat = hihat + volume_db
    hihat = hihat.fade_out(30)
    return hihat

def make_snare(volume_db=-20):
    """Snare using mid-frequency tone"""
    snare = Sine(200).to_audio_segment(duration=80)
    snare = snare + volume_db
    snare = snare.fade_out(60)
    return snare

def generate_drum_track(tempo_bpm, total_duration_ms, energy):
    """Generate a kid-friendly drum pattern"""
    beat_ms = int(60000 / tempo_bpm)
    bar_ms = beat_ms * 4
    drum_track = AudioSegment.silent(duration=total_duration_ms)

    kick = make_kick()
    snare = make_snare()
    hihat = make_hihat()

    pos = 0
    while pos < total_duration_ms - bar_ms:
        # Kick on beat 1 and 3
        if pos + 0 < total_duration_ms:
            drum_track = drum_track.overlay(kick, position=pos)
        if pos + beat_ms * 2 < total_duration_ms:
            drum_track = drum_track.overlay(kick, position=pos + beat_ms * 2)

        # Snare on beat 2 and 4
        if pos + beat_ms < total_duration_ms:
            drum_track = drum_track.overlay(snare, position=pos + beat_ms)
        if pos + beat_ms * 3 < total_duration_ms:
            drum_track = drum_track.overlay(snare, position=pos + beat_ms * 3)

        # Hi-hat every half beat (if high energy)
        if energy in ["high", "medium"]:
            for i in range(8):
                hh_pos = pos + (beat_ms * i // 2)
                if hh_pos < total_duration_ms:
                    drum_track = drum_track.overlay(hihat, position=hh_pos)

        pos += bar_ms

    return drum_track

# ── Magic sparkle effect ──────────────────────────────────────────────────────

def generate_sparkle_fx(total_duration_ms, volume_db=-28):
    """Add random high-pitched sparkle notes for a magical kids feel"""
    sparkle_notes = [NOTES["C5"], NOTES["E5"], NOTES["G5"], NOTES["A5"], NOTES["B5"]]
    sparkle_track = AudioSegment.silent(duration=total_duration_ms)

    seed = int(datetime.now().strftime("%j")) + 200
    rng = random.Random(seed)

    # Add sparkle every 2-4 seconds
    pos = rng.randint(500, 2000)
    while pos < total_duration_ms - 200:
        freq = rng.choice(sparkle_notes)
        dur = rng.randint(80, 200)
        sparkle = make_tone(freq, dur, volume_db, wave="sine")
        sparkle = sparkle.fade_in(20).fade_out(50)
        sparkle_track = sparkle_track.overlay(sparkle, position=pos)
        pos += rng.randint(2000, 4000)

    return sparkle_track

# ── Master music generator ────────────────────────────────────────────────────

def generate_kids_music(mood="playful", duration_seconds=180, output_path="kids_music.mp3"):
    """
    Generate fresh unique kids background music.
    
    Args:
        mood: one of adventure / wonder / excitement / gentle / playful
        duration_seconds: how long the music should be
        output_path: where to save the MP3
    
    Returns:
        output_path if successful, None if failed
    """
    print(f"🎵 Generating fresh kids music (mood: {mood}, duration: {duration_seconds}s)...")

    # Pick mood config (fallback to playful)
    mood_config = MOODS.get(mood, MOODS["playful"])
    scale_name = mood_config["scale"]
    tempo_bpm = mood_config["tempo_bpm"]
    energy = mood_config["melody_energy"]
    chord_rhythm = mood_config["chord_rhythm"]

    scale_notes = SCALES[scale_name]
    total_ms = duration_seconds * 1000

    # Use day-of-year as seed → different music every day, consistent within same day
    daily_seed = int(datetime.now().strftime("%j%Y"))
    random.seed(daily_seed)

    try:
        print(f"  🎼 Scale: {scale_name} | Tempo: {tempo_bpm} BPM | Energy: {energy}")

        # 1. Generate melody
        print("  ♩ Building melody...")
        melody_pattern = generate_melody_pattern(scale_notes, energy, num_bars=16)
        melody = render_melody(melody_pattern, tempo_bpm, volume_db=-16)

        # Loop melody to fill duration
        while len(melody) < total_ms:
            melody = melody + melody
        melody = melody[:total_ms]

        # 2. Generate chords
        print("  🎹 Building chords...")
        chords = generate_chord_track(
            CHORD_PROGRESSIONS, tempo_bpm, chord_rhythm, total_ms, volume_db=-28)

        # 3. Generate bass
        print("  🎸 Building bass line...")
        bass = generate_bass_line(tempo_bpm, total_ms, scale_notes, volume_db=-24)

        # 4. Generate drums
        print("  🥁 Building drum track...")
        drums = generate_drum_track(tempo_bpm, total_ms, energy)

        # 5. Sparkle FX
        print("  ✨ Adding sparkle effects...")
        sparkles = generate_sparkle_fx(total_ms, volume_db=-30)

        # 6. Mix all layers
        print("  🎚️  Mixing all layers...")
        final_mix = AudioSegment.silent(duration=total_ms)
        final_mix = final_mix.overlay(chords)
        final_mix = final_mix.overlay(bass)
        final_mix = final_mix.overlay(drums)
        final_mix = final_mix.overlay(melody)
        final_mix = final_mix.overlay(sparkles)

        # 7. Master: normalize + fade in/out
        final_mix = final_mix.normalize()
        final_mix = final_mix - 6  # pull back 6dB so it doesn't overpower voice
        final_mix = final_mix.fade_in(2000).fade_out(3000)

        # 8. Export
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        final_mix.export(output_path, format="mp3", bitrate="192k")
        print(f"  ✅ Music saved: {output_path} ({duration_seconds}s)")
        return output_path

    except Exception as e:
        print(f"  ❌ Music generation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_music_for_video(topic_plan, video_duration_seconds, output_dir):
    """
    Generate background music matched to the video's mood and length.
    Called automatically from video_assembler.py
    """
    os.makedirs(output_dir, exist_ok=True)

    # Map topic emotion to music mood
    emotion = topic_plan.get("emotion", "playful")
    mood_map = {
        "wonder":      "wonder",
        "excitement":  "excitement",
        "laughter":    "playful",
        "curiosity":   "adventure",
        "adventure":   "adventure",
        "joy":         "playful",
        "calm":        "gentle",
        "happy":       "playful"
    }
    music_mood = mood_map.get(emotion.lower(), "playful")

    output_path = os.path.join(output_dir, f"background_music_{music_mood}.mp3")

    # Add 30 seconds buffer so music doesn't cut abruptly
    music_duration = int(video_duration_seconds) + 30

    result = generate_kids_music(
        mood=music_mood,
        duration_seconds=music_duration,
        output_path=output_path
    )

    return result
  
