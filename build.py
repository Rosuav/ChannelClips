# Build the clips!
import csv
import json
import os
import subprocess
from dataclasses import dataclass # ImportError? Upgrade to Python 3.7 or pip install dataclasses
import requests # ImportError? pip install requests

# Lift a client ID from another project. TODO: Allow other sources eg env var
with open("../stillebot/twitchbot_config.json") as f:
	client_id = json.load(f)["ircsettings"]["clientid"]

font_file = "Sans"
font_size = 72

@dataclass
class VideoPiece:
	slug: str # eg PoorSavageLorisHassaanChop
	start: str # Start position
	duration: str # "0" = till end of clip
	def download_raw(self):
		# 1) Query the Twitch API and find the thumbnail_url
		r = requests.get("https://api.twitch.tv/helix/clips?id=" + self.slug,
			headers={"Client-ID": client_id},
		)
		r.raise_for_status()
		thumb = r.json()["data"][0]["thumbnail_url"]
		# TODO: Save ["created_at"] somewhere to automatically date-stamp the clips
		# 2) Remove "-preview-" to end of string, add ".mp4"
		video = thumb.split("-preview-")[0] + ".mp4"
		# 3) Download that file, save it
		print("Downloading %s..." % self.raw_fn)
		r = requests.get(video)
		r.raise_for_status()
		with open(self.raw_fn, "wb") as f:
			f.write(r.content)

	def cut_video(self):
		# 4) Trim the file to the specified start/dur, save under new name
		cmd = ["ffmpeg", "-ss", self.start, "-i", self.fn]
		if self.duration != "0": cmd += ["-t", self.duration]
		cmd += ["-c", "copy", self.fn]
		subprocess.check_call(cmd)

	def precache(self):
		self.slug = self.slug.replace("https://clips.twitch.tv/", "")
		self.raw_fn = "cache/%s.mp4" % self.slug
		self.fn = "cache/%s-%s-%s.mp4" % (self.slug, self.start, self.duration)
		try: os.stat(self.raw_fn)
		except FileNotFoundError: self.download_raw()
		try: os.stat(self.fn)
		except FileNotFoundError: self.cut_video()

@dataclass
class TextPiece:
	text: str
	duration: str
	def build_video(self):
		bg = "color=c=#00007F:s=1920x1080:d=" + self.duration
		text = f"drawtext=fontfile={font_file}:fontsize={font_size}:fontcolor=white"
		text += ":x=(w-text_w)/2:y=(h-text_h)/2:text='%s'" % self.text.replace(r"\n", "\n")
		cmd = ["ffmpeg", "-f", "lavfi", "-i", bg, "-vf", text, self.fn]
		subprocess.check_call(cmd)
	def precache(self):
		self.fn = "cache/text-%s.%s.mkv" % (self.text, self.duration)
		try: os.stat(self.fn)
		except FileNotFoundError: self.build_video()
# TODO: Consider using the FFMPEG 'subtitles' filter to add annotations

def remove_comments(iter):
	for line in iter:
		line = line.split("#")[0].strip()
		if line: yield line

# 1) Read and parse the file
def parse_template(fn):
	pieces = []
	with open(fn) as f:
		for line in csv.reader(remove_comments(f), delimiter=' '):
			if len(line) == 2: pieces.append(TextPiece(*line))
			else: pieces.append(VideoPiece(*line))
	return pieces

# 2) Download all clips into the local cache - see VideoPiece.precache()
# 3) Build images or video files for title cards - see TextPiece.precache()

# 4) Stitch the files together into an output file
def build_compilation(videos, output):
	files = "\n".join("file '%s'" % os.path.abspath(v.fn) for v in videos)
	tmpfn = "filelist.txt"
	with open(tmpfn, "w") as f: f.write(files)
	cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", tmpfn, output]
	subprocess.run(cmd, check=True)
	os.unlink(tmpfn)

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
