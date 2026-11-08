import json
import subprocess
import concurrent.futures

print("==========================================================")
print(" Metal Head Den - Local YouTube Video ID Resolver")
print(" Uses yt-dlp to permanently map exact YouTube Video IDs")
print("==========================================================")

with open('playlists.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def fetch_yt_id(track):
    if track.get('sources', {}).get('youtube'):
        return track['sources']['youtube']
    artist = track['artist'] if track['artist'] != 'nan' else ''
    query = f"ytsearch1:{artist} {track['title']}".strip()
    try:
        res = subprocess.run(
            ['yt-dlp', '--get-id', '--no-playlist', query],
            capture_output=True, text=True, timeout=15
        )
        vid = res.stdout.strip().split('\n')[0]
        if len(vid) == 11:
            track['sources']['youtube'] = vid
            print(f"[OK] {track['title']} -> {vid}")
            return vid
    except Exception as e:
        print(f"[ERR] {track['title']}: {e}")
    return ""

all_tracks = [t for pl in data['playlists'] for t in pl['tracks']]
print(f"Resolving {len(all_tracks)} tracks using parallel workers...")

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(fetch_yt_id, all_tracks)

with open('playlists.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nSaved updated playlists.json with exact YouTube Video IDs!")
