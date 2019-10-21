# Build the clips!
import csv
from dataclasses import dataclass # ImportError? Upgrade to Python 3.7 or pip install dataclasses

@dataclass
class VideoPiece:
	slug: str # eg PoorSavageLorisHassaanChop
	start: float # Start position
	duration: float # 0.0 = till end of clip
	def precache(self):
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
	for piece in pieces:
		piece.precache()
	build_compilation(pieces, output)

if __name__ == "__main__":
	main("BestClips", "BestClips.mkv")
