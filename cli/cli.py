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
    
    questions = [
        inquirer.List(
            'option',
            message="Choose an action",
            choices=['Get Container Images', 
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