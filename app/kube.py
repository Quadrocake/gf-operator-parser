from kubernetes import client, config
import json 
import os

class Kube_api():
    def __init__(self):
        if os.environ["DEVELOPMENT"] == "True":
            config.load_kube_config()
        else:
            config.load_incluster_config()
        self.api = client.CoreV1Api()

    def list_custom_objects_all(self):
        ret = client.CustomObjectsApi().list_cluster_custom_object(
            group="integreatly.org", 
            version="v1alpha1", 
            plural="grafanadashboards"
        )
        return(ret)

    def list_custom_object_namespaced(self):
        ret = client.CustomObjectsApi().list_namespaced_custom_object(
            group="integreatly.org", 
            version="v1alpha1", 
            namespace="infra",
            plural="grafanadashboards"
        )
        return(ret)
