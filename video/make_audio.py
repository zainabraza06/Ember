"""Builds the voice track (voice_track.wav) and the mixed audio (mix.wav) for the 28 s Ember demo.
Voice: per-sentence WAV files from the Windows built-in text-to-speech voice (Microsoft Mark), trimmed and placed at fixed times, loudness-normalised.
Music: a soft ambient pad synthesised with ffmpeg from sine tones (no samples, no third-party music), set 24 LU below the voice.
Usage: python make_audio.py <ffmpeg.exe> <dir with seg01..seg10.wav and plan.json> <out dir>"""
import json, re, subprocess, sys
from pathlib import Path
ff, vo, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(exist_ok=True)
plan = json.load(open(vo / 'plan.json')); start, trim = plan['start'], plan['trim']
start[1], start[2], start[9] = 2.35, 4.25, 27.75 - plan['len'][9]                     # the second hook sentence lands on its headline; the next scene's voice follows
DUR = 28.0
def run(args): return subprocess.run([ff, '-y', '-hide_banner', '-loglevel', 'error'] + args, check=True)
def lufs(path):
    r = subprocess.run([ff, '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1])
# voice track
ins, fl, labels = [], [], []
for i in range(10):
    ins += ['-i', str(vo / f'seg{i + 1:02d}.wav')]
    ms = int(round(start[i] * 1000))
    fl.append(f'[{i}:a]atrim=start={max(0, trim[i] - .04):.3f},asetpts=PTS-STARTPTS,aresample=44100,adelay={ms}|{ms}[v{i}]'); labels.append(f'[v{i}]')
fl.append(''.join(labels) + f'amix=inputs=10:normalize=0,apad=whole_dur={DUR},atrim=0:{DUR},highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,alimiter=limit=0.9:level=disabled[vo]')
run(ins + ['-filter_complex', ';'.join(fl), '-map', '[vo]', '-ac', '1', '-ar', '44100', str(out / 'voice_raw.wav')])
g = -16 - lufs(out / 'voice_raw.wav')
run(['-i', str(out / 'voice_raw.wav'), '-af', f'volume={g:.2f}dB,alimiter=limit=0.89:level=disabled', '-ar', '44100', '-ac', '1', str(out / 'voice_track.wav')])
vl = lufs(out / 'voice_track.wav')
# ambient pad: slow Am - F - C - G feel from stacked detuned sines, low-passed, with a long echo and a fade in/out
notes = [55, 110, 164.81, 220, 261.63, 329.63, 110.5, 220.8]
src = [f'sine=f={f}:d={DUR}:sample_rate=44100' for f in notes]
fm = ''.join(f'[{i}:a]volume={0.5 if f < 120 else 0.28}[m{i}];' for i, f in enumerate(notes)) + ''.join(f'[m{i}]' for i in range(len(notes))) + f'amix=inputs={len(notes)}:normalize=0,tremolo=f=0.22:d=0.35,lowpass=f=1100,aecho=0.8:0.7:700|1300:0.35|0.25,afade=t=in:st=0:d=1.6,afade=t=out:st={DUR - 1.8}:d=1.8[pad]'
args = []
for s in src: args += ['-f', 'lavfi', '-i', s]
run(args + ['-filter_complex', fm, '-map', '[pad]', '-ac', '1', str(out / 'music_raw.wav')])
mg = (vl - 24) - lufs(out / 'music_raw.wav')
run(['-i', str(out / 'music_raw.wav'), '-af', f'volume={mg:.2f}dB', str(out / 'music.wav')])
run(['-i', str(out / 'voice_track.wav'), '-i', str(out / 'music.wav'), '-filter_complex', f'[0:a][1:a]amix=inputs=2:normalize=0,atrim=0:{DUR},aformat=channel_layouts=stereo[a]', '-map', '[a]', '-ar', '44100', str(out / 'mix.wav')])
print('voice LUFS', round(vl, 1), 'music LUFS', round(lufs(out / 'music.wav'), 1), 'mix LUFS', round(lufs(out / 'mix.wav'), 1))
