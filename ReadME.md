## Python script to Get VMs and Disk Information from a GCP Project

- Date: June 7, 2023
- Author: Janarthanan kugathasan

### Introduction

Managing virtual machines (VMs) and disks in a cloud environment is crucial for effective infrastructure management. In this blog post, we will explore a Python script that retrieves VM and disk information from a Google Cloud Platform (GCP) project. This script utilizes the Google Cloud Python SDK to interact with the GCP APIs and collect relevant data.

### Script Overview

The script consists of several functions and utilizes the Google Cloud Python SDK to interact with GCP services. Let’s take a closer look at the key components of the script:

#### Importing Required Libraries
The script begins by importing the necessary libraries, including the Google Cloud SDK, datetime, csv, argparse, and collections.

#### Authentication
The script assumes the authentication details are already configured using environment variables. Ensure that you have set the GOOGLE_APPLICATION_CREDENTIALS environment variable with the path to your service account key file.

#### Retrieving Disk Logging Information
The get_disk_logging() function collects logging information related to disks in the GCP project. This is used to collect the creator information of the disk.

Retrieving VM Logging Information
The get_vm_logging() function collects logging information related to VM instances in the GCP project. This is used to collect the creator information of the VM.

Listing All VM Instances
The list_all_instances() function utilizes the Google Cloud Compute Engine API to list all VM instances in the project. It returns a dictionary containing the instances grouped by zone. It retrieves disk creation time, size, type, zone, attached VMs and description using the Google Cloud Logging API.

Listing All Disks
The list_all_disks() function utilizes the Google Cloud Compute Engine API to list all disks in the project. It returns a dictionary containing the disks grouped by zone. It retrieves VM creation time, machine type, zone, attached disks, and description using the Google Cloud Logging API.

Main Function
The main() function serves as the entry point of the script. It calls the necessary functions to collect VM and disk information, processes the data, and writes it to CSV files. The function also uploads the generated CSV files to a specified GCP bucket.

Uploading Files to GCP Bucket
The upload_cs_file() function handles the file upload process to a specified GCP bucket using the Google Cloud Storage API.

Usage
To use the script, follow these steps:

Ensure you have the necessary authentication details set up by setting the GOOGLE_APPLICATION_CREDENTIALS environment variable with the path to your service account key file.
Install the required dependencies by running pip install requirements.txt.
Run the script with the following command: python script_name.py project_name bucket_name, where project_name is the name of your GCP project and bucket_name is the name of the GCP bucket where you want to upload the generated CSV files.
Output
The script generates two CSV files: one containing VM information (vm_info_<timestamp>.csv) and the other containing disk information (disk_info_<timestamp>.csv). Each CSV file includes relevant details such as VM or disk name, size, type, creation timestamp, attached resources, and creator information.

Conclusion
In this blog post, we explored a Python script that utilizes the Google Cloud Python SDK to retrieve VM and disk information from a GCP project. By leveraging this script, you can automate the collection of crucial infrastructure details, enabling better management and analysis of your cloud environment. Feel free to modify the script to suit your specific requirements and enhance your cloud infrastructure management capabilities.
