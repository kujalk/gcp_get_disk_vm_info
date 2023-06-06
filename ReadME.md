Method
---------------

- Create virtual directory
    python -m venv virtual
    virtual/scripts/activate

- Install required packages
    pip install -r requirements.txt

- Run the script 
  1. If you are using CloudShell to run, then authorize the shell and run the script
  python .\list_vm_disk_info.py mygcp-projectid gcpbucketname

  2. If you use local machine, then download the service account json key which have appropriate access and set the path of the key file as env variable

  set GOOGLE_APPLICATION_CREDENTIALS=E:\\tf_svc_key.json
  
  python .\list_vm_disk_info.py mygcp-projectid gcpbucketname
