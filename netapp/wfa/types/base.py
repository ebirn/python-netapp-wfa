from xml.etree import ElementTree as ET

import abc
from abc import ABCMeta


class Serializer(object, metaclass=ABCMeta):
    """base class for all objects, that do serialization from / to (mostly from) NetApp OnCommand WFA
    to_object() is used by the Service classes to parse the XML, to_payload()
    generates XML Body for POST, PUT requests """

    _element = None
    _mapping = dict()

    @classmethod
    def register(cls, element, the_class):
        """register to serialize XML elements into given classname"""
        cls._mapping[element] = type(the_class())

    def __init__(self):
        pass

    @staticmethod
    def _optional_text(field):
        """return text value of optional element (or None)"""
        if field is not None:
            return field.text
        return None

    #@abc.abstractmethod
    def to_object(self, root):
        """convert xml tree into object graph, needs to be overridden"""

        # convert the object if the tag / class pair was registered before
        if root.tag in self._mapping:
            t = self._mapping[root.tag]
            obj = t()

            return obj.to_object(root)
        else:
            print("Unknown element: %s - need to register tag in Serializer.register(tag_name, class_type)" % root.tag)

        return None

    # @abc.abstractmethod not all of them may need implementation after all
    def to_payload(self):
        """default of payload genaration is empty, raising NotImplementatedError"""
        raise NotImplementedError("to_payload() is not implemented in %s" % type(self).__name__)
        pass

    @staticmethod
    def _append_element(parent, tag, text=None):
        """ append a sub element to parent, with given tag name and text value
        @:returns newly created xml element
        """
        sub_elem = ET.Element(tag)
        sub_elem.text = text
        parent.append(sub_elem)
        return sub_elem


class LinkedObject(Serializer, metaclass=ABCMeta):
    """Base class for data objects that contain atom links. the links are stored in a dict self.links,
        the rel="" attribute as the value, i.e. self.links[rel] = href"""

    _element = None

    def __init__(self):
        super(LinkedObject, self).__init__()
        self.links = {}

    def to_object(self, element):
        """parse atom links and add to dict """
        for link in element.findall('./{http://www.w3.org/2005/Atom}link'):
            self.links[link.get('rel')] = link.get('href')

        return self


class Collection(Serializer):
    """container object, like a list"""
    _element = 'collection'

    def __init__(self):
        super(Collection, self).__init__()
        self._items = []

        pass

    @property
    def items(self):
        return list(self._items)

    @items.setter
    def items(self, items):
        self._items = items

    def append(self, x):
        self._items.append(x)

    def __iter__(self):
        self._items.__iter__()

    def __contains__(self, item):
        return item in self._items

    def to_object(self, element):
        if element.tag != self._element:
            raise TypeError('cannot create %s from element %s' % (self._element, element.tag))

        for child in element:
            self.append(super().to_object(child))

        return self._items

    def to_payload(self, element=None):
        if element is None:
            element = self._element

        root = ET.Element(element)

        for item in self._items:
            root.append(item.to_payload())

        tree = ET.ElementTree(root)
        return tree

    def __repr__(self):
        return "Collection(%s)" % len(self._items)
