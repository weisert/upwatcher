
import upwatcher as uw


def test_parse_commit_info():
    test_string = '''
commit 936cea331ab3b57e81c3a18b9e350300ae283eb7
Author: servolk <servolk@chromium.org>
Date:   Tue Jan 31 20:59:55 2017 -0800

    Recognize legacy avc1 codec ids in StringToVideoCodec

    Currently StringToVideoCodec function doesn't support legacy avc1 codec
    ids (like avc1.66.30 or avc1.77.31). This causes some Chromecast
    internal tests to fail (see the associated bug).
    So move TranslateLegacyAvc1CodecIds to video_codecs.* and use it in
    StringToVideoCodec to try and parse legacy avc1 codec ids.

    BUG=internal b/34631886

    Review-Url: https://codereview.chromium.org/2659133003 .
    Cr-Commit-Position: refs/heads/master@{#447451}

    '''
    result = uw.parse_commit_info(test_string)
    assert result['commit_message'] == test_string
    assert 'commit' in result
    assert result['commit'] == '936cea331ab3b57e81c3a18b9e350300ae283eb7'
    assert 'author' in result
    assert result['author'] == 'servolk <servolk@chromium.org>'
    assert 'date' in result
    assert result['date'] == 'Tue Jan 31 20:59:55 2017 -0800'
    assert 'head' in result
    assert result['head'] == 'Recognize legacy avc1 codec ids in ' \
                          'StringToVideoCodec'
    assert 'url' in result
    assert result['url'] == 'https://codereview.chromium.org/2659133003'
