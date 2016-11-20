# python-netapp-wfa
Python 3.x client for the NetApp OnCommand Workflow Automation (WFA) REST API

### external dependencies
The client is based on Python 3.5, mostly the `xml.etree.*` modules.
The only external dependency is the `requests` package, see `requirements.txt` file.
```
pip install -r requirements.txt
```
## Quickstart
```
import netapp.wfa as wfa

wfa.configure('username', 'password', 'https://my-wfa.example.com/')

service = wfa.WorkflowService()
all_workflows = service.list()

my_workflow = all_workflow[3]
wf_inputs = WorkflowInputs()
wf_inputs.set_input('key', 'value')

job_status = service.execute(my_workflow, wf_inputs)

```


## NetApp OnCommand Workflow Automation
you need a NetApp mySupport account for this (https://mysupport.netapp.com/) - sorry.
The development of this client was done against WFA 4.0, 
see NetApp documentation below (specifically the REST Web Services Primer)

OnCommand® Workflow Automation 4.0 for Linux® Download:
[https://mysupport.netapp.com/NOW/download/software/ocwfa_linux/4.0/]()

OnCommand Workflow Automation 4.0 Documentation
[https://mysupport.netapp.com/documentation/docweb/index.html?productID=62307&language=en-US]()

REST Web Services Primer for WFA 4.0
[https://library.netapp.com/ecm/ecm_download_file/ECMLP2436051]()

## status of implemetation
currently only these endpoints are implemented

- Workflow
- Filter
- Finder
 
But... this is not even half of the API? True, but the intention of this client is primarily to kick off workflows 
(and monitor their progress / status) for integration with other frameworks
  
