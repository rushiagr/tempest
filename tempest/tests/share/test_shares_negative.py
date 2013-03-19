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
from tempest import exceptions
from tempest.tests.share import base


class SharesNegativeTest(base.BaseShareTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(SharesNegativeTest, cls).setUpClass()
        cls.client = cls.shares_client

    def test_share_get_nonexistant_share_id(self):
        # Should not be able to get a nonexistant share
        #Creating a nonexistant share id
        share_id_list = []
        resp, shares = self.client.list_shares()
        for i in range(len(shares)):
            share_id_list.append(shares[i]['id'])
        while True:
            non_exist_id = rand_name('999')
            if non_exist_id not in share_id_list:
                break
        #Trying to Get a non existant share
        self.assertRaises(exceptions.NotFound, self.client.get_share,
                          non_exist_id)

    def test_share_delete_nonexistant_share_id(self):
        # Should not be able to delete a nonexistant Share
        # Creating nonexistant share id
        share_id_list = []
        resp, shares = self.client.list_shares()
        for i in range(len(shares)):
            share_id_list.append(shares[i]['id'])
        while True:
            non_exist_id = '12345678-abcd-4321-abcd-123456789098'
            if non_exist_id not in share_id_list:
                break
        # Try to Delete a non existant share
        self.assertRaises(exceptions.NotFound, self.client.delete_share,
                          non_exist_id)

    def test_create_share_with_invalid_size(self):
        # Should not be able to create share with invalid size
        # in request
        v_name = rand_name('Share-')
        metadata = {'Type': 'work'}
        self.assertRaises(exceptions.BadRequest, self.client.create_share,
                          size='#$%', display_name=v_name, metadata=metadata)

    def test_create_share_with_out_passing_size(self):
        # Should not be able to create share without passing size
        # in request
        v_name = rand_name('Share-')
        metadata = {'Type': 'work'}
        self.assertRaises(exceptions.BadRequest, self.client.create_share,
                          size='', display_name=v_name, metadata=metadata)

    def test_create_share_with_size_zero(self):
        # Should not be able to create share with size zero
        v_name = rand_name('Share-')
        metadata = {'Type': 'work'}
        self.assertRaises(exceptions.BadRequest, self.client.create_share,
                          size='0', display_name=v_name, metadata=metadata)

    def test_get_invalid_share_id(self):
        # Should not be able to get share with invalid id
        self.assertRaises(exceptions.NotFound, self.client.get_share,
                          '#$%%&^&^')

    def test_get_share_without_passing_share_id(self):
        # Should not be able to get share when empty ID is passed
        self.assertRaises(exceptions.NotFound, self.client.get_share, '')

    def test_delete_invalid_share_id(self):
        # Should not be able to delete share when invalid ID is passed
        self.assertRaises(exceptions.NotFound, self.client.delete_share,
                          '!@#$%^&*()')

    def test_delete_share_without_passing_share_id(self):
        # Should not be able to delete share when empty ID is passed
        self.assertRaises(exceptions.NotFound, self.client.delete_share, '')


class SharesNegativeTestXML(SharesNegativeTest):
    _interface = 'xml'
