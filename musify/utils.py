from functools import partial
import aiologger, sys
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.formatters.json import Formatter
from aiologger import Logger
from aiologger.levels import LogLevel

handler = AsyncStreamHandler(
    stream=sys.stderr,
    level=LogLevel.DEBUG if sys.argv[-1] == 'debug' else LogLevel.INFO,
    formatter=Formatter(
        fmt='%(asctime)s  %(levelname)-8s %(name)-8s: %(message)s',
        datefmt='%d/%m/%y %H:%M:%S'
    )
)
getLogger = partial(aiologger.Logger)