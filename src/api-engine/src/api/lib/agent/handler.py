#
# SPDX-License-Identifier: Apache-2.0
#
import logging

from django.conf import settings

from api.lib.agent.docker import DockerAgent
from api.lib.agent.kubernetes import KubernetesAgent
from api.common.enums import HostType

LOG = logging.getLogger(__name__)
MEDIA_ROOT = getattr(settings, "MEDIA_ROOT")


class AgentHandler(object):
    def __init__(self, node=None):
        self._network_type = node.network_type
        self._network_version = node.network_version
        self._node_type = node.type
        self._agent_type = node.agent.type
        node_dict = node.__dict__
        node_dict.update(
            {
                "worker_api": node.agent.worker_api,
                "agent_id": str(node.agent.id),
                "compose_file": node.get_compose_file_path(),
            }
        )
        self._agent = DockerAgent(node_dict)
        self._worker_api = node.agent.worker_api
        self._node = node

        if self._agent_type == HostType.Kubernetes.name.lower():
            self._agent = KubernetesAgent(node_dict)

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value

    @property
    def compose_config(self):
        return (
            self._agent.generate_compose_yaml()
            if self._agent_type == HostType.Docker.name.lower()
            else None
        )

    def create_node(self):
        self._agent.create()

        return True

    def delete_node(self):
        self._agent.delete()

        return True
