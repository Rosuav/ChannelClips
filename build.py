# Build the clips!
import csv
import json
from dataclasses import dataclass # ImportError? Upgrade to Python 3.7 or pip install dataclasses
import requests # ImportError? pip install requests

# Lift a client ID from another project. TODO: Allow other sources eg env var
with open("../stillebot/twitchbot_config.json") as f:
	client_id = json.load(f)["ircsettings"]["clientid"]

@dataclass
class VideoPiece:
	slug: str # eg PoorSavageLorisHassaanChop
	start: float # Start position
	duration: float # 0.0 = till end of clip
	def precache(self):
		# 1) Query the Twitch API and find the thumbnail_url
		# 2) Remove "-preview-" to end of string, add ".mp4"
		# 3) Download that file, save it
		# 4) Trim the file to the specified start/dur, save under new name
		self.slug = self.slug.replace("https://clips.twitch.tv/", "")
		r = requests.get("https://api.twitch.tv/helix/clips?id=" + self.slug,
			headers={"Client-ID": client_id},
		)
		r.raise_for_status()
		print(r.json())

@dataclass
class TextPiece:
	text: str
	duration: float
	def precache(self):
		...

def remove_comments(iter):
	for line in iter:
		line = line.split("#")[0].strip()
		if line: yield line

# 1) Read and parse the file
def parse_template(fn):
	pieces = []
	with open(fn) as f:
		for line in csv.reader(remove_comments(f), delimiter=' '):
			if len(line) == 2: pieces.append(TextPiece(line[0], float(line[1])))
			else: pieces.append(VideoPiece(line[0], float(line[1]), float(line[2])))
	return pieces

# 2) Download all clips into the local cache - see VideoPiece.precache()
# 3) Build images or video files for title cards - see TextPiece.precache()

# 4) Stitch the files together into an output file
def build_compilation(videos, output):
	...

def main(fn, output):
	pieces = parse_template(fn)
	print(pieces)
	for piece in pieces:
		piece.precache()
	build_compilation(pieces, output)

if __name__ == "__main__":
	main("BestClips", "BestClips.mkv")
