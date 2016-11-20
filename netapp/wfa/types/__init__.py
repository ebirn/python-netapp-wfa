

from netapp.wfa.types.base import Serializer
from netapp.wfa.types.filter import *
from netapp.wfa.types.workflow import *



Serializer.register('collection', base.Collection)

# Workflow related serializations
Serializer.register('workflow', workflow.Workflow)
Serializer.register('userInput', workflow.UserInput)
Serializer.register('conditionalUserInput', workflow.UserInput)
Serializer.register('returnParameter', workflow.ReturnParameter)
Serializer.register('jobStatus', workflow.JobStatus)
Serializer.register('job', workflow.WorkflowJob)
Serializer.register('workflow-execution-progress', workflow.WorkflowJobProgress)


# register filter serialization
Serializer.register('filter', filter.Filter)
Serializer.register('filterTestResults', filter.FilterTestResults)

# register finder data types
Serializer.register('finder', filter.Finder)
Serializer.register('finderTestResults', filter.FinderTestResults)

