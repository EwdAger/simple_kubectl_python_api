# coding=utf-8
"""
Created on 2020/6/2 16:05

@author: EwdAger
"""
import os
from typing import Any

from kubernetes import client, config
import yaml

from app.config.common import BASE_DIR


class K8sClient:
    def __init__(self):
        self.apps_path = os.path.join(BASE_DIR, 'resource', 'k8s_apps')
        self.client = self._kubernetes_init()

    @staticmethod
    def _kubernetes_init():
        config.kube_config.load_kube_config(config_file=os.path.join(BASE_DIR, 'app', 'config', 'kubeconfig.yaml'))
        return client

    def dict_to_yaml(self, yaml_name: str, deploy_dict: dict):
        """
        字典转yaml并存入resource文件夹
        :param yaml_name:
        :param deploy_dict:
        :return:
        """

        yaml_path = os.path.join(self.apps_path, yaml_name)
        with open(yaml_path, 'w') as f:
            yaml.dump(deploy_dict, f)

        return yaml_path

    def create_namespace(self, namespace: str) -> str:
        """
        创建命名空间
        :param namespace:
        :return:
        """
        res = self.client.CoreV1Api().create_namespace(
            body=self.client.V1Namespace(metadata=self.client.V1ObjectMeta(name=namespace)))

        return res.metadata.name

    def delete_namespace(self, namespace: str) -> str:
        """
        删除 命名空间
        :param namespace:
        :return: str Terminal
        """

        res = self.client.CoreV1Api().delete_namespace(namespace)

        return res.status

    def create_deployment_by_dict(self, namespace: str, body_dict: dict) -> str:
        """
        使用dict 创建 工作负载
        :param namespace:
        :param body_dict:
        :return:
        """
        resp = self.client.AppsV1Api().create_namespaced_deployment(
            namespace=namespace, body=body_dict, pretty=True
        )

        return resp.metadata.name

    def create_deployment_by_yaml(self, namespace: str, yaml_path: str) -> str:
        """
        使用yaml 创建 工作负载
        :param namespace:
        :param yaml_path:
        :return:
        """
        with open(yaml_path, 'r') as f:
            deploy_body = yaml.safe_load(f)
            res = self.create_deployment_by_dict(namespace, deploy_body)
        return res

    def delete_deployment(self, name: str, namespace: str) -> str:
        """
        删除 工作负载
        :param name:
        :param namespace:
        :return:
        """
        res = self.client.AppsV1Api().delete_namespaced_deployment(name=name, namespace=namespace, pretty=True)

        return res.status

    def read_deployment(self, name: str, namespace: str) -> Any:
        """
        查看 工作负载详情 TODO 未实现输出重要信息，目前输出整个对象
        :param name:
        :param namespace:
        :return:
        """
        res = self.client.AppsV1Api().read_namespaced_deployment(name=name, namespace=namespace, pretty=True)

        return res

    def read_deployment_pods_num(self, name: str, namespace: str) -> int:
        """
        查看 工作负载启动的相同pods数
        :param name:
        :param namespace:
        :return:
        """
        deploy_obj = self.read_deployment(name, namespace)
        nums = deploy_obj.spec.replicas
        return nums

    def edit_deployment_pods_num(self, name: str, namespace: str, nums: int) -> Any:
        """
        更改 工作负载启动的相同pods数
        :param name:
        :param namespace:
        :param nums:
        :return:
        """
        deploy_obj = self.read_deployment(name, namespace)
        deploy_obj.spec.replicas = nums
        res = self.client.AppsV1Api().patch_namespaced_deployment(name, namespace, deploy_obj, pretty=True)

        return res

    def edit_deployment_by_dict(self, name: str, namespace: str, body_dict: dict) -> Any:
        """
        使用dict 升级 工作负载
        :param name:
        :param namespace:
        :param body_dict:
        :return:
        """
        res = self.client.AppsV1Api().patch_namespaced_deployment(name, namespace, body_dict, pretty=True)

        return res

    def edit_deployment_by_yaml(self, name: str, namespace: str, yaml_path: str) -> Any:
        """
        使用yaml 升级 工作负载
        :param name:
        :param namespace:
        :param yaml_path:
        :return:
        """
        with open(yaml_path, 'r') as f:
            deploy_body = yaml.safe_load(f)
            res = self.edit_deployment_by_dict(name, namespace, deploy_body)
        return res

    def stop_deployment_pods_all(self, name: str, namespace: str) -> Any:
        """
        停止 工作负载 ，本质为将pods数调整为 0
        :param name:
        :param namespace:
        :return:
        """
        res = self.edit_deployment_pods_num(name, namespace, 0)
        return res

    def read_namespace_all_pods_status(self, namespace: str) -> bool:
        """
        返回 工作负载 所有 pods 状态，如果有一个未在Running 状态将返回 False
        TODO 删除pods时，仍会返回True，因为判断条件不能简单的设为所有pods是否全为Running
        :param namespace:
        :return:
        """
        res = self.client.CoreV1Api().list_namespaced_pod(namespace)
        is_ready = True
        for i in res.items:
            print(i.metadata.name + " " + i.status.phase)
            if i.status.phase != "Running":
                is_ready = False
        return is_ready


if __name__ == "__main__":
    k8s_client = K8sClient()

