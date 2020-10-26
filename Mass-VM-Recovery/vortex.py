import json
import time
import requests


def get_VM_backups(base_url, version, token, vmid, vcid, latest=False):
    resource = '/backups/vmware/vms'
    filter = {
        "vcenter_id": {"$eq": vcid},
        "vm_id": {"$eq": vmid}
    }
    url = f'{base_url}{resource}?limit=500&filter={json.dumps(filter)}'
    response = http_get(url, version, token=token)
    if latest:
        pit_id = response['_embedded']['items'][0]['id']
        return pit_id
    else:
        return response['_embedded']['items']


def get_PIT_params(base_url, version, token, pit_id):
    url = f'{base_url}/backups/vmware/vms/{pit_id}'
    time.sleep(3)
    response = http_get(url, version, token=token)
    return response


def recoverVM(base_url, version, token, body):
    url = f'{base_url}/restores/vmware/vms'
    response = http_post(url, version, token, body=body)
    return response


def list_vm(base_url, version, token, vcid,
            vmname: str, idlookup=False):
    resource = f'/datasources/vmware/vcenters/{vcid}/vms'
    filter = {
        "name": {"$contains": vmname}
    }
    if vmname:
        url = f'{base_url}{resource}?limit=500&filter={json.dumps(filter)}'
    else:
        url = f'{base_url}{resource}?limit=500'
    
    response = http_get(url, version, token=token)
    
    if idlookup:
        for i in range(len(response['_embedded']['items'])):
            if response['_embedded']['items'][i]['name'] == vmname:
                return response['_embedded']['items'][i]['id']
    else:
        return response['_embedded']['items']


def list_vc(base_url, version, token):
    url = f'{base_url}/datasources/vmware/vcenters?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_tags(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/tags?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_vc_pools(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/resource-pools?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_vc_datacenters(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/datacenters?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_vc_datastores(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/datastores?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_vc_folders(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/folders?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def list_vc_networks(base_url, version, token, vcid):
    url = f'{base_url}/datasources/vmware/vcenters/{vcid}/networks?limit=500'
    response = http_get(url, version, token=token)
    return response['_embedded']['items']


def http_version_header(version: int):
    return {'Accept': f'application/api.clumio.*=v{version}+json'}


def http_get(url: str, version: int, token: str):
    headers = http_version_header(version)
    headers['Authorization'] = f'Bearer {token}'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f'HTTP GET to {url} failed with code {response.status_code}')
        print(response.status_code)
        return -1
    return response.json()


def http_post(url: str, version: int, token: str, body=None):
    headers = http_version_header(version)
    headers['Authorization'] = f'Bearer {token}'
    response = requests.post(url, headers=headers, data=json.dumps(body))
    if response.status_code != 200:
        print(f'HTTP POST to {url} failed with code {response.status_code}')
        print(response.status_code)
        return -1
    return response.json()
