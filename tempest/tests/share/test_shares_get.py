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


class SharesGetTest(base.BaseShareTest):

    _interface = "json"

    @classmethod
    def setUpClass(cls):
        super(SharesGetTest, cls).setUpClass()
        cls.client = cls.shares_client

    @attr(type='smoke')
    def test_share_create_get_delete(self):
        # Create a share, Get it's details and Delete the share
        try:
            share = {}
            v_name = rand_name('Share-')
            metadata = {'Type': 'work'}
            #Create a share
            resp, share = self.client.create_share(size=1,proto='nfs',
                                                     display_name=v_name,
                                                     metadata=metadata)
            self.assertEqual(200, resp.status)
            self.assertTrue('id' in share)
            self.assertTrue('display_name' in share)
            self.assertEqual(share['display_name'], v_name,
                             "The created share name is not equal "
                             "to the requested name")
            self.assertTrue(share['id'] is not None,
                            "Field share id is empty or not found.")
            self.client.wait_for_share_status(share['id'], 'available')
            # Get Share information
            resp, fetched_share = self.client.get_share(share['id'])
            self.assertEqual(200, resp.status)
            self.assertEqual(v_name,
                             fetched_share['display_name'],
                             'The fetched Share is different '
                             'from the created Share')
            self.assertEqual(share['id'],
                             fetched_share['id'],
                             'The fetched Share is different '
                             'from the created Share')
            self.assertEqual(metadata,
                             fetched_share['metadata'],
                             'The fetched Share is different '
                             'from the created Share')
        except Exception:
            self.fail("Could not create a share")
        finally:
            if share:
                # Delete the Share if it was created
                resp, _ = self.client.delete_share(share['id'])
                self.assertEqual(202, resp.status)
                self.client.wait_for_resource_deletion(share['id'])

    @attr(type='positive')
    def test_share_get_metadata_none(self):
        # Create a share without passing metadata, get details, and delete
        try:
            share = {}
            v_name = rand_name('Share-')
            # Create a share without metadata
            resp, share = self.client.create_share(size=1,proto='nfs',
                                                     display_name=v_name,
                                                     metadata={})
            self.assertEqual(200, resp.status)
            self.assertTrue('id' in share)
            self.assertTrue('display_name' in share)
            self.client.wait_for_share_status(share['id'], 'available')
            #GET Share
            resp, fetched_share = self.client.get_share(share['id'])
            self.assertEqual(200, resp.status)
            self.assertEqual(fetched_share['metadata'], {})
        except Exception:
            self.fail("Could not get share metadata")
        finally:
            if share:
                # Delete the Share if it was created
                resp, _ = self.client.delete_share(share['id'])
                self.assertEqual(202, resp.status)
                self.client.wait_for_resource_deletion(share['id'])


class SharesGetTestXML(SharesGetTest):
    _interface = "xml"
