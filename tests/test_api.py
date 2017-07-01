import bitstamp_simple.api as api

def test_empty_authentication():
    assert not api.HttpApi().has_authentication_parameters()

def test_http_request():
    url = 'https://httpbin.org/post'
    data = 'foobar'
    response = api.HttpApi._http_request(url, data).decode('utf8')
    assert data in response
