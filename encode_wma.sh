for dir in ./Musify/*/*/*.mp3; do
	base=${dir##./Musify}
	base_wma='./MusifyWMA'$base
	filename=${base_wma%.mp3}.wma
	parentdir="$(dirname "$filename")"
	mkdir -p "$parentdir"
	ffmpeg -hide_banner -loglevel warning -i "$dir" -c:a wmav2 -n "$filename"
done;
