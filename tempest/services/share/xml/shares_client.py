# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2012 IBM
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

import time
import urllib

from lxml import etree

from tempest.common.rest_client import RestClientXML
from tempest import exceptions
from tempest.services.compute.xml.common import Document
from tempest.services.compute.xml.common import Element
from tempest.services.compute.xml.common import Text
from tempest.services.compute.xml.common import xml_to_json
from tempest.services.compute.xml.common import XMLNS_11


class SharesClientXML(RestClientXML):
    """
    Client class to send CRUD share API requests to a Cinder endpoint
    """

    def __init__(self, config, username, password, auth_url, tenant_name=None):
        super(SharesClientXML, self).__init__(config, username, password,
                                               auth_url, tenant_name)
        self.service = 'volume'
        self.build_interval = self.config.compute.build_interval
        self.build_timeout = self.config.compute.build_timeout

    def _parse_share(self, body):
        vol = dict((attr, body.get(attr)) for attr in body.keys())

        for child in body.getchildren():
            tag = child.tag
            if tag.startswith("{"):
                ns, tag = tag.split("}", 1)
            if tag == 'metadata':
                vol['metadata'] = dict((meta.get('key'),
                                       meta.text) for meta in
                                       child.getchildren())
            else:
                vol[tag] = xml_to_json(child)
        return vol

    def list_shares_with_detail(self, params=None):
        """List all the details of shares."""
        url = 'shares/detail'

        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url, self.headers)
        body = etree.fromstring(body)
        shares = []
        if body is not None:
            shares += [self._parse_share(vol) for vol in list(body)]
        return resp, shares

    def get_share(self, share_id):
        """Returns the details of a single share."""
        url = "shares/%s" % str(share_id)
        resp, body = self.get(url, self.headers)
        body = etree.fromstring(body)
        return resp, self._parse_share(body)

    def create_share(self, size, proto, **kwargs):
        """Creates a new share.

        :param size: Size of share in GB. (Required)
        :param display_name: Optional share Name.
        :param metadata: An optional dictionary of values for metadata.
        :param share_type: Optional Name of share_type for the share
        :param snapshot_id: When specified the share is created from
                            this snapshot
        """
        #NOTE(afazekas): it should use a share namespace
        share = Element("share", xmlns=XMLNS_11, size=size, proto=proto, share_type=proto, display_name=(kwargs.get('display_name', 'share1')))

        if 'metadata' in kwargs:
            _metadata = Element('metadata')
            share.append(_metadata)
            for key, value in kwargs['metadata'].items():
                meta = Element('meta')
                meta.add_attr('key', key)
                meta.append(Text(value))
                _metadata.append(meta)
            attr_to_add = kwargs.copy()
            del attr_to_add['metadata']
        else:
            attr_to_add = kwargs

        for key, value in attr_to_add.items():
            share.add_attr(key, value)

        resp, body = self.post('shares', str(Document(share)),
                               self.headers)
        body = xml_to_json(etree.fromstring(body))
        return resp, body

    def delete_share(self, share_id):
        """Deletes the Specified share."""
        return self.delete("shares/%s" % str(share_id))

    def wait_for_share_status(self, share_id, status):
        """Waits for a share to reach a given status."""
        resp, body = self.get_share(share_id)
        share_status = body['status']
        start = int(time.time())

        while share_status != status:
            time.sleep(self.build_interval)
            resp, body = self.get_share(share_id)
            share_status = body['status']
            if share_status == 'error':
                raise exceptions.shareBuildErrorException(share_id=share_id)

            if int(time.time()) - start >= self.build_timeout:
                message = 'share %s failed to reach %s status within '\
                          'the required time (%s s).' % (share_id,
                                                         status,
                                                         self.build_timeout)
                raise exceptions.TimeoutException(message)

    def is_resource_deleted(self, id):
        try:
            self.get_share(id)
        except exceptions.NotFound:
            return True
        return False
