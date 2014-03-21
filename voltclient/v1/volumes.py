# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import json

import six
from six.moves.urllib import parse

from voltclient.common import base
from voltclient.common import exception

ISCSI_PARAMS = ('host', 'port', 'iqn', 'lun')

PEER_PARAMS = tuple('peer_id')

PARAMS = ISCSI_PARAMS + PEER_PARAMS


class Volume(base.Resource):
    def __repr__(self):
        return "<Volume %s>" % self._info

    def update(self, **fields):
        self.manager.update(self, **fields)

    def delete(self):
        return self.manager.delete(self)

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class VolumeManager(base.Manager):
    resource_class = Volume

    def list(self, **kwargs):
        """Get a list of volumes.

        :param volume_id:
        :rtype: list of :class:`Volume`
        """
        volume_id = kwargs.pop('volume_id', None)

        url = '/v1/volumes'
        if volume_id:
            url += '/%s' % parse.quote(str(volume_id))
            _, body_iter = self.api.raw_request('HEAD', url)
            body = ''.join([c for c in body_iter])
            volumes = map(lambda x: Volume(self, x), eval(body))

        else:
            _, body_iter = self.api.raw_request('GET', url)
            body = ''.join([c for c in body_iter])
            volumes = map(lambda x: Volume(self, x), eval(body))

        return volumes

    def get(self, **kwargs):
        """Get the metadata for a specific image.

        :param image: image object or id to look up
        :rtype: :class:`Image`
        """
        volume_id = kwargs.pop('volume_id', None)

        fields = {}
        for field in kwargs:
            if field in PARAMS:
                fields[field] = str(kwargs[field])
            else:
                msg = 'get() got an unexpected keyword argument \'%s\''
                raise TypeError(msg % field)


        _, body_iter = self.api.raw_request('GET', '/v1/volumes/%s'
                                          % parse.quote(str(volume_id)),
                                          body=fields)
        body = ''.join([c for c in body_iter])
        return map(lambda x: Volume(self, x), eval(body))

    def logout(self, **kwargs):
        """Delete the metadata of a volume in volt."""
        peer_id = kwargs.pop('peer_id', None)
        volume_id = kwargs.pop('volume_id', None)
        url = '/v1/volumes'
        if peer_id:
            fields = {'peer_id': peer_id}
        else:
            fields = {}
        if volume_id:
            url += '/%s' % volume_id

        _, body = self.api.raw_request('DELETE', url, body=fields)

    def login(self, **kwargs):
        """Register a volume to Volt.

        TODO(zpfalpc23@gmail.com): document accepted params
        """
        volume_id = kwargs.pop('volume_id', None)

        fields = {}
        for field in kwargs:
            if field in PARAMS:
                fields[field] = str(kwargs[field])
            else:
                msg = 'register() got an unexpected keyword argument \'%s\''
                raise TypeError(msg % field)

        resp, body_iter = self.api.raw_request(
            'POST', '/v1/volumes/%s' % volume_id, body=fields)
        body = eval(''.join([c for c in body_iter]))
        return Volume(self, body)