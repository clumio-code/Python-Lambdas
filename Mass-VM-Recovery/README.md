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

1. Clone this repo
2. Install the dependencies locally ("pip install -r requirements.txt -t ." to install the dependencies)
3. zip everthing up
4. Upload to S3 (same region as lambda deployment)
5. Add your S3 zipfile URL to the yaml template
6. Deploy the yaml template in cloud formations
7. Add the required Lambda Environemental Variables
8. RUN!

------------
Lambda Variables:
------------

This script requires the following environmental variables:


1. bucket
   - The S3 bucket name containing the creds and recovery plan files

2. creds
   - The name of the JSON file in the S3 bucket
   - Be sure to add your own API key + Source and Target vCenter information

3. csv
   - The name of the recovery plan CSV file in the bucket
   - Follow the formatting in the example recovery plan. Header line must be maintained.

------------------------
Lambda Permissions
------------------------

In addition to the base lambda permissions, this role will also need access to the s3 bucket containting the credendtial and recovery plan files



