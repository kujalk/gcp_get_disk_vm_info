"""
Script to get all the VMs and Disk info from a GCP project
"""

from __future__ import annotations
import os
from datetime import datetime
import csv
from google.cloud import storage
import argparse
from google.cloud import logging
from google.cloud.logging import DESCENDING, Client,ASCENDING

from collections import defaultdict
from collections.abc import Iterable

from google.cloud import compute_v1

#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="E:\\tfkey.json"

def get_disk_logging(project):

    print("Collecting Disk Logging Information")
    # Get the current UTC time
    current_hour = datetime.utcnow()

    # Format the current UTC time as a string
    current_hour = current_hour.strftime("%Y-%m-%dT%H:%M:%SZ")
    earlier='2022-01-31T03:00:00Z'

    client = Client(project = project)

    filter1 = 'resource.type = gce_disk'
    filter2 = 'resource.type="gce_disk" protoPayload.methodName="v1.compute.disks.insert" AND timestamp>=' + '\"' + earlier + '\" AND timestamp<=' + '\"' + current_hour + '\"'

    whole_data=[]

    for filter_ in (filter1,filter2):
        for entry in client.list_entries(filter_=filter_,order_by=ASCENDING, page_size=1000):
            timestamp = entry.timestamp.isoformat()
            resource = entry.resource.labels
            payload = entry.payload
            whole_data.append(payload)

    return whole_data

def get_vm_logging(project):
    
    print("Collecting VM Logging Information")

    # Get the current UTC time
    current_hour = datetime.utcnow()

    # Format the current UTC time as a string
    current_hour = current_hour.strftime("%Y-%m-%dT%H:%M:%SZ")
    earlier='2022-01-31T03:00:00Z'
    
    client = Client(project = project)

    filter1 = 'resource.type = gce_instance protoPayload.methodName="beta.compute.instances.insert"'
    filter2 = 'resource.type="gce_instance" protoPayload.methodName="beta.compute.instances.insert" AND timestamp>=' + '\"' + earlier + '\" AND timestamp<=' + '\"' + current_hour + '\"'

    whole_data=[]

    for filter_ in (filter1,filter2):
        for entry in client.list_entries(filter_=filter_,order_by=ASCENDING, page_size=1000):
            timestamp = entry.timestamp.isoformat()
            resource = entry.resource.labels
            payload = entry.payload
            whole_data.append(payload)

    return whole_data


# define function that uploads a file from the bucket
def upload_cs_file(bucket_name, source_file_name, destination_file_name): 
    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)

        blob = bucket.blob(destination_file_name)
        blob.upload_from_filename(source_file_name)

        print(f"Upload of file {source_file_name} is successful")
    except Exception as e:
        print(f"Upload of file {source_file_name} failed - {e}")

def list_all_instances(project_id: str,) -> dict[str, Iterable[compute_v1.Instance]]:
    try:
        instance_client = compute_v1.InstancesClient()
        request = compute_v1.AggregatedListInstancesRequest()
        request.project = project_id
        request.max_results = 100

        agg_list = instance_client.aggregated_list(request=request)

        return agg_list
    except Exception as e:
        print(f"Error while getting all instances {e}")
        return None

def list_all_disks(project_id: str,) -> dict[str, Iterable[compute_v1.Instance]]:
    try:
        instance_client = compute_v1.DisksClient()
        request = compute_v1.AggregatedListDisksRequest()
        request.project = project_id
        request.max_results = 100

        agg_list = instance_client.aggregated_list(request=request)

        return agg_list
    except Exception as e:
        print(f"Error while getting all disks {e}")
        return None
        

def main(project_name,bucket_name):

    try:

        disk_logging = get_disk_logging(project_name)
        all_disks = list_all_disks(project_name)

        all_instances = defaultdict(list)
        all_list = []
        for zone, response in all_disks:
            if response.disks:
                all_instances[zone].extend(response.disks)
                
                for disk in response.disks:
                    type = disk.type.split("/")[-1]
                    if disk.users:
                        used=[]
                        for item in disk.users:
                            used.append(item.split("/")[-1])
                    else:
                        used ="not attached"
                        
                    print(f"Found Disk : {disk.name}")
                    
                    creator = "NA, if its attached disk, refer the VM details"

                    for item in disk_logging:
                        try:
                            if item["authorizationInfo"][0]["resourceAttributes"]["name"].split("/")[-1]==disk.name:
                                creator=(item["response"]["user"])
                                break
                        except:
                            pass

                    data = {
                        "disk_name" : disk.name,
                        "disk_size (GB)" : disk.size_gb,
                        "disk_type" : type,
                        "disk_description" : disk.description,
                        "disk_zone": zone.split("/")[-1],
                        "disk_creation_time": disk.creation_timestamp,
                        "attached_vms": used,
                        "creator_email": creator
                    }
                    
                    all_list.append(data)

        if len(all_list) > 0:
            
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Generate the file name using the timestamp
            disk_csv_file = f"disk_info_{timestamp}.csv"


            # Open the CSV file in write mode
            with open(disk_csv_file, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=list(all_list[0].keys()))

                # Write the header row
                writer.writeheader()

                # Write the dictionary data to the CSV file
                writer.writerows(all_list)
                
            print(f"CSV is written -> {disk_csv_file}")

        else:
            print("No any disk information found")


        vm_logging = get_vm_logging(project_name)
        all_vms = list_all_instances(project_name)

        all_instances = defaultdict(list)
        all_vmslist = []

        for zone, response in all_vms:
            
            
            if response.instances:
                all_instances[zone].extend(response.instances)
                
                for instance in response.instances:
                    machine_type = instance.machine_type.split("/")[-1]
                    print(f"Found VM : {instance.name}")
                    
                    filter_data = [item for item in all_list if instance.name in item.get('attached_vms', [])]

                    disk_info = []
                    if filter_data:
                        for entry in filter_data:
                            disk_info.append(f"{entry.get('disk_name')}:{entry.get('disk_type')}")
                    else:
                        disk_info.append("None")
                        
                    creator = "NA"

                    for item in vm_logging:
                        try:
                            if item["authorizationInfo"][0]["resourceAttributes"]["name"].split("/")[-1]==instance.name:
                                creator=(item["response"]["user"])
                                break
                        except:
                            pass

                    all_vmslist.append({
                        "vm_name" : instance.name,
                        "vm_typpe" : machine_type,
                        "disk_attached" : disk_info,
                        "zone": zone.split("/")[-1],
                        "description": instance.description,
                        "creation_timestamp" : instance.creation_timestamp,
                        "last_Start_timestamp": instance.last_start_timestamp,
                        "creator_email": creator
                    })

                    
        if len(all_vmslist) > 0:

            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Generate the file name using the timestamp
            vm_csv_file = f"vm_info_{timestamp}.csv"


            # Open the CSV file in write mode
            with open(vm_csv_file, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=list(all_vmslist[0].keys()))

                # Write the header row
                writer.writeheader()

                # Write the dictionary data to the CSV file
                writer.writerows(all_vmslist)
                
            print(f"CSV is written -> {vm_csv_file}")

        else:
            print("No any VMs information found")


        if(os.path.exists(disk_csv_file)):
            upload_cs_file(bucket_name, disk_csv_file, disk_csv_file)

        if(os.path.exists(vm_csv_file)):
            upload_cs_file(bucket_name, vm_csv_file, vm_csv_file)

    except Exception as e:
        print(f"Error in main method - {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to get the VMs and Disk information")
    parser.add_argument("project_name", help="GCP Project Name")
    parser.add_argument("bucket_name", help="Bucket Name to upload the files")
    args = parser.parse_args()

    main(args.project_name, args.bucket_name)