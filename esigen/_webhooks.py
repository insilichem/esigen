#!/usr/bin/env python

"""
Based on https://docs.figshare.com/#upload_files_example_upload_on_figshare
"""

import hashlib
import json
import os

import requests
from requests.exceptions import HTTPError
VERIFY = 'IN_PRODUCTION' in os.environ

class WebHook(object):

    AUTH_URL = 'REPLACE_THIS'
    BASE_URL = 'REPLACE_THIS/{endpoint}'
    _HEADER_AUTH_KEYWORD = 'token'
    _DEFAULT_HEADERS = {}
    AUTH_METHOD = 'headers'

    def __init__(self, token):
        self.token = token

    def raw_issue_request(self, method, url, data=None, binary=False, headers=None, params=None, **kwargs):
        if headers is None:
            headers = self._DEFAULT_HEADERS.copy()
        if params is None:
            params = {}
        if self.AUTH_METHOD == 'headers':
            headers['Authorization'] = '{} {}'.format(self._HEADER_AUTH_KEYWORD, self.token)
        elif self.AUTH_METHOD == 'params':
            params['access_token'] = self.token

        if data is not None and not binary:
            data = json.dumps(data)
        response = requests.request(method, url, headers=headers, data=data, params=params,
                                    verify=VERIFY, **kwargs)
        try:
            response.raise_for_status()
            try:
                data = json.loads(response.content)
            except ValueError:
                data = response.content
        except HTTPError as error:
            print('Caught an HTTPError: {}'.format(error))
            print('Body:\n', response.content)
            raise

        return data

    def issue_request(self, method, endpoint, *args, **kwargs):
        return self.raw_issue_request(method, self.BASE_URL.format(endpoint=endpoint), *args, **kwargs)


class Figshare(WebHook):

    AUTH_URL = 'https://figshare.com/account/applications/authorize'
    TOKEN_URL = 'https://api.figshare.com/v2/token'
    BASE_URL = 'https://api.figshare.com/v2/{endpoint}'
    CHUNK_SIZE = 1048576

    def list_articles(self, ):
        result = self.issue_request('GET', 'account/articles')
        print('Listing current articles:')
        if result:
            for item in result:
                print( u'  {url} - {title}'.format(**item))
        else:
            print('  No articles.')

    def create_article(self, title, description=''):
        data = {'title': title, 'description': description}
        result = self.issue_request('POST', 'account/articles', data=data)
        url = result['location']
        result = self.raw_issue_request('GET', url)
        return result.get('id'), result.get('url_private_html')

    def list_files_of_article(self, article_id):
        result = self.issue_request('GET', 'account/articles/{}/files'.format(article_id))
        print('Listing files for article {}:'.format(article_id))
        if result:
            for item in result:
                print('  {id} - {name}'.format(**item))
        else:
            print('  No files.')

    def get_file_check_data(self, file_name):
        with open(file_name, 'rb') as fin:
            md5 = hashlib.md5()
            size = 0
            data = fin.read(self.CHUNK_SIZE)
            while data:
                size += len(data)
                md5.update(data)
                data = fin.read(self.CHUNK_SIZE)
            return md5.hexdigest(), size

    def initiate_new_upload(self, article_id, file_name):
        endpoint = 'account/articles/{}/files'
        endpoint = endpoint.format(article_id)

        md5, size = self.get_file_check_data(file_name)
        data = {'name': os.path.basename(file_name),
                'md5': md5,
                'size': size}

        result = self.issue_request('POST', endpoint, data=data)
        print('Initiated file upload:', result['location'], '\n')

        result = self.raw_issue_request('GET', result['location'])

        return result

    def complete_upload(self, article_id, file_id):
        self.issue_request('POST', 'account/articles/{}/files/{}'.format(article_id, file_id))

    def upload_parts(self, file_info, file_path):
        url = '{upload_url}'.format(**file_info)
        result = self.raw_issue_request('GET', url)

        print('Uploading parts:')
        with open(file_path, 'rb') as fin:
            for part in result['parts']:
                self.upload_part(file_info, fin, part)

    def upload_part(self, file_info, stream, part):
        udata = file_info.copy()
        udata.update(part)
        url = '{upload_url}/{partNo}'.format(**udata)

        stream.seek(part['startOffset'])
        data = stream.read(part['endOffset'] - part['startOffset'] + 1)

        self.raw_issue_request('PUT', url, data=data, binary=True)
        print('  Uploaded part {partNo} from {startOffset} to {endOffset}'.format(**part))

    def upload_files(self, article_id, *filenames):
        results = []
        for filename in filenames:
            # Then we upload the file.
            file_info = self.initiate_new_upload(article_id, filename)
            # Until here we used the figshare API; following lines use the figshare upload service API.
            self.upload_parts(file_info, filename)
            # We return to the figshare API to complete the file upload process.
            r = self.complete_upload(article_id, file_info['id'])
            results.append(r)
        return results


class Zenodo(WebHook):

    AUTH_URL = r'https://zenodo.org/oauth/authorize'
    TOKEN_URL = r'https://zenodo.org/oauth/token'
    BASE_URL = r'https://zenodo.org/api/{endpoint}'
    _HEADER_AUTH_KEYWORD = 'Bearer'
    _DEFAULT_HEADERS = {"Content-Type": "application/json"}
    AUTH_METHOD = 'params'

    def create_article(self, title, description='Created with ESIgen'):
        data = {'metadata': {'title': title, 'upload_type': 'dataset', 'description': description}}
        result = self.issue_request('POST', 'deposit/depositions', data=data)
        return result.get('id'), result.get('links', {}).get('html')

    def upload_files(self, article_id, *filenames):
        for filename in filenames:
            data = {'filename': os.path.basename(filename)}
            files = {'file': open(filename, 'rb')}
            print('Uploading file', filename)
            r = self.issue_request('POST', 'deposit/depositions/{}/files'.format(article_id),
                                   data=data, files=files, headers={}, binary=True)
