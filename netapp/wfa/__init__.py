
# auto import all the wfa service classes
from netapp.wfa.service import WorkflowService, FilterService, FinderService

from .endpoint import configure as configure
from .types import Workflow
from .types import WorkflowInput
from .types import WorkflowJobProgress
from .types import WorkflowJob