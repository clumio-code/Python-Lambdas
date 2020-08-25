-------
Publisher:
-------

Luke McCleary

Luke@clumio.com

---------
Summary:
---------

This Lamda app provides automated recovery of VMware Virtual Machines for the Clumio platform 

-------
Instructions:
-------

1. Download the dependencies, app, and vortex files
2. Unzip the dependencies
3. zip everthing up and load into a lambda
4. Upload the customized recovery plan and credentials files to an S3 bucket (same region)
5. Add the required Lambda Environemental Variables
6. RUN!

------------
Lambda Variables:
------------

This script requires the following environmental variables:

1. base_url
   - The URL for your Clumio managment plane. Example: https://us-east-1.api.clumio.com

2. bucket
   - The S3 bucket name containing the creds and recovery plan files

3. creds
   - The name of the JSON file in the S3 bucket
   - Be sure to add your own API key + Source and Target vCenter information

4. csv
   - The name of the recovery plan CSV file in the bucket
   -follow the formatting in the example recovery plan. Header line must be maintained.

------------------------
Lambda Permissions
------------------------

In addition to the base lambda permissions, this role will also need access to the s3 bucket containting the credendtial and recovery plan files



