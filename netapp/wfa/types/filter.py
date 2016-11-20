from netapp.wfa.types.base import LinkedObject, Serializer


class FilterBase(LinkedObject):
    """base implementation for Filter and Finders"""
    def __init__(self):
        super(FilterBase, self).__init__()
        self.id = None
        self.name = None
        self.certification = None
        self.parameters = set()
        self.dictionaryName = None

    def to_object(self, element):
        super(FilterBase, self).to_object(element)

        self.id = element.get('id')
        self.name = element.find('./name').text
        self.certification = element.find('./certification').text
        self.dictionaryName = element.find('./dictionaryName').text

        # etract parameter list
        for param_elem in element.findall('./parameters/parameter'):
            self.parameters.add(param_elem.text)

        return self


class Filter(FilterBase):
    _element = 'filter'

    def __init__(self):
        super(Filter, self).__init__()
        self.version = None
        pass

    def to_object(self, element):
        super(Filter, self).to_object(element)
        self.version = '.'.join([element.find('version').find(v).text for v in ('major', 'minor', 'revision')])

        return self

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Filter(%s)' % self.id


class ResultRow(Serializer):
    def __init__(self, columns):
        self.fields = {}
        self.columns = columns
        for col in columns:
            self.fields[col] = None

    def __getitem__(self, item):
        """allow [] operator access on column values, with column name as key"""
        return self.fields[item]

    def __iter__(self):
        """iterate over column values, in the order of columns"""
        for col in self.columns:
            yield self.fields[col]

    def get(self, key):
        return self.fields[key]

    def to_object(self, root):
        for cell_elem in root.findall('./cell'):
            key = cell_elem.get('key')
            val = cell_elem.get('value')
            self.fields[key] = val

        return self

    def __str__(self):
        """just return field values in the order defined by the columns"""
        return str([self.fields[col] for col in self.columns])


class TestResults(Serializer):

    def __init__(self):
        self.name = None
        self.dictionaryName = None
        self.parameters = {}
        self.columns = []
        self.rows = []

    def __iter__(self):
        """iterating on the test results gives back rows"""
        for row in self.rows:
            yield row

    def to_object(self, element):

        self.dictionaryName = element.find('./dictionaryName').text

        # parse parameter key/values
        for param_elem in element.findall('./parameters/parameter'):
            self.parameters[param_elem.get('key')] = param_elem.get('value')

        # process column headers, required for parsing row data
        for col_elem in element.findall('./columns/column'):
            self.columns.append(col_elem.text)

        # parse row values
        for row_elem in element.findall('./rows/row'):
            row = ResultRow(self.columns)
            self.rows.append(row.to_object(row_elem))

        return self


class FilterTestResults(TestResults):
    _element = 'filterTestResults'
    #<filterTestResults>
    #  <filterName>CM aggregates based on ONTAP version</filterName>
    #  <dictionaryName>cm_storage.Aggregate</dictionaryName>
    #<parameters>
    #  <parameter value="8.1" key="os_version"/>
    #</parameters>
    #<columns>
    #   <column>#</column>
    #   <column>name</column>
    #   <column>node.cluster.primary_address</column>
    #   <column>node.name</column>
    #</columns>
    #<rows>
    # <row>
    #   <cell value="1" key="#"/>
    #   <cell value="aggr0" key="name"/>
    #   <cell value="10.72.181.165" key="node.cluster.primary_address"/>
    #   <cell value="f3170-181-42" key="node.name"/>
    #</row> <row>
    #   <cell value="2" key="#"/>
    #   <cell value="f317018142_aggr1" key="name"/>
    #   <cell value="10.72.181.165" key="node.cluster.primary_address"/>
    #   <cell value="f3170-181-42" key="node.name"/>
    #</row> <row>

    def __init__(self):
        super(FilterTestResults, self).__init__()
        self.filterName = None

    def to_object(self, element):
        self.filterName = element.find('./filterName').text
        self.name = self.filterName
        super(FilterTestResults, self).to_object(element)

        return self


class Finder(FilterBase):
    """a finder is a set of filters, that are use together, kind of like composite design pattern?"""
    def __init__(self):
        super(Finder, self).__init__()
        self.filters = []
        pass

    def to_object(self, element):
        super(Finder, self).to_object(element)

        for filter_elem in element.findall('./filters/filter'):
            f = Filter()
            self.filters.append(f.to_object(filter_elem))

        return self


class FinderTestResults(TestResults):
    _element = 'finderTestResults'

    def __init__(self):
        super(FinderTestResults, self).__init__()
        self.finderName = None
        self.reason = None

    def to_object(self, element):
        self.finderName = element.find('./finderName').text
        self.name = self.finderName
        super(FinderTestResults, self).to_object(element)
        self.reason = self._optional_text(element.find('./reasonForNoResult'))
        return self