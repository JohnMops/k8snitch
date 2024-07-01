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

def get_images_info(namespace: str) -> None:
    """
    Takes in a chosen namespace, gets all the images
    running in all containers in all deployments and 
    stateful sets and builds a table with the information

    Args:
        namespace (str): Chosen namespace to analyze
    """
    
    v1 = client.AppsV1Api()
    
    deployment_list = v1.list_namespaced_deployment(namespace=namespace)
            
    data: dict = {
                "Service": [],
                "Image Used": [],
                "Last Update Time": []
            }

    for deployment in deployment_list.items:
        deployment_name: str = deployment.metadata.name
        deployment_container_image: str = deployment.spec.template.spec.containers[0].image
        last_update_time: str = "N/A"
        
        if deployment.status.conditions:
            for condition in deployment.status.conditions:
                if condition.type == "Progressing" and condition.status == "True":
                    last_update_time = condition.last_update_time
                    break

        data["Service"].append(deployment_name)
        data["Image Used"].append(deployment_container_image)
        data["Last Update Time"].append(last_update_time)
    
    sts_list: list = v1.list_namespaced_stateful_set(namespace=namespace)
    
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

