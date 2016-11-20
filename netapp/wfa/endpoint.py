import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET


def configure(user, password, endpoint='https://localhost/', ssl_verify=None):
    """initial configuration of WFA endpoint and authentication """
    Service.configure(user=user, password=password, endpoint=endpoint, ssl_verify=ssl_verify)


class Service:
    _endpoint = 'https://localhost/'
    _user = None
    _password = None
    _ssl_verify = True

    """constructor for WFA connection, endpoint, credentials"""
    @classmethod
    def configure(cls, user, password, endpoint, ssl_verify):
        cls._endpoint = endpoint
        cls._user = user
        cls._password = password

        if ssl_verify is not None:
            cls._ssl_verify = ssl_verify
        return

    def __init__(self):
        pass

    def _get_auth(self):
        """create authentication credentials for REST endpoint"""
        return HTTPBasicAuth(self._user, self._password)

class Endpoint(Service):
    def __init__(self, uri):
        super().__init__()
        self._uri = uri
        self._headers = dict()
        self._headers['user-agent'] = 'wfa-client/0.0.1'
        self._headers['Accept'] = 'application/xml'

        pass

    @property
    def url(self):
        return self._endpoint + self._uri


    def _process_response(self, response):
        """do initial xml processing of response body, at this point we are assuming it is parseable xml"""

        #print("raw response: =========================================================")
        #print(response.content)
        #print("=======================================================================")

        root = ET.fromstring(response.content)
        from netapp.wfa.types import Serializer
        ser = Serializer()
        return ser.to_object(root)

    def _build_xml_payload(self, data):
        """create an XML payload that is sent to server"""
        str_data = ET.tostring(data.to_payload(), encoding="unicode", short_empty_elements=True)
        return str_data

    def _request_url(self, verb, url, data=None, params=None):
        if url is None:
            url = self.url

        body = None
        if data is not None:
            body = self._build_xml_payload(data)

        print("request: %s to %s" %(verb, url))
        res = requests.request(verb, url, data=body, auth=self._get_auth(), headers=self._headers, params=params, verify=self._ssl_verify, )
        # raise an esception if you can, i.e. if bad status code
        res.raise_for_status()
        # should already do some xml processing at this stage

        return self._process_response(res)


    def http_get(self, url=None, params=None):
        res = self._request_url('GET', url=url, params=params)
        return res


    def http_post(self, data, url=None, params=None):
        res = self._request_url('POST', url=url, data=data, params=params)
        return res

    def http_delete(self, data, url=None, params=None):
        res = self._request_url('DELETE', url=url, data=data, params=params)
        return res

    def http_put(self, data, url=None, params=None):
        res = self._request_url('PUT', url=url, data=data, params=params)
        return res