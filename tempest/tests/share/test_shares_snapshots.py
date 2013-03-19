# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from tempest.tests.share import base


class SharesSnapshotTest(base.BaseShareTest):
    _interface = "json"

    def test_share_from_snapshot(self):
        share_origin = self.create_share(size=1)
        snapshot = self.create_snapshot(share_origin['id'])
        share_snap = self.create_share(size=1,
                                         snapshot_id=
                                         snapshot['id'])
        self.snapshots_client.delete_snapshot(snapshot['id'])
        self.shares_client.delete_share(share_snap['id'])
        self.snapshots_client.wait_for_resource_deletion(snapshot['id'])
        self.snapshots.remove(snapshot)
        self.shares_client.delete_share(share_origin['id'])
        self.shares_client.wait_for_resource_deletion(share_snap['id'])
        self.shares.remove(share_snap)
        self.shares_client.wait_for_resource_deletion(share_origin['id'])
        self.shares.remove(share_origin)


class SharesSnapshotTestXML(SharesSnapshotTest):
    _interface = "xml"
