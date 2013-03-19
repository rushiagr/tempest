# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack, LLC
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

import json
import time
import urllib

from tempest.common.rest_client import RestClient
from tempest import exceptions


class SharesClientJSON(RestClient):
    """
    Client class to send CRUD Share API requests to a Cinder endpoint
    """

    def __init__(self, config, username, password, auth_url, tenant_name=None):
        super(SharesClientJSON, self).__init__(config, username, password,
                                                auth_url, tenant_name)

        self.service = self.config.share.catalog_type
        self.build_interval = self.config.share.build_interval
        self.build_timeout = self.config.share.build_timeout

    def list_shares(self, params=None):
        """List all the shares created."""
        url = 'shares'
        if params:
                url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = json.loads(body)
        return resp, body['shares']

    def list_shares_with_detail(self, params=None):
        """List the details of all shares."""
        url = 'shares/detail'
        if params:
                url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = json.loads(body)
        return resp, body['shares']

    def get_share(self, share_id):
        """Returns the details of a single share."""
        url = "shares/%s" % str(share_id)
        resp, body = self.get(url)
        body = json.loads(body)
        return resp, body['share']

    def create_share(self, size, proto, **kwargs):
        """
        Creates a new Share.
        size(Required): Size of share in GB.
        protocol(Required): Protocol for share (CIFS or NFS).
        Following optional keyword arguments are accepted:
        display_name: Optional share Name.
        metadata: A dictionary of values to be used as metadata.
        share_type: Optional Name of share_type for the share
        snapshot_id: When specified the share is created from this snapshot
        """
        post_body = {'size': size}
        post_body['proto'] = proto
        post_body.update(kwargs)
        post_body = json.dumps({'share': post_body})
        resp, body = self.post('shares', post_body, self.headers)
        body = json.loads(body)
        return resp, body['share']

    def delete_share(self, share_id):
        """Deletes the Specified Share."""
        return self.delete("shares/%s" % str(share_id))

    def attach_share(self, share_id, instance_uuid, mountpoint):
        """Attaches a share to a given instance on a given mountpoint."""
        post_body = {
            'instance_uuid': instance_uuid,
            'mountpoint': mountpoint,
        }
        post_body = json.dumps({'os-attach': post_body})
        url = 'shares/%s/action' % (share_id)
        resp, body = self.post(url, post_body, self.headers)
        return resp, body

    def detach_share(self, share_id):
        """Detaches a share from an instance."""
        post_body = {}
        post_body = json.dumps({'os-detach': post_body})
        url = 'shares/%s/action' % (share_id)
        resp, body = self.post(url, post_body, self.headers)
        return resp, body

    def wait_for_share_status(self, share_id, status):
        """Waits for a Share to reach a given status."""
        resp, body = self.get_share(share_id)
        share_name = body['display_name']
        share_status = body['status']
        start = int(time.time())

        while share_status != status:
            time.sleep(self.build_interval)
            resp, body = self.get_share(share_id)
            share_status = body['status']
            if share_status == 'error':
                raise exceptions.ShareBuildErrorException(share_id=share_id)

            if int(time.time()) - start >= self.build_timeout:
                message = ('Share %s failed to reach %s status within '
                           'the required time (%s s).' %
                           (share_name, status, self.build_timeout))
                raise exceptions.TimeoutException(message)

    def is_resource_deleted(self, id):
        try:
            self.get_share(id)
        except exceptions.NotFound:
            return True
        return False
