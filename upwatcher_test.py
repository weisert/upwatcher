
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


def test_parse_commit_info_gerrit():
    test_string = '''
commit 08268de146718a0d96c0eaf79adf0dd3999ecf28
Author: Dale Curtis <dalecurtis@chromium.org>
Date:   Thu Nov 2 03:18:18 2017 +0000

    IVFParser is only used by unit tests.
    
    So don't build it for all platforms and non-test targets.
    
    BUG=778369
    TEST=none
    
    Cq-Include-Trybots: master.tryserver.chromium.android:android_optional_gpu_tests_rel;master.tryserver.chromium.linux:linux_optional_gpu_tests_rel;master.tryserver.chromium.mac:mac_optional_gpu_tests_rel;master.tryserver.chromium.win:win_optional_gpu_tests_rel
    Change-Id: I106f2a909b27028fbc88a2fdf9dd850f97d5eb73
    Reviewed-on: https://chromium-review.googlesource.com/738638
    Commit-Queue: Dale Curtis <dalecurtis@chromium.org>
    Reviewed-by: Miguel Casas <mcasas@chromium.org>
    Cr-Commit-Position: refs/heads/master@{#513391}

media/BUILD.gn
media/base/BUILD.gn
media/filters/BUILD.gn
media/filters/ivf_parser.h
    '''
    result = uw.parse_commit_info(test_string)
    assert result['commit_message'] == test_string
    assert 'commit' in result
    assert result['commit'] == '08268de146718a0d96c0eaf79adf0dd3999ecf28'
    assert 'author' in result
    assert result['author'] == 'Dale Curtis <dalecurtis@chromium.org>'
    assert 'date' in result
    assert result['date'] == 'Thu Nov 2 03:18:18 2017 +0000'
    assert 'head' in result
    assert result['head'] == 'IVFParser is only used by unit tests.'
    assert 'url' in result
    assert result['url'] == 'https://chromium-review.googlesource.com/738638'
