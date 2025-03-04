""" metadata operations
"""
from typing import Iterator, Optional, Sequence, Union

import irods.exception
import irods.meta


class MetaData():
    """Irods metadata operations """

    def __init__(self, item):
        self.item = item

    def __iter__(self) -> Iterator:
        for m in self.item.metadata.items():
            yield m

    def __contains__(self, val: Union[str, Sequence]) -> bool:
        if isinstance(val, str):
            val = [val]
        all_attrs = ["name", "value", "units"][:len(val)]
        for meta in self:
            n_same = 0
            for i_attr, attr in enumerate(all_attrs):
                if getattr(meta, attr) == val[i_attr] or val[i_attr] is None:
                    n_same += 1
                else:
                    break
            if n_same == len(val):
                return True
        return False

    def __repr__(self) -> str:
        """Create a sorted representation of the metadata"""

        # Sort the list of items name -> value -> units, where None is the lowest
        meta_list = list(self)
        meta_list = sorted(meta_list, key=lambda m: (m.units is None, m.units))
        meta_list = sorted(meta_list, key=lambda m: (m.value is None, m.value))
        meta_list = sorted(meta_list, key=lambda m: (m.name is None, m.name))
        meta_str = ""
        for m in meta_list:
            meta_str += f" - {{name: {m.name}, value: {m.value}, units: {m.units}}}\n"
        return meta_str

    def __str__(self) -> str:
        return self.__repr__()

    def add(self, key: str, value: str, units: Optional[str] = None):
        """
        Adds metadata to all items

        Parameters
        ----------
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string

        Throws:
            CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME
        """
        try:
            if (key, value, units) in self:
                raise irods.exception.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME()
            self.item.metadata.add(key, value, units)
        except irods.exception.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME as error:
            raise ValueError("ADD META: Metadata already present") from error
        except irods.exception.CAT_NO_ACCESS_PERMISSION as error:
            raise ValueError("UPDATE META: no permissions") from error

    def set(self, key: str, value: str, units: Optional[str] = None):
        """Set the metadata entry.

        If the metadata entry already exists, then all metadata entries with
        the same key will be deleted before adding the new entry. An alternative
        is using the add method to only add to the metadata entries and not
        delete them.

        Parameters
        ----------
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string

        Throws: CAT_NO_ACCESS_PERMISSION
        """
        self.delete(key, None)
        self.add(key, value, units)

    def delete(self, key: str, value: Optional[str], units: Optional[str] = None):
        """
        Deletes a metadata entry of all items

        Parameters
        ----------
        items: list of iRODS data objects or iRODS collections
        key: string
        value: string
        units: (optional) string

        Throws:
            CAT_SUCCESS_BUT_WITH_NO_INFO: metadata did not exist
        """
        try:
            if value is None:
                metas = self.item.metadata.get_all(key)
                value_units = [(m.value, m.units) for m in metas]
                if (value, units) not in value_units:
                    for meta in metas:
                        self.item.metadata.remove(meta)
            else:
                self.item.metadata.remove(key, value, units)
        except irods.exception.CAT_SUCCESS_BUT_WITH_NO_INFO as error:
            raise KeyError(f"Cannot delete metadata with key '{key}', value '{value}'"
                             f" and units '{units}' since it does not exist.") from error
        except irods.exception.CAT_NO_ACCESS_PERMISSION as error:
            raise ValueError("Cannot delete metadata due to insufficient permission for "
                             "path '{item.path}'.") from error

    def clear(self):
        """Delete all metadata belonging to the item.
        """
        for meta in self:
            self.item.metadata.remove(meta)
