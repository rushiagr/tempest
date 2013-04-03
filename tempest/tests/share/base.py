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

import logging
import time

from tempest import clients
from tempest.common.utils.data_utils import rand_name
from tempest import exceptions
import tempest.test

LOG = logging.getLogger(__name__)


class BaseShareTest(tempest.test.BaseTestCase):

    """Base test case class for all Cinder API tests."""

    @classmethod
    def setUpClass(cls):
        cls.isolated_creds = []

        if cls.config.compute.allow_tenant_isolation:
            creds = cls._get_isolated_creds()
            username, tenant_name, password = creds
            os = clients.Manager(username=username,
                                 password=password,
                                 tenant_name=tenant_name,
                                 interface=cls._interface)
        else:
            os = clients.Manager(interface=cls._interface)
        cls.os = os
        cls.shares_client = os.shares_client
        cls.snapshots_client = os.shares_snapshots_client
        cls.servers_client = os.servers_client
        cls.image_ref = cls.config.compute.image_ref
        cls.flavor_ref = cls.config.compute.flavor_ref
        cls.build_interval = cls.config.share.build_interval
        cls.build_timeout = cls.config.share.build_timeout
        cls.snapshots = []
        cls.shares = []

        skip_msg = (("%s skipped as Cinder endpoint is not available"+'|'+"volume" '''cls.shares_client.service''') %
                    cls.__name__)
        try:
            
            cls.shares_client.keystone_auth(cls.os.username,
                                             cls.os.password,
                                             cls.os.auth_url,
                                             'volume',#cls.shares_client.service,
                                             cls.os.tenant_name)
        except exceptions.EndpointNotFound:
            cls.clear_isolated_creds()
            raise cls.skipException(skip_msg)

    @classmethod
    def _get_identity_admin_client(cls):
        """
        Returns an instance of the Identity Admin API client
        """
        os = clients.ComputeAdminManager()
        return os.identity_client

    @classmethod
    def _get_isolated_creds(cls):
        """
        Creates a new set of user/tenant/password credentials for a
        **regular** user of the share API so that a test case can
        operate in an isolated tenant container.
        """
        admin_client = cls._get_identity_admin_client()
        rand_name_root = rand_name(cls.__name__)
        if cls.isolated_creds:
            # Main user already created. Create the alt one...
            rand_name_root += '-alt'
        username = rand_name_root + "-user"
        email = rand_name_root + "@example.com"
        tenant_name = rand_name_root + "-tenant"
        tenant_desc = tenant_name + "-desc"
        password = "pass"

        resp, tenant = admin_client.create_tenant(name=tenant_name,
                                                  description=tenant_desc)
        resp, user = admin_client.create_user(username,
                                              password,
                                              tenant['id'],
                                              email)
        # Store the complete creds (including UUID ids...) for later
        # but return just the username, tenant_name, password tuple
        # that the various clients will use.
        cls.isolated_creds.append((user, tenant))

        return username, tenant_name, password

    @classmethod
    def clear_isolated_creds(cls):
        if not cls.isolated_creds:
            return
        admin_client = cls._get_identity_admin_client()

        for user, tenant in cls.isolated_creds:
            admin_client.delete_user(user['id'])
            admin_client.delete_tenant(tenant['id'])

    @classmethod
    def tearDownClass(cls):
        cls.clear_snapshots()
        cls.clear_shares()
        cls.clear_isolated_creds()

    @classmethod
    def create_snapshot(cls, share_id=1, **kwargs):
        """Wrapper utility that returns a test snapshot."""
        resp, snapshot = cls.snapshots_client.create_snapshot(share_id,
                                                              **kwargs)
        assert 202 == resp.status
        cls.snapshots_client.wait_for_snapshot_status(snapshot['id'],
                                                      'available')
        cls.snapshots.append(snapshot)
        return snapshot

    #NOTE(afazekas): these create_* and clean_* could be defined
    # only in a single location in the source, and could be more general.

    @classmethod
    def create_share(cls, size=1, **kwargs):
        """Wrapper utility that returns a test share."""
        resp, share = cls.shares_client.create_share(size, **kwargs)
        assert 200 == resp.status
        cls.shares_client.wait_for_share_status(share['id'], 'available')
        cls.shares.append(share)
        return share

    @classmethod
    def clear_shares(cls):
        for share in cls.shares:
            try:
                cls.share_client.delete_share(share['id'])
            except Exception:
                pass

        for share in cls.shares:
            try:
                cls.servers_client.wait_for_resource_deletion(share['id'])
            except Exception:
                pass

    @classmethod
    def clear_snapshots(cls):
        for snapshot in cls.snapshots:
            try:
                cls.snapshots_client.delete_snapshot(snapshot['id'])
            except Exception:
                pass

        for snapshot in cls.snapshots:
            try:
                cls.snapshots_client.wait_for_resource_deletion(snapshot['id'])
            except Exception:
                pass

    def wait_for(self, condition):
        """Repeatedly calls condition() until a timeout."""
        start_time = int(time.time())
        while True:
            try:
                condition()
            except Exception:
                pass
            else:
                return
            if int(time.time()) - start_time >= self.build_timeout:
                condition()
                return
            time.sleep(self.build_interval)


class BaseShareAdminTest(BaseShareTest):
    """Base test case class for all share Admin API tests."""
    @classmethod
    def setUpClass(cls):
        super(BaseShareAdminTest, cls).setUpClass()
        cls.adm_user = cls.config.identity.admin_username
        cls.adm_pass = cls.config.identity.admin_password
        cls.adm_tenant = cls.config.identity.admin_tenant_name
        if not all((cls.adm_user, cls.adm_pass, cls.adm_tenant)):
            msg = ("Missing share Admin API credentials "
                   "in configuration.")
            raise cls.skipException(msg)

        cls.os_adm = clients.AdminManager(interface=cls._interface)
        cls.client = cls.os_adm.share_types_client
