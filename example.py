#!/usr/bin/env python3

# examples on how to use the WFA client

import netapp.wfa as wfa


# base address of rest endoint
endpoint = 'https://wfa-server.example.com/'

# user credentials
user='your_storage_manager'
password='<secret_phrase>'

# if you must
ssl_verify = False

# globally, statically configure backend (set as class attributes)
wfa.configure(user, password, endpoint, ssl_verify)


# start doing some work:
workflow_service = wfa.WorkflowService()

# get a list of all workflows
all_workflows = workflow_service.list()

# find a workflow by nam
snap_mirror_workflow = workflow_service.find('Resync SnapMirror relationship')
snap_mirror_workflow = workflow_service.workflow_by_uuid('81a45bc6-70bb-4193-86bd-b840a8e7e6bc')

# the Workflow instance snap_mirror_workflow.
workflow_input = wfa.WorkflowInput()
workflow_input.set_input('key', 'value')

workflow_service.execute(workflow=snap_mirror_workflow, input=workflow_input)


# filters can get a list of available resources - matching conditions - from WFA
filter_service = wfa.FilterService()
# all available filters
all_filters = filter_service.list()

# get individual filter and execute
# filter = filter_service.filter_by_id('individual-uuid-asdf')
# params need to be set depending on filter (see filter.params property)
# params = {}
# filter_results = filter_service.test_filter(filter, params)


# mostly you will use Finders instead of filter
# Finders are a combination of filters, that are all called with the identical parameter set
finder_service = wfa.FinderService()
# all available filters
all_finders = finder_service.list()

# filters, related to dicationary name
volume_finders = finder_service.list(dictionary='cm_storage.volume')
for vol_finder in volume_finders:
    print(vol_finder)

# execute a finder
# this finder finds all volumes in given svm
finder_id='70eb184d-44f9-42f5-ae21-e76c0a318a0b'
vol_finder = finder_service.finder_by_id(finder_id)
finder_results = finder_service.test_finder(vol_finder, cluster_name='my_cluster', vserver_name='my_svm_vserver', vol_name='my_vol')

# now get the result values from the finder call
print('Columns: %s' % finder_results.columns)
# iterate rows
for row in finder_results:
    # iterate column in rows, could also do: row[column_name], the rows are of type ResultRow
    print('row: ', end='')
    for col in row:
        print('= %s =' % col, end='')
    print()


