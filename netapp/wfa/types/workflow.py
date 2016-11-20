from xml.etree import ElementTree as ET

from netapp.wfa.types.base import LinkedObject, Serializer

class Workflow(LinkedObject):
    # FIXME: api error? atom:link rel="self" href="https://10.60.64.210/rest/workflows/81a45bc6-70bb-4193-86bd-b840a8e7e6bc"
    # is it mixxing the numeric job id?

    _element = 'workflow'

    def __init__(self, uuid=None):
        super(Workflow, self).__init__()
        self.uuid = uuid
        self.name = None
        self.categories = []
        self.description = None
        self.min_ontap = None
        self.min_software = None
        self.link = dict()
        self.inputs = []
        self.outputs = []
        self.jobStatus = None

        pass

    def to_object(self, root):
        # do the LinkedObject parsing
        super().to_object(root)

        self.uuid = root.get('uuid')
        # this is a bit offensife, find() can return None, but in our case... never
        self.name = root.find('./name').text
        self.categories = [c.text for c in root.find('./categories/category')]
        self.description = root.find('./description').text
        self.min_ontap = self._optional_text(root.find('./minONTAPVersion'))
        self.min_software = self._optional_text(root.find('./minSoftwareVersions'))

        self.version = '.'.join([root.find('version').find(v).text for v in ('major', 'minor', 'revision')])

        ser = Serializer()
        # list of input parameters
        for elem_input in root.findall('./userInputList/userInput'):
            self.inputs.append(ser.to_object(elem_input))

        # output parameters
        for elem_output in root.findall('./returnParameters/returnParameter'):
            self.outputs.append(ser.to_object(elem_output))

        # this is only returned, when querying a job status
        elem_status = root.find('./jobStatus')
        if elem_status is not None:
            self.jobStatus = ser.to_object(elem_status)

        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Workflow(%s): v%s - %s' % (self.uuid, self.version, self.name)


class UserInput(Serializer):
    """list of user input fields in Workflow object. not used as input for Workflow submission"""
    _element = 'userInput'
    #  <userInput>
    #   <name>DestinationVserver</name>
    #   <description>Destination Storage Virtual Machine Name</description>
    #   <defaultValue/>
    #   <type>Query</type>
    #   <allowedValues/>
    #   <mandatory>true</mandatory>
    # </userInput>

    def __init__(self):
        super(UserInput, self).__init__()
        self.name = None
        self.description = None
        self.defaultValue = None
        self.type = None
        self.allowed = []
        self.mandatory = None
        self.conditional = None
        return

    def to_object(self, root):
        self.name = root.find('./name').text
        self.description = root.find('./description').text
        self.defaultValue = self._optional_text(root.find('./defaultValue'))
        self.type = root.find('type').text
        # TODO no idea how to convert this yet, need to find examples
        self.allowed = [v.text for v in root.findall('./allowedValues/value')]
        self.mandatory = self._optional_text(root.find('./mandatory')) in ['true', 'True']

        conditional = root.find('./conditionalUserInput')
        if conditional is not None:
            ser = Serializer()
            self.conditional = ser.to_object(conditional)

        return self

    def __str__(self):
        return "%s: %s [%s] %s" % (self.type, self.name, self.defaultValue, "optional" if not self.mandatory else "")

    def __repr__(self):
        return "Input(%s)" % self.__str__()


class ReturnParameter(Serializer):
    _element = 'returnParameter'
    """specification for return values to expect from workflow execution
    confusing fact: 'value' is actually more a Type of a value, like snapvault_destination_volume.name - i.e. defining the
    semantics of the value"""
    #<returnParameter>
    #  <name>snapvault_destination_volume</name>
    #  <value>snapvault_destination_volume.name</value>
    #  <description>Name of the volume provisioned for SnapVault destination.</description>
    #</returnParameter>

    def __init__(self):
        super(ReturnParameter, self).__init__()
        self.name = None

        self.value = None
        self.description = None

    def to_object(self,root):
        self.name = root.find('./name').text
        self.value = root.find('./value').text
        self.description = root.find('./description').text

        return self

    def __str__(self):
        return "%s: %s" %(self.value, self.name)

    def __repr__(self):
        return "ReturnParameter(%s)" % self.__str__()


class JobStatus(Serializer):
    _element = 'jobStatus'
    #<jobStatus>
    #    <jobStatus>COMPLETED</jobStatus>
    #    <jobType>Workflow Execution – Hello World</jobType>
    #    <scheduleType>Immediate</scheduleType>
    #    <startTime>Dec 14, 2012 12:47:27 PM</startTime>
    #    <endTime>Dec 14, 2012 12:47:36 PM</endTime>
    #    <plannedExecutionTime>Dec 14, 2012 12:47:23 PM</plannedExecutionTime>
    #    <comment>API Example Execution</comment>
    #    <returnParameters>
    #        <returnParameters value="John Doe" key="Name"/>
    #    </returnParameters>
    #</jobStatus>

    def __init__(self):
        super(JobStatus, self).__init__()
        self.value = None # Job status value, Enum
        self.type = None
        self.phase = None
        self.scheduleType = None
        self.startTime = None
        self.endTime = None
        self.plannedExecutionTime = None
        self.comment = None
        self.progress = WorkflowJobProgress()
        self.inputs = {}
        self.results = {}

    def to_object(self, root):
        self.value = root.find('./jobStatus').text
        self.phase = self._optional_text(root.find('./phase'))
        self.type = root.find('./jobType').text
        self.scheduleType = root.find('./scheduleType').text
        self.startTime = self._optional_text(root.find('./startTime'))
        self.endTime = self._optional_text(root.find('./endTime'))
        self.plannedExecutionTime = self._optional_text(root.find('./plannedExecutionTime'))
        self.comment = root.find('./comment').text

        progress_elem = root.find('./workflow-execution-progress')
        if progress_elem is not None:
            self.progress = super().to_object(progress_elem)

        # construct input data values, that were provided on job submission
        for input in root.findall('./userInputValues/userInputEntry'):
            self.inputs[input.get('key')] = input.get('value')

        #FIXME double check, if the path is really correct
        # build a dictionary of result values
        for param in root.findall('./returnParameters/returnParameters'):
            self.results[param.get('key')] = param.get('value')

        return self


class WorkflowInput(Serializer):
    """used as input data for workflow submissions, i.e. HTTP POST'ed when submitting a workflow """
    _element = 'workflowInput'
    #<workflowInput>
    #  <userInputValues>
    #    <userInputEntry key="Name" value="John Doe"/>
    #  </userInputValues>
    #  <comments>API Example Execution</comments>
    #  <executionDateAndTime>9/23/11 2:59 PM</executionDateAndTime>
    #</workflowInput>

    def __init__(self):
        super(WorkflowInput, self).__init__()
        self.comment = ""
        self.executionDateAndTime = ""
        self.values = {}

    def set_input(self, key, value):
        self.values[key] = value

    def to_payload(self):
        elem = ET.Element(self._element)

        self._append_element(elem, 'comments', self.comment)
        self._append_element(elem, 'executionDateAndTime', self.executionDateAndTime)

        userInputValues = ET.Element('userInputValues')
        for key,value in self.values.items():
            entry = self._append_element(userInputValues, 'userInputEntry')
            entry.set('key', key)
            entry.set('value', value)

        elem.append(userInputValues)
        return elem


class WorkflowJobProgress(Serializer):
    _element = 'workflow-execution-progress'

    # <?xml version="1.0" encoding="UTF-8"?>
    # <workflow-execution-progress>
    #   <current-command>...</current-command>
    #   <current-command-index>...</current-command-index>
    #   <commands-number>...</commands-number>
    #   <command-execution-progress>
    #       <current>...</current>
    #       <total>...</total>
    #       <progressPercentage>...</progressPercentage>
    #       <note>...</note>
    #   </command-execution-progress>
    # </workflow-execution-progress>

    def __init__(self):
        super(WorkflowJobProgress, self).__init__()
        self.commandName = 'unknown'
        self.commandIndex = 0
        self.commandsNumber = 100

        self.executionCurrent = 0
        self.executionTotal = 100
        self.executionPercentage = None
        self.executionNote = None

    def to_object(self, root):
        self.commandName = root.find('./current-command').text
        self.commandIndex = int(root.find('./current-command-index').text)
        self.commandTotal = int(root.find('./commands-number').text)

        elem_progress = root.find('./command-execution-progress/')

        self.executionCurrent = int(elem_progress.find('./current'))
        self.executionTotal = int(elem_progress.find('./total'))
        self.executionPercentage = int(elem_progress.find('./progressPercentage'))
        self.executionNote = elem_progress.find('./node').text


class WorkflowJob(LinkedObject):
    _element = 'job'
    """representation of a created job"""
    def __init__(self):
        super(WorkflowJob, self).__init__()
        self.id = None
        self.workflow = None
        self.jobStatus = None
        pass

    def to_object(self, root):
        super().to_object(root)
        self.id = root.get('jobId')
        self.workflow = super().to_object(root.find('./workflow'))
        self.jobStatus = super().to_object(root.find('./jobStatus'))

        return self
