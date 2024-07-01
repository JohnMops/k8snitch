import click
import inquirer
from k8s import functions as k8s

    
# @cli.command()
def choose_option() -> None:
    """
    1. Checks for the active context and provides options
    2. Provides options for choosing what action to take
    """
    print(f'You are connected to {k8s.show_active_context()}')    
    
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
            ns_list: list = k8s.list_namespaces()
            chosen_ns: str = choose_namespace(ns_list=ns_list)
            k8s.get_images_info(namespace=chosen_ns)
            choose_option()
        case "Wednesday":
            print("It's Wednesday!")



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
    # ns_list = k8s.list_namespaces()
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