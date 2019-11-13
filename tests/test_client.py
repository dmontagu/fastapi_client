# -*- coding: utf-8 -*-
"""
Regression tests
"""
from asyncio import get_event_loop
import hashlib

from generated_client.api_client import ApiClient, SyncApis
import generated_client.models as models

class Client(SyncApis):
    """
    Context manager for apis - closes the client on exit.
    """
    def __init__(self):
        super().__init__(ApiClient(host='http://localhost:8000', timeout=3600))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        get_event_loop().run_until_complete(self.client._async_client.close())


def test_any():
    """
    Test apis with no response schema. Should succeed and leave the returned data alone
    """
    with Client() as client:
        result = client.client_api.no_schema()
        assert isinstance(result, dict)
        assert result['hello'] == 'world'


def _get_file_info():
    """ Return length and hash string from a file """
    with open(__file__, 'rb') as file:
        data = file.read()
        length = len(data)
        hash_text = hashlib.sha256(data).hexdigest()

    return length, hash_text



def test_file_post():
    """
    Test files posted as multipart/form.
    TODO: Optional[bytes] = File(...) doesn't yet work, test when it does.
    """
    length, hash_text = _get_file_info()

    with Client() as client:
        with open(__file__, 'rb') as file:
            ret = client.client_api.file_upload(file=file)
            assert isinstance(ret, models.FormPostResponse)
            assert ret.length == length
            assert ret.hash == hash_text
            assert ret.token is None
            assert ret.content_type.startswith('multipart/form-data')

        with open(__file__, 'rb') as file:
            ret = client.client_api.file_upload(file=file, token="asdf")
            assert ret.length == length
            assert ret.hash == hash_text
            assert ret.token == "asdf"
            assert ret.content_type.startswith('multipart/form-data')


def test_form_post():
    """
    Test ordinary forms with no files are sent as application/x-www-form-urlencoded
    """
    with Client() as client:
        ret = client.client_api.form_upload(token="asdf")
        assert isinstance(ret, models.FormPostResponse)
        assert ret.length == 0
        assert ret.hash is None
        assert ret.token == "asdf"
        assert ret.content_type.startswith('application/x-www-form-urlencoded')


def test_list_query():
    """
    Check lists in queries are properly expanded in the constructed URL..
    """
    tags = ['2', '1', '3']
    with Client() as client:
        ret = client.client_api.tags_list(tags=tags)
        assert ret.tags == tags
