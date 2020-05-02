import html

class Index():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class AlAudioObject():
    '''Represents vk's alaudio object. It is constructed from audio_data acquired in load_section'''

    _index = Index(**{
        'AUDIO_ITEM_CAN_ADD_BIT': 2,
        'AUDIO_ITEM_CLAIMED_BIT': 4,
        'AUDIO_ITEM_EXPLICIT_BIT': 1024,
        'AUDIO_ITEM_HAS_LYRICS_BIT': 1,
        'AUDIO_ITEM_HQ_BIT': 16,
        'AUDIO_ITEM_INDEX_ADS': 15,
        'AUDIO_ITEM_INDEX_ALBUM': 19,
        'AUDIO_ITEM_INDEX_ALBUM_ID': 6,
        'AUDIO_ITEM_INDEX_AUTHOR_LINK': 8,
        'AUDIO_ITEM_INDEX_CONTEXT': 11,
        'AUDIO_ITEM_INDEX_COVER_URL': 14,
        'AUDIO_ITEM_INDEX_DURATION': 5,
        'AUDIO_ITEM_INDEX_EXTRA': 12,
        'AUDIO_ITEM_INDEX_FEAT_ARTISTS': 18,
        'AUDIO_ITEM_INDEX_FLAGS': 10,
        'AUDIO_ITEM_INDEX_HASHES': 13,
        'AUDIO_ITEM_INDEX_ID': 0,
        'AUDIO_ITEM_INDEX_LYRICS': 9,
        'AUDIO_ITEM_INDEX_MAIN_ARTISTS': 17,
        'AUDIO_ITEM_INDEX_OWNER_ID': 1,
        'AUDIO_ITEM_INDEX_PERFORMER': 4,
        'AUDIO_ITEM_INDEX_SUBTITLE': 16,
        'AUDIO_ITEM_INDEX_TITLE': 3,
        'AUDIO_ITEM_INDEX_TRACK_CODE': 20,
        'AUDIO_ITEM_INDEX_URL': 2,
        'AUDIO_ITEM_LONG_PERFORMER_BIT': 32,
        'AUDIO_ITEM_REPLACEABLE': 512,
        'AUDIO_ITEM_UMA_BIT': 128,
    })

    def __init__(self, data):
        self._construct_object(data)

    def _construct_object(self, data):
        _hashes = data[self._index.AUDIO_ITEM_INDEX_HASHES].split('/')
        _covers = data[self._index.AUDIO_ITEM_INDEX_COVER_URL].split(',')

        _dict = {
            'aid': int(data[self._index.AUDIO_ITEM_INDEX_ID]),
            'owner_id': int(data[self._index.AUDIO_ITEM_INDEX_OWNER_ID]),
            'ownerId': data[self._index.AUDIO_ITEM_INDEX_OWNER_ID],
            'fullId': '{}_{}'.format(data[self._index.AUDIO_ITEM_INDEX_OWNER_ID], data[self._index.AUDIO_ITEM_INDEX_ID]),
            'title': data[self._index.AUDIO_ITEM_INDEX_TITLE],
            'subTitle': data[self._index.AUDIO_ITEM_INDEX_SUBTITLE],
            'performer': data[self._index.AUDIO_ITEM_INDEX_PERFORMER],
            'duration': int(data[self._index.AUDIO_ITEM_INDEX_DURATION]),
            'lyrics': int(data[self._index.AUDIO_ITEM_INDEX_LYRICS]),
            'url': data[self._index.AUDIO_ITEM_INDEX_URL],
            'flags': data[self._index.AUDIO_ITEM_INDEX_FLAGS],
            'context': data[self._index.AUDIO_ITEM_INDEX_CONTEXT],
            'extra': data[self._index.AUDIO_ITEM_INDEX_EXTRA],
            'addHash': _hashes[0] if _hashes[0] else "",
            'editHash': _hashes[1] if _hashes[1] else "",
            'actionHash': _hashes[2] if _hashes[2] else "",
            'deleteHash': _hashes[3] if _hashes[3] else "",
            'replaceHash': _hashes[4] if _hashes[4] else "",
            'urlHash': _hashes[5] if _hashes[5] else "",
            'canEdit': not(not(_hashes[1])),
            'canDelete': not(not(_hashes[3])),
            'isLongPerformer': data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_LONG_PERFORMER_BIT,
            'canAdd': not(not(data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_CAN_ADD_BIT)),
            'coverUrl_s': _covers[0],
            'coverUrl_p': _covers[1] if len(_covers) > 1 else '',
            'isClaimed': not(not(data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_CLAIMED_BIT)),
            'isExplicit': not(not(data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_EXPLICIT_BIT)),
            'isUMA': not(not(data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_UMA_BIT)),
            'isReplaceable': not(not(data[self._index.AUDIO_ITEM_INDEX_FLAGS] & self._index.AUDIO_ITEM_REPLACEABLE)),
            'ads': data[self._index.AUDIO_ITEM_INDEX_ADS],
            'album': data[self._index.AUDIO_ITEM_INDEX_ALBUM],
            'albumId': int(data[self._index.AUDIO_ITEM_INDEX_ALBUM_ID]),
            'trackCode': data[self._index.AUDIO_ITEM_INDEX_TRACK_CODE]
        }
        _dict['artist'] = _dict['performer']
        for key, value in _dict.items():
            if type(value) is str:
                _dict[key] = html.unescape(html.unescape(value))
            
        for key, value in _dict.items():
            setattr(self, key, value)