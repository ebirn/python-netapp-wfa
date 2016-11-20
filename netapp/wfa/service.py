# basic connection / api endpoint setup
# this should never be used, when programming against the library

from netapp.wfa.endpoint import Endpoint
from requests import HTTPError

class WorkflowError(Exception):
    pass


class WorkflowService(Endpoint):
    """execute and control / query / workflows, watch status during execution"""
    def __init__(self):
        super(WorkflowService, self).__init__(uri='/rest/workflows')
        return

    #FIXME bug in WFA api? this only works with exact matches
    def find(self, name=None, categories=None):

        #ensure categories is a list
        if not isinstance(categories, (list, tuple)):
            categories = list(categories)

        """search for workflows matching 'name'"""
        params = dict()
        params['name'] = name
        params['categories'] = categories
        return self.http_get(params=params)

    def workflow_by_uuid(self, uuid):
        """load workflow directly via its uuid, when not selecting it from the list or search result"""
        # https://10.60.64.210/rest/workflows/81a45bc6-70bb-4193-86bd-b840a8e7e6bc
        return self.http_get(url=self._endpoint + '/rest/workflows/%s' % uuid)

    def job_by_id(self, workflow_uuid, job_id):
        return self.http_get(url=self._endpoint + '/rest/workflows/%s/jobs/%s' % (workflow_uuid, job_id))

    def list(self):
        """list all available workflows"""
        return self.http_get()

    def preview(self, workflow, input):
        """dry run a workflow, result will show return values"""
        res = None
        try:
            res = self.http_post(input, workflow.links['preview'])
        except HTTPError as he:
            print("body: %s" % he.response.text)

        # if all is good, returns a list of output parameters (or empty list)
        return res

    def execute(self, workflow, input):
        """start/launch a workflow with given inputs"""
        return self.http_post(input, url=workflow.links['execute'])

    def cancel(self, job):
        """cancel a running workflow job"""
        return self.http_post(job, url=job.links['cancel'])

    def add(self, job):
        """ to create job, is it redo? """
        return self.http_post(job, url=job.links['add'])

    def outputs(self, job):
        """get the outputs of a workflow execution"""
        return self.http_get(url=job.links['out'])

    def update(self, job, wait=False):
        """get updated job status,
        @:param wait=True will wait for job to terminate (but: no logpolling support yet)"""
        params = None
        if wait:
            params = {'waitinterval': 0}
        return self.http_get(url=job.links['self'], params=params)

    def resume(self, job):
        """continue a workflow execution that was previously halted / stopped"""
        return self.http_post(job, url=job.links['resume'])

    def cleanup(self, job):
        """DELETE resources from failed job executions"""
        return self.http_delete(job.links['reservation'])


class FilterService(Endpoint):
    """ retrieve and text/execute filters"""
    def __init__(self):
        super(FilterService, self).__init__(uri='/rest/filters')

        return

    def list(self, dictionary=None):
        """get list of available filter, or select list for filters in dictionary
        dictionary is the type of result value, examples:
            cm_storage.aggregate
            cm_storage.volume
        @:parameter dictionary String that filter should belong to, to be in result list"""
        params = None
        if dictionary:
            params = {'dictionary': dictionary}

        return self.http_get(params=params)

    def filter_by_id(self, id):
        """load a filter by its unique id"""
        return self.http_get(self.url + '/' + id)

    def test_filter(self, filter, **params):
        """execute filter and get result list"""
        return self.http_get(filter.links['test'], params=params)

    def test_filter_no_reservation(self, filter, **params):
        """get filter results while ignoring reservations/reserved resources"""
        return self.http_get(filter.links['test'], params=params)
    pass


class FinderService(Endpoint):
    """ retrieve and text/execute finders (combinations of filters)"""
    def __init__(self):
        super(FinderService, self).__init__(uri='/rest/finders')

        return

    def list(self, dictionary=None):
        """get list of available _finders_, or select list for filters in dictionary
        dictionary is the type of result value, examples:
            cm_storage.aggregate
            cm_storage.volume
        @:parameter dictionary String that filter should belong to, to be in result list"""
        params = None
        if dictionary:
            params = {'dictionary': dictionary}

        return self.http_get(params=params)

    def finder_by_id(self, id):
        """load a finder by its unique id"""
        return self.http_get(self.url + '/' + id)

    def test_finder(self, finder, **params):
        """execute finder and get result list"""
        return self.http_get(finder.links['test'], params=params)

    def test_finder_no_reservation(self, finder, **params):
        """get finder results while ignoring reservations/reserved resources"""
        return self.http_get(finder.links['test'], params=params)



