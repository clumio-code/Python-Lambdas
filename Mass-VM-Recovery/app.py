import json
import csv
import vortex
import boto3
import os

nl = '\n'


def recover(event, context):
    main()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def get_creds(bucket, key):
    
    s3 = connect_service('s3')
    data = s3.get_object(Bucket=bucket, Key=key)
    credsfile = data['Body'].read()
    creds = json.loads(credsfile)
    
    creds = {
        'token': creds['Token'],
        'base_url': creds['Server'],
        'target_vcid': creds['Target_vc'],
        'source_vcid': creds['Source_vc']
    }

    return creds


def get_recoveryplan(bucket, key):

    s3 = connect_service('s3')
    data = s3.get_object(Bucket=bucket, Key=key)
    decoded = data['Body'].read().decode()
    input = decoded.split('\n')
    reader = csv.DictReader(input)
    vm_list = []
    for line in reader:
        vm_list.append(line)
    return vm_list


def get_resources(base_url, token, target_vcid):
    # lookup target vcenter resource names + IDs
    datacenters = vortex.list_vc_datacenters(base_url, 1, token, target_vcid)
    res_pools = vortex.list_vc_pools(base_url, 1, token, target_vcid)
    datastores = vortex.list_vc_datastores(base_url, 1, token, target_vcid)
    networks = vortex.list_vc_networks(base_url, 1, token, target_vcid)
    folders = vortex.list_vc_folders(base_url, 1, token, target_vcid)
    tags = vortex.list_tags(base_url, 1, token, target_vcid)

    resources = {
        'datacenters': datacenters,
        'res_pools': res_pools,
        'datastores': datastores,
        'networks': networks,
        'folders': folders,
        'tags': tags
    }

    return resources


def connect_service(service, key_id=None, secret_key=None):
    '''connect client'''
    print(f'{nl}Attmpting connection to {service}')
    try:
        client = boto3.client(
            service,
            aws_access_key_id=key_id,
            aws_secret_access_key=secret_key,
            region_name=os.environ['AWS_REGION']
        )

        return client
    except Exception as e:
        print(f'{nl}Failed to connect to {service}:{nl}{e}')


def matcher(response, obj_name, obj_type: str):
    match = None
    try:
        for i in range(len(response)):
            if response[i]['name'] == obj_name:
                match = 1
                return response[i]
    except Exception as e:
        print(e)
        pass
    if not match:
        print(f'Failed to locate a matching {obj_type} for {obj_name}')


def recover_vms(vm_list, creds, items):
    for i in range(len(vm_list)):
        vmname = None
        try:
            vmname = vm_list[i]['vm_name']
            target_sddc = vm_list[i]['target_sddc']
            target_tag = vm_list[i]['target_tag']
            target_ds = vm_list[i]['target_ds']
            target_net = vm_list[i]['target_net']
            target_folder = vm_list[i]['target_folder']
            target_res_pool = vm_list[i]['target_pool']
        except Exception as e:
            print(f'''Failed to map recovery resources for {vmname}: {e}''')
            continue

        try:
            # gather VM recovery parameters
            vmid = vortex.list_vm(
                creds['base_url'], 1, creds['token'], creds['source_vcid'],
                vmname, idlookup=True)
            pit_id = vortex.get_VM_backups(
                creds['base_url'], 1, creds['token'], vmid, creds['source_vcid'],
                True)
            if pit_id:
                print(f'Found backup PIT for {vmname}')
            mac = vortex.get_PIT_params(creds['base_url'], 1, creds['token'],
                                        pit_id)['nics'][0]['mac_address']
        except Exception as e:
            print(f'''Failed to retreive VM backup PIT for {vmname}: {e}''')
            continue

        try:
            # map target vcenter resource names to IDs
            dc_id = matcher(
                items['datacenters'], target_sddc, 'datacenter')['id']
            ds_id = matcher(
                items['datastores'], target_ds, 'datastore')['id']
            res_pool_id = matcher(
                items['res_pools'], target_res_pool, 'res pool')['id']
            folder_id = matcher(
                items['folders'], target_folder, 'folder')['id']
            network_id = matcher(
                items['networks'], target_net, 'network')['id']
            tag_id = matcher(
                items['tags'], target_tag, 'tag')['id']
            cat_id = matcher(
                items['tags'], target_tag, 'tag')['category']['id']
        except Exception as e:
            print(f'Failed to match recovery inputs with VMware resources')
            print(f'{vmname}: {e}')
            continue

        try:
            # build recovery body
            body = {
                "source": {
                    "backup_id": pit_id
                },
                "target": {
                    "datacenter_id": dc_id,
                    "datastore_id": ds_id,
                    # "host_id": "string",
                    "network_options": [
                        {
                            "mac_address": mac,
                            "network_id": network_id,
                            "should_connect": True
                        }
                    ],
                    "parent_vm_folder_id": folder_id,
                    "resource_pool_id": res_pool_id,
                    "should_power_on": True,
                    "tags": [
                        {
                            "category_id": cat_id,
                            "tag_id": tag_id
                        }
                    ],
                    "vcenter_id": creds['target_vcid'],
                    "vm_name": f'restored-{vmname}'
                }
            }

            # execute restores
            print(f'Attempting the restore of {vmname}')
            task_id = None
            task_id = vortex.recoverVM(
                creds['base_url'], 1, creds['token'], body)
            if task_id['task_id']:
                print(f'Successfully initiated recovery of {vmname}:{task_id}')
            else:
                print(f'{task_id}')
            print('\n')

        except Exception as e:
            print(f'''Failed to recover {vmname}: {e}''')
            pass


def main():
    creds = get_creds(os.environ['bucket'], os.environ['creds'])
    print(f'successfully imported creds: {creds}')
    vm_list = get_recoveryplan(os.environ['bucket'], os.environ['csv'])
    print(f'successfully imported recovery plan: {vm_list}')
    items = get_resources(
        creds['base_url'], creds['token'], creds['target_vcid'])
    print(f'successfully retrieved all source vCenter assets: {items}')
    recover_vms(vm_list, creds, items)
