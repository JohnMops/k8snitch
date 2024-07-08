import click
import inquirer
from k8s.functions import Kuber

    
# @cli.command()
def choose_option() -> None:
    """
    1. Checks for the active context and provides options
    2. Provides options for choosing what action to take
    """
    kuber: Kuber = Kuber()
    
    questions = [
        inquirer.List(
            'option',
            message="Choose an action",
            choices=['Get Deployment Logs',
                     'Get StatefulSet Logs',
                     'Get Pods Metrics',
                     'Get Container Images', 
                     'Get Resource Requests Information',
                     'Get Replica Count',
                     'Exit'
                     ],
        ),
    ]
    answers: dict = inquirer.prompt(questions)
    click.echo(f'You chose: {answers["option"]}')
    
    match answers["option"]:
        case "Exit":
            exit(0)
        case "Get StatefulSet Logs":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            sts_list: list = kuber.list_statefulsets(namespace=chosen_ns)
            if sts_list:
                sts_name: str = choose_statefulset(sts_list=sts_list)
                sts_label_selector: str = kuber.get_statefulset_labels(namespace=chosen_ns,
                                                                    sts_name=sts_name)
                kuber.read_logs(namespace=chosen_ns,
                                label_selector=sts_label_selector)
                choose_option()
            else:
                # print(f'No StatefulSets in {chosen_ns}\n')
                click.echo(click.style(f'No StatefulSets in {chosen_ns}\n', fg='red'))
                choose_option()
        case "Get Deployment Logs":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            deployment_list: list = kuber.list_deployments(namespace=chosen_ns)
            if deployment_list:
                deployment_name: str = choose_deployment(deployment_list=deployment_list)
                deployment_label_selector: str = kuber.get_deployment_labels(deployment_name=deployment_name,
                                                                            namespace=chosen_ns)
                kuber.read_logs(namespace=chosen_ns,
                                label_selector=deployment_label_selector)
                choose_option()
            else: 
                click.echo(click.style(f'No Deployments in {chosen_ns}\n', fg='red'))
                choose_option()
        case "Get Pods Metrics":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            kuber.get_pod_metrics(namespace=chosen_ns)
            choose_option()
        case "Get Container Images":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            kuber.get_images_info(namespace=chosen_ns)
            choose_option()
        case "Get Resource Requests Information":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            kuber.get_resources_requests(namespace=chosen_ns)
            choose_option()
        case "Get Replica Count":
            ns_list: list = kuber.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            kuber.get_replicas_count(namespace=chosen_ns)
            choose_option()

def choose_deployment(deployment_list: list) -> str:
    """
    Gets a list of deployments in the cluster
    and presents them as options

    Args:
        deployment_list (list): List of deployments in the cluster

    Returns:
        str: Returns the chosen deployment
    """
    
    questions = [
        inquirer.List(
            'option',
            message="Choose Deployment",
            choices=lambda answers: deployment_list,
        ),
    ]
    answers: dict = inquirer.prompt(questions)

    return answers["option"] 

def choose_statefulset(sts_list: list) -> str:
    """
    Gets a list of statefulsets in the cluster
    and presents them as options

    Args:
        sts_list (list): List of statefulsets in the cluster

    Returns:
        str: Returns the chosen statefulset
    """
    questions = [
        inquirer.List(
            'option',
            message="Choose StatefulSet",
            choices=lambda answers: sts_list,
        ),
    ]
    answers: dict = inquirer.prompt(questions)

    return answers["option"] 

# @cli.command()
def choose_namespace(ns_list: list) -> str:
    """
    Gets a list of namespaces in the cluster
    and presents them as options

    Args:
        ns_list (list): List of namespaces in the cluster

    Returns:
        str: Returns the chosen namespace
    """
    # ns_list = kuber.list_namespaces()
    # print(ns_list)
    questions = [
        inquirer.List(
            'option',
            message="Choose Namespace",
            choices=lambda answers: ns_list,
        ),
    ]
    answers: dict = inquirer.prompt(questions)
    # click.echo(f'You chose: {answers["option"]}')

    return answers["option"] 

def show_connected_cluster(kuber) -> None:
    print(f'You are connected to {kuber.show_active_context()}\n')    
    
    questions = [
        inquirer.List(
            'option',
            message="Is this the correct cluster? ",
            choices=['Yes', 
                     'No',
                     'Exit'
                     ],
        ),
    ]
    answers: dict = inquirer.prompt(questions)
    
    match answers["option"]:
        case "No":
            print("Please connect to the right cluster and try again")
            exit(0)
        case "Yes":
            pass
        case "Exit":
            exit(0)