# Build the clips!

# 1) Read and parse the file

def parse_template(fn):
	...

# 2) Download all clips into the local cache
def precache(slug):
	...

# 3) Build images or video files for title cards (and, again, cache)
def make_title(text):
	...

# 4) Stitch the files together into an output file
def build_compilation(videos, output):
	...

def main(fn, output):
	pieces = parse_template(fn)
	print(pieces)
	for piece in pieces:
		if piece is "video": precache(piece)
		elif piece is "text": make_title(piece)
	build_compilation(pieces, output)

if __name__ == "__main__":
	main("BestClips", "BestClips.mkv")
