# Build the clips!
import csv
import json
import os
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
	def download_raw(self):
		# 1) Query the Twitch API and find the thumbnail_url
		r = requests.get("https://api.twitch.tv/helix/clips?id=" + self.slug,
			headers={"Client-ID": client_id},
		)
		r.raise_for_status()
		thumb = r.json()["data"][0]["thumbnail_url"]
		# 2) Remove "-preview-" to end of string, add ".mp4"
		video = thumb.split("-preview-")[0] + ".mp4"
		# 3) Download that file, save it
		print("Downloading %s..." % self.raw_fn)
		r = requests.get(video)
		r.raise_for_status()
		with open(self.raw_fn, "wb") as f:
			f.write(r.content)
	def precache(self):
		self.slug = self.slug.replace("https://clips.twitch.tv/", "")
		self.raw_fn = "cache/%s.mp4" % self.slug
		try: os.stat(self.raw_fn)
		except FileNotFoundError: self.download_raw()
		# 4) Trim the file to the specified start/dur, save under new name
		...

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
	try: os.mkdir("cache")
	except FileExistsError: pass
	for piece in pieces:
		piece.precache()
	build_compilation(pieces, output)

if __name__ == "__main__":
	main("BestClips", "BestClips.mkv")
