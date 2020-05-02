import asyncio
import aiofiles
import aiohttp
import m3u8
import pathlib
import uuid

try:
    from cryptography.hazmat.primitives.ciphers.algorithms import AES
except:
    pass

from .utils import getLogger, handler
logger = getLogger(name=__name__)
logger.add_handler(handler)

async def fetch_playlist(url: str, session: aiohttp.ClientSession) -> (bytes, str):
    '''Fetches contents of .m3u8 HLS playlist by its url'''
    async with session.get(url, allow_redirects=False) as response:
        if response.status == 302:
            # Redirect occurs when trying to fetch the playlist using other IP address than the one which was used to get the URLs
            # We cannot allow the library to just follow redirects automatically,
            # because we'll need the final URL to make up absolute URLs out from relative ones in the .m3u8 playlist
            # This function returns the actual url after redirection if it occurs.
            await logger.debug('Redirect-Location: {}'.format(response.headers['Location']))
            # Recursion. Normally 2 redirects occur: 302 Moved Temporarily and 302 Found
            return await fetch_playlist(response.headers['Location'], session)
        elif response.status == 200:
            data = await response.text()
            return data, url

async def fetch_segment(i: int, s: m3u8.Segment, path: pathlib.Path) -> None:
    '''Fetches the transport stream (.ts) segment into a file with *path*.
    Decyphers if needed. Segment should already contain the actual key, not only its URL'''
    async with aiohttp.ClientSession() as session:
        async with session.get(s.absolute_uri) as response:
            if response.status != 200:
                raise Exception(response)
            content = await response.read()
    # Decypher content with the key if needed. Segment's number is used as the Initialization Vector (IV)
    if s.key.uri:
        try:
            cipher = AES.new(
                s.key._value, AES.MODE_CBC, iv=i.to_bytes(length=16, byteorder='big')
            )
            content = cipher.decrypt(content)
        except ValueError as e:
            raise Exception(f'{e}, content length: {len(content)}')
    async with aiofiles.open(path/f'{i}.ts', 'wb') as f:
        await f.write(content)
        await logger.debug(f'Fetched {i}-th segment..')


async def fetch_track(url: str, path: pathlib.Path):
    '''Fetches the whole track (audio file) into a directory with *path*.
    Saves transport streams (.ts) files into the directory, as well as the myslist.txt file to be used inFFmpeg command'''
    async with aiohttp.ClientSession() as session:
        # The actual URL is returned alongside playlist so that absolute URLs could be made up
        playlist, url = await fetch_playlist(url, session)
        m = m3u8.loads(playlist, uri=url)
        # Normally, only 1-2 unique public keys are present in .m3u8 playlist and 7-12 segments are encoded.
        # We can reuse these unique key for all the encoded segments
        for key in m.keys:
            if key.uri:
                async with session.get(key.uri) as response:
                    key._value = await response.read()

    # mylist.txt file is written alongside the .ts files to be used as input in FFmpeg concat command
    async with aiofiles.open(path/'tslist.txt', 'w') as f:
        await f.write('\n'.join(f'file \'{i}.ts\'' for i, s in enumerate(m.segments)))

    # Segments (.ts files) are fetched concurrently for performance
    tasks = []
    for i, s in enumerate(m.segments):
        tasks.append(asyncio.ensure_future(fetch_segment(i, s, path)))
    await asyncio.gather(*tasks)


async def download_hls(url: str, path: pathlib.Path) -> bytes:
    # Prepare a directory for incoming .ts segments
    ts_path = path / uuid.uuid4().hex
    ts_path.mkdir(exist_ok=True)
    try:
        # Fetch all the .ts files and write "tslist.txt"
        await hlscore.fetch_track(url, ts_path)
        # .ts segments should be concatenated using FFmpeg demuxer
        # Simple concatenation will lead to "tape jamming" between segments
        # ffmpeg:           main executable
        # -hide_banner:     does not show general FFmpeg's information on startup
        # -loglevel panic   no logging (only in fatal events)
        # -y                overwrite if exist (not used here because we pipe output)
        # -f concat         function to use - concat demuxer
        # -i <path>         input path (tslist.txt file lisitng .ts segments), e.g.
        #                   '0.ts'
        #                   '1.ts'
        #                   ... etc
        #                   Note: single quotes are important (double quotes will not work).
        #                   Note: all the listed segments must be present
        # -c copy           Codec, simple copy
        # -map 0:a:0        Extract only audio stream (a) , no video (0) and no text (0)
        # -f mp3            Format mp3
        # -                 output, hyphen means to pipe output to STDOUT, otherwise a filename
        p = await asyncio.create_subprocess_shell(
            f'ffmpeg -hide_banner -loglevel panic -y -f concat -i {ts_path / "tslist.txt"} -c copy -map 0:a:0 -f mp3 -',
            stdout=asyncio.subprocess.PIPE
        )
        # Return bytes
        return await p.stdout.read()
    finally:
        # Cleanup
        shutil.rmtree(ts_path)