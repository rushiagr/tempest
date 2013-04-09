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

from tempest.common.utils.data_utils import rand_name
from tempest.test import attr
from tempest.tests.share import base


class SharesListTestCIFS(base.BaseShareTest):

    """
    This test creates a number of 1G shares. To run successfully,
    ensure that the backing file for the share group that Nova uses
    has space for at least 3 1G shares!
    If you are running a Devstack environment, ensure that the
    share_BACKING_FILE_SIZE is atleast 4G in your localrc
    """

    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(SharesListTestCIFS, cls).setUpClass()
        cls.client = cls.shares_client

        # Create 3 test shares
        cls.share_list = []
        cls.share_id_list = []
        for i in range(3):
            v_name = rand_name('share')
            metadata = {'Type': 'work'}
            try:
                resp, share = cls.client.create_share(size=1,proto='cifs',
                                                        display_name=v_name,
                                                        metadata=metadata)
                cls.client.wait_for_share_status(share['id'], 'available')
                resp, share = cls.client.get_share(share['id'])
                cls.share_list.append(share)
                cls.share_id_list.append(share['id'])
            except Exception:
                if cls.share_list:
                    # We could not create all the shares, though we were able
                    # to create *some* of the shares. This is typically
                    # because the backing file size of the share group is
                    # too small. So, here, we clean up whatever we did manage
                    # to create and raise a SkipTest
                    for volid in cls.share_id_list:
                        cls.client.delete_share(volid)
                        cls.client.wait_for_resource_deletion(volid)
                    msg = ("Failed to create ALL necessary shares to run "
                           "test. This typically means that the backing file "
                           "size of the nova-shares group is too small to "
                           "create the 3 shares needed by this test case")
                    raise cls.skipException(msg)
                raise

    @classmethod
    def tearDownClass(cls):
        # Delete the created shares
        for volid in cls.share_id_list:
            resp, _ = cls.client.delete_share(volid)
            cls.client.wait_for_resource_deletion(volid)
        super(SharesListTestCIFS, cls).tearDownClass()

    #TODO(rushiagr): write test_share_list (without details)
    @attr(type='smoke')
    def test_share_list_with_details(self):
        # Get a list of shares with details
        # Fetch all shares
        resp, fetched_list = self.client.list_shares_with_detail()
        self.assertEqual(200, resp.status)
        # Verify that all the shares are returned
        missing_vols = [v for v in self.share_list if v not in fetched_list]
        self.assertFalse(missing_vols,
                         "Failed to find share %s in fetched list" %
                         ', '.join(m_vol['display_name']
                                   for m_vol in missing_vols))


class ShareListTestCIFSXML(SharesListTestCIFS):
    _interface = 'xml'
