# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_k8sclient
----------------------------------

Tests for `k8sclient` module. Deploy Kubernetes using:
http://kubernetes.io/docs/getting-started-guides/docker/

and then run this test
"""

from testtools.testcase import unittest
import urllib3
import uuid

from k8sclient.client import api_client
from k8sclient.client.apis import apiv_api
from k8sclient.client.apis import apisextensionsvbeta_api
from k8sclient.client.apis import apisbatchv_api
from k8sclient.tests import base


def _is_k8s_running():
    try:
        urllib3.PoolManager().request('GET', '127.0.0.1:8080')
        return True
    except urllib3.exceptions.HTTPError:
        return False


class TestK8sclient(base.TestCase):
    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_list_endpoints(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        endpoints = api.list_endpoints()
        self.assertTrue(len(endpoints.items) > 0)

    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_pod_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        name = 'test-' + str(uuid.uuid4())

        pod_manifest = {'apiVersion': 'v1',
                        'kind': 'Pod',
                        'metadata': {'color': 'blue', 'name': name},
                        'spec': {'containers': [{'image': 'dockerfile/redis',
                                                 'name': 'redis'}]}}

        resp = api.create_namespaced_pod(body=pod_manifest,
                                         namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status.phase)

        resp = api.read_namespaced_pod(name=name,
                                       namespace='default')
        self.assertEqual(name, resp.metadata.name)
        self.assertTrue(resp.status.phase)

        number_of_pods = len(api.list_pod().items)
        self.assertTrue(number_of_pods > 0)

        resp = api.delete_namespaced_pod(name=name, body={},
                                         namespace='default')

    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_service_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        service_manifest = {'apiVersion': 'v1',
                            'kind': 'Service',
                            'metadata': {'labels': {'name': 'frontend'},
                                         'name': 'frontend',
                                         'resourceversion': 'v1'},
                            'spec': {'ports': [{'name': 'port',
                                                'port': 80,
                                                'protocol': 'TCP',
                                                'targetPort': 80}],
                                     'selector': {'name': 'frontend'}}}

        resp = api.create_namespaced_service(body=service_manifest,
                                             namespace='default')
        self.assertEqual('frontend', resp.metadata.name)
        self.assertTrue(resp.status)

        resp = api.read_namespaced_service(name='frontend',
                                           namespace='default')
        self.assertEqual('frontend', resp.metadata.name)
        self.assertTrue(resp.status)

        service_manifest['spec']['ports'] = [{'name': 'new',
                                              'port': 8080,
                                              'protocol': 'TCP',
                                              'targetPort': 8080}]
        resp = api.patch_namespaced_service(body=service_manifest,
                                            name='frontend',
                                            namespace='default')
        self.assertEqual(2, len(resp.spec.ports))
        self.assertTrue(resp.status)

        resp = api.delete_namespaced_service(name='frontend',
                                             namespace='default')

    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_replication_controller_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        rc_manifest = {
            'apiVersion': 'v1',
            'kind': 'ReplicationController',
            'metadata': {'labels': {'name': 'frontend'},
                         'name': 'frontend'},
            'spec': {'replicas': 2,
                     'selector': {'name': 'frontend'},
                     'template': {'metadata': {
                         'labels': {'name': 'frontend'}},
                         'spec': {'containers': [{
                             'image': 'nginx',
                             'name': 'nginx',
                             'ports': [{'containerPort': 80,
                                        'protocol': 'TCP'}]}]}}}}

        resp = api.create_namespaced_replication_controller(
            body=rc_manifest, namespace='default')
        self.assertEqual('frontend', resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        resp = api.read_namespaced_replication_controller(
            name='frontend', namespace='default')
        self.assertEqual('frontend', resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        resp = api.delete_namespaced_replication_controller(
            name='frontend', body={}, namespace='default')


    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_configmap_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        test_configmap = {
            "kind": "ConfigMap",
            "apiVersion": "v1",
            "metadata": {
                "name": "test-configmap",
            },
            "data": {
                "config.json": "{\"command\":\"/usr/bin/mysqld_safe\"}",
                "frontend.cnf": "[mysqld]\nbind-address = 10.0.0.3\nport = 3306\n"
            }
        }

        resp = api.create_namespaced_config_map(
            body=test_configmap, namespace='default'
        )
        self.assertEqual('test-configmap', resp.metadata.name)

        resp = api.read_namespaced_config_map(
            name='test-configmap', namespace='default')
        self.assertEqual('test-configmap', resp.metadata.name)

        test_configmap['data']['config.json'] = "{}"
        resp = api.patch_namespaced_config_map(
            name='test-configmap', namespace='default', body=test_configmap)

        resp = api.delete_namespaced_config_map(
            name='test-configmap', body={}, namespace='default')


    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_node_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apiv_api.ApivApi(client)

        for item in api.list_namespaced_node().items:
            node = api.read_namespaced_node(name=item.metadata.name)
            self.assertTrue(len(node.metadata.labels) > 0)
            self.assertIsInstance(node.metadata.labels, dict)


class TestK8sclientBeta(base.TestCase):
    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_deployment_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apisextensionsvbeta_api.ApisextensionsvbetaApi(client)

        deployment_manifest = {
            'kind': 'Deployment',
            'spec': {
                'template':
                    {'spec':
                        {'containers': [
                            {'image': 'nginx',
                             'name': 'test-deployment',
                             'ports': [{'containerPort': 80}]
                             }
                        ]},
                        'metadata': {'labels': {'app': 'test-deployment'}}},
                'replicas': 2},
            'apiVersion': 'extensions/v1beta1',
            'metadata': {'name': 'test-deployment'}}

        resp = api.create_namespaced_deployment(
            body=deployment_manifest, namespace='default')
        self.assertEqual('test-deployment', resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        resp = api.read_namespaced_deployment(
            name='test-deployment', namespace='default')
        self.assertEqual('test-deployment', resp.metadata.name)
        self.assertEqual(2, resp.spec.replicas)

        deployment_manifest['spec']['replicas'] = 1
        resp = api.patch_namespaced_deployment(
            name='test-deployment', namespace='default',
            body=deployment_manifest)
        self.assertEqual(1, resp.spec.replicas)

        resp = api.delete_namespaced_deployment(
            name='test-deployment', body={}, namespace='default')


class TestK8sclientBatch(base.TestCase):
    @unittest.skipUnless(
        _is_k8s_running(), "Kubernetes is not available")
    def test_job_apis(self):
        client = api_client.ApiClient('http://127.0.0.1:8080/')
        api = apisbatchv_api.ApisbatchvApi(client)

        job_manifest = {
            'kind': 'Job',
            'spec': {
                'template':
                    {'spec':
                        {'containers': [
                            {'image': 'busybox',
                             'name': 'test-job',
                             'command': ["sh", "-c", "sleep 5"]
                             }],
                         'restartPolicy': 'Never'},
                        'metadata': {'name': 'test-job'}}},
            'apiVersion': 'batch/v1',
            'metadata': {'name': 'test-job'}}

        resp = api.create_namespaced_job(
            body=job_manifest, namespace='default')
        self.assertEqual('test-job', resp.metadata.name)

        resp = api.read_namespaced_job(
            name='test-job', namespace='default')
        self.assertEqual('test-job', resp.metadata.name)

        resp = api.delete_namespaced_job(
            name='test-job', body={}, namespace='default')
