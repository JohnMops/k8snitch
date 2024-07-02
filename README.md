# k8snitch

k8snitch is an interactive CLI tool designed to fetch information from your Kubernetes cluster on the fly.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/k8snitch.git
   cd k8snitch
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python3 k8snitch.py
   ```

   Alternatively, create an alias for easier access.

## Functionality

### Get Container Images

- **Select this action**: Choose to fetch container image information.
- **Select the namespace**: Specify the namespace in the Kubernetes cluster.
- **Output format**: Displays information in a formatted table.
- **Outputs**:
  - Deployment/Statefulset name
  - Images running in each deployment/statefulset
  - Last update time of the resource

### Get Resource Requests Information

- **Select this action**: Choose to fetch resources requests information.
- **Select the namespace**: Specify the namespace in the Kubernetes cluster.
- **Output format**: Displays information in a formatted table.
- **Outputs**:
  - Deployment/Statefulset name
  - Resource Type 
  - CPU
  - Memory

### Get Replica Count

- **Select this action**: Choose to fetch resources requests information.
- **Select the namespace**: Specify the namespace in the Kubernetes cluster.
- **Output format**: Displays information in a formatted table.
- **Outputs**:
  - Workload type: statefulset/deployment
  - Name of the workload
  - Namespace
  - Replica caount for the workload

More functionalities to be added in future updates.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests for new features, improvements, or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions or support, contact the project maintainer at evgenibir@outlook.com.

---

This README.md provides an overview of k8snitch, including setup instructions, current functionality (specifically for fetching container images from Kubernetes), information on contributing, licensing details, and contact information. Adjust the details (such as email and repository URL) based on your actual repository and preferences.