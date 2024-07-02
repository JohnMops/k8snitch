from kubernetes import client, config
import pandas as pd
from tabulate import tabulate

config.load_kube_config()

def show_active_context() -> str:
    """
    Retrieves the current kubeconfig context

    Returns:
        str: Returns the kubeconfig context
    """
    contexts, active_context = config.list_kube_config_contexts()
    current_context = active_context['name']
    
    return current_context

def get_deployments(namespace: str) -> list:
    """
    Fetches the list of deployments for a specific namespace

    Args:
        namespace (str): Namespace name to fetch deployments from

    Returns:
        list: List of deployments witht he full JASON
    """
    v1 = client.AppsV1Api()
    
    deployment_list = v1.list_namespaced_deployment(namespace=namespace)
    
    return deployment_list

def get_statefulsets(namespace: str) -> list:
    """
    Fetches the list of statefulsets for a specific namespace

    Args:
        namespace (str): Namespace name to fetch statefulsets from

    Returns:
        list: List of statefulsets witht he full JASON
    """
    v1 = client.AppsV1Api()
    
    sts_list: list = v1.list_namespaced_stateful_set(namespace=namespace)
    
    return sts_list

def get_resources_requests(namespace: str) -> None:
    deployment_list: list = get_deployments(namespace=namespace)
    sts_list: list = get_statefulsets(namespace=namespace)
    
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
    
            

def get_images_info(namespace: str) -> None:
    """
    Takes in a chosen namespace, gets all the images
    running in all containers in all deployments and 
    stateful sets and builds a table with the information

    Args:
        namespace (str): Chosen namespace to analyze
    """
    
    v1 = client.AppsV1Api()
    
    deployment_list: list = get_deployments(namespace=namespace)
            
    data: dict = {
                "Service": [],
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

        data["Service"].append(deployment_name)
        data["Image Used"].append(deployment_container_image)
        data["Last Update Time"].append(last_update_time)
    
    sts_list: list = get_statefulsets(namespace=namespace)
    
    for sts in sts_list.items:
        sts_name: str = sts.metadata.name
        sts_container_images: str = ", \n".join([container.image for container in sts.spec.template.spec.containers])
        last_update_time: str = "N/A"
        
        if sts.status.conditions:
            for condition in sts.status.conditions:
                if condition.type == "Progressing" and condition.status == "True":
                    last_update_time = condition.last_update_time
                    break
                
        data["Service"].append(sts_name)
        data["Image Used"].append(sts_container_images)
        data["Last Update Time"].append(last_update_time)
    
    df = pd.DataFrame(data)
    
    df.index = df.index + 1

    print(tabulate(df, headers='keys', tablefmt='grid'))
    
    print("\n")

def list_namespaces() -> list:
    """
    Gets the list of namespaces in
    the cluster

    Returns:
        list: Returns the list of namespaces in the cluster
    """
    
    v1 = client.CoreV1Api()
    namespace_list: list = []
    
    namespaces: dict = v1.list_namespace()
    for i in range(len(namespaces.items)):
        namespace_list.append(namespaces.items[i].metadata.name)
    return namespace_list

def get_replicas_count(namespace: str) -> None:
    """
    Gets replica count for all deployments and 
    statefulsets in a namespace and displays them
    in a table

    Args:
        namespace (str): Chosen namespace by the user
    """
    v1 = client.AppsV1Api()
    
    deployment_list: list = get_deployments(namespace=namespace)
    sts_list: list = get_statefulsets(namespace=namespace)
    
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