from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from kubernetes.client.exceptions import ApiException
import pandas as pd
from tabulate import tabulate
from helpers import helpers

class Kuber():
    def __init__(self) -> None:
        self._appsv1api = client.AppsV1Api()
        self._corev1api = client.CoreV1Api()
        self._customobjectsapi = client.CustomObjectsApi()

    def load_kube_config() -> None:
        try:
            config.load_kube_config()
        except ConfigException as e:
            print(e)
            exit(1)

    def show_active_context(self) -> str:
        """
        Retrieves the current kubeconfig context

        Returns:
            str: Returns the kubeconfig context
        """
        contexts, active_context = config.list_kube_config_contexts()
        current_context = active_context['name']
        
        return current_context
    
    def get_deployment_labels(self, deployment_name: str, namespace: str) -> str:
        deployment: dict = self._appsv1api.read_namespaced_deployment(name=deployment_name, 
                                                                      namespace=namespace)
        labels: dict = deployment.spec.selector.match_labels
        label_selector: str = ",".join([f"{key}={value}" for key, value in labels.items()])
        
        return label_selector
    
    def get_statefulset_labels(self, sts_name: str, namespace: str) -> str:        
        sts: dict = self._appsv1api.read_namespaced_stateful_set(name=sts_name, 
                                                                 namespace=namespace)
        labels: dict = sts.spec.selector.match_labels
        label_selector: str = ",".join([f"{key}={value}" for key, value in labels.items()])
        
        return label_selector
    
    def read_logs(self, namespace: str, label_selector: str) -> None:
        v1 = self._corev1api

        pods = v1.list_namespaced_pod(namespace, label_selector=label_selector)
        
        for pod in pods.items:
            pod_name: str = pod.metadata.name
            containers: dict = pod.spec.containers
            
            for container in containers:
                if container.name.startswith('istio'):
                    break
                else:
                    try:
                        print('-' * 20 + f" Logs for pod {pod_name}: " + '-' * 20 + '\n')
                        logs = v1.read_namespaced_pod_log(name=pod_name, 
                                                        namespace=namespace, 
                                                        container=container.name)
                        print(logs)
                    except ApiException as e:
                        print(e)
            
    def get_pod_metrics(self, namespace: str) -> None:
        """
        Fetches metrics for each pod in a namespaces 
        from the metric server and returns a table with
        the values

        Args:
            namespace (str): Namespace to analyze
        """
        try:

            api_instance = self._customobjectsapi

            data: list = []
            headers: list = ["Pod", "CPU(Cores)", "Memory(Bytes)"]
            
            group = 'metrics.k8s.io'
            version = 'v1beta1'
            namespace = namespace
            plural = 'pods'

            pod_metrics = api_instance.list_namespaced_custom_object(group, version, namespace, plural)

            # Print pod metrics
            for pod in pod_metrics['items']:
                pod_name = pod['metadata']['name']
                total_cpu_cores = 0
                total_memory_mb = 0

                for container in pod['containers']:
                    cpu_usage = container['usage']['cpu']
                    memory_usage = container['usage']['memory']

                    total_cpu_cores += helpers.convert_cpu_to_cores(cpu_usage)
                    total_memory_mb += helpers.convert_memory_to_mb(memory_usage)
            
                data.append([
                    pod_name,
                    f'{total_cpu_cores:.2f}C',
                    f'{total_memory_mb:.0f}Mi'
                ])
            
            df = pd.DataFrame(data, columns=headers)
        
            df.index = df.index + 1

            print(tabulate(df, headers='keys', tablefmt='grid'))
            
            print("\n")

        except ApiException as e:
            print(f"Exception when calling CustomObjectsApi->list_namespaced_custom_object: {e}")


    def get_deployments(self, namespace: str) -> list:
        """
        Fetches the list of deployments for a specific namespace

        Args:
            namespace (str): Namespace name to fetch deployments from

        Returns:
            list: List of deployments witht he full JASON
        """
        v1 = self._appsv1api
        
        deployment_list = v1.list_namespaced_deployment(namespace=namespace)
        
        return deployment_list

    def get_statefulsets(self, namespace: str) -> list:
        """
        Fetches the list of statefulsets for a specific namespace

        Args:
            namespace (str): Namespace name to fetch statefulsets from

        Returns:
            list: List of statefulsets witht he full JASON
        """
        v1 = self._appsv1api
        
        sts_list: list = v1.list_namespaced_stateful_set(namespace=namespace)
        
        return sts_list

    def get_resources_requests(self, namespace: str) -> None:
        deployment_list: list = self.get_deployments(namespace=namespace)
        sts_list: list = self.get_statefulsets(namespace=namespace)
        
        data = []
        headers = ["Container Name", "Resource Type", "CPU", "Memory"]
        
        for deployment in deployment_list.items:
            deployment_name: str = deployment.metadata.name
            for container in deployment.spec.template.spec.containers:
                resources: dict = container.resources
                requests = resources.requests or {}
                limits = resources.limits or {}

                # Prepare row data for requests and limits
                data.append([
                    container.name,
                    "Requests",
                    requests.get("cpu", "None"),
                    requests.get("memory", "None"),
                ])
                data.append([
                    container.name,
                    "Limits",
                    limits.get("cpu", "None"),
                    limits.get("memory", "None"),
                ])
        
        for sts in sts_list.items:
            sts_name: str = sts.metadata.name
            for container in sts.spec.template.spec.containers:
                for container in sts.spec.template.spec.containers:
                    resources: dict = container.resources
                    requests = resources.requests or {}
                    limits = resources.limits or {}

                    # Prepare row data for requests and limits
                    data.append([
                        container.name,
                        "Requests",
                        requests.get("cpu", "None"),
                        requests.get("memory", "None"),
                    ])
                    data.append([
                        container.name,
                        "Limits",
                        limits.get("cpu", "None"),
                        limits.get("memory", "None"),
                    ])
            
        df = pd.DataFrame(data, columns=headers)
        
        df.index = df.index + 1

        print(tabulate(df, headers='keys', tablefmt='grid'))
        
        print("\n")
        
                

    def get_images_info(self, namespace: str) -> None:
        """
        Takes in a chosen namespace, gets all the images
        running in all containers in all deployments and 
        stateful sets and builds a table with the information

        Args:
            namespace (str): Chosen namespace to analyze
        """
        
        v1 = self._appsv1api
        
        deployment_list: list = self.get_deployments(namespace=namespace)
                
        data: dict = {
                    "Type": [],
                    "Name": [],
                    "Image Used": [],
                    "Last Update Time": []
                }

        for deployment in deployment_list.items:
            deployment_name: str = deployment.metadata.name
            deployment_container_image: str = ", \n".join([container.image for container in deployment.spec.template.spec.containers])
            last_update_time: str = "N/A"
            
            if deployment.status.conditions:
                for condition in deployment.status.conditions:
                    if condition.type == "Progressing" and condition.status == "True":
                        last_update_time = condition.last_update_time
                        break
            
            data["Type"].append('Deployment')
            data["Name"].append(deployment_name)
            data["Image Used"].append(deployment_container_image)
            data["Last Update Time"].append(last_update_time)
        
        sts_list: list = self.get_statefulsets(namespace=namespace)
        
        for sts in sts_list.items:
            sts_name: str = sts.metadata.name
            sts_container_images: str = ", \n".join([container.image for container in sts.spec.template.spec.containers])
            last_update_time: str = "N/A"
            
            if sts.status.conditions:
                for condition in sts.status.conditions:
                    if condition.type == "Progressing" and condition.status == "True":
                        last_update_time = condition.last_update_time
                        break
            
            data["Type"].append('StatefulSet')
            data["Name"].append(sts_name)
            data["Image Used"].append(sts_container_images)
            data["Last Update Time"].append(last_update_time)
        
        df = pd.DataFrame(data)
        
        df.index = df.index + 1

        print(tabulate(df, headers='keys', tablefmt='grid'))
        
        print("\n")

    def list_deployments(self, namespace: str) -> list:
        """
        Fetches the list of deployments for a specific namespace

        Args:
            namespace (str): Namespace name to fetch deployments from

        Returns:
            list: List of deployments names
        """
        v1 = self._appsv1api
        deployment_list: list = []
        
        deployments = v1.list_namespaced_deployment(namespace=namespace)
        for deployment in deployments.items:
            deployment_name: str = deployment.metadata.name
            deployment_list.append(deployment_name)
        
        return deployment_list
    
    def list_statefulsets(self, namespace: str) -> list:
        """
        Fetches the list of statefulsets for a specific namespace

        Args:
            namespace (str): Namespace name to fetch statefulsets from

        Returns:
            list: List of statefulsets names
        """
        v1 = self._appsv1api
        sts_list: list = []
        
        statefulsets = v1.list_namespaced_stateful_set(namespace=namespace)
        for sts in statefulsets.items:
            sts_name: str = sts.metadata.name
            sts_list.append(sts_name)
        
        return sts_list
    
    def list_namespaces(self) -> list:
        """
        Gets the list of namespaces in
        the cluster

        Returns:
            list: Returns the list of namespaces in the cluster
        """
        
        v1 = self._corev1api
        namespace_list: list = []
        
        try:
            namespaces: dict = v1.list_namespace()
        except ApiException as e:
            print(f'Your request failed with code: {e.status}')
            print(f'Reason for failure: {e.reason}')
            exit(1)
            
        for i in range(len(namespaces.items)):
            namespace_list.append(namespaces.items[i].metadata.name)
        return namespace_list

    def get_replicas_count(self, namespace: str) -> None:
        """
        Gets replica count for all deployments and 
        statefulsets in a namespace and displays them
        in a table

        Args:
            namespace (str): Chosen namespace by the user
        """
        v1 = self._appsv1api
        
        deployment_list: list = self.get_deployments(namespace=namespace)
        sts_list: list = self.get_statefulsets(namespace=namespace)
        
        data = []
        
        headers = ["Type", "Name", "Namespace", "Replicas Set", "Replicas Ready"]

        for deployment in deployment_list.items:
                data.append([
                    "Deployment",
                    deployment.metadata.name,
                    deployment.metadata.namespace,
                    deployment.spec.replicas,
                    deployment.status.ready_replicas
                ])

        for statefulset in sts_list.items:
            data.append([
                "StatefulSet",
                statefulset.metadata.name,
                statefulset.metadata.namespace,
                statefulset.spec.replicas,
                statefulset.status.ready_replicas
            ])

        df = pd.DataFrame(data, columns=headers)
        
        df.index = df.index + 1

        print(tabulate(df, headers=headers, tablefmt="grid"))
        print("\n")