""" resource operations
"""
from typing import Optional

import irods.exception
import irods.resource

from ibridges.irodsconnector import keywords as kw
from ibridges.irodsconnector import session


class Resources(object):
    """Irods Resource operations """

    def __init__(self, session: session.Session):
        """ iRODS resource initialization

            Parameters
            ----------
            session : session.Session
                instance of the Session class
        """
        self._resources: Optional[dict] = None
        self.session = session

    def get_resource(self, resc_name: str) -> irods.resource.iRODSResource:
        """Instantiate an iRODS resource.

        Prameters
        ---------
        resc_name : str
            Name of the iRODS resource.

        Returns
        -------
        iRODSResource
            Instance of the resource with `resc_name`.

        Raises:
            irods.exception.ResourceDoesNotExist

        """
        try:
            return self.session.irods_session.resources.get(resc_name)
        except irods.exception.ResourceDoesNotExist as error:
            return {'successful': False, 'reason': repr(error)}

    def get_free_space(self, resc_name: str) -> int:
        """Determine free space in a resource hierarchy.

        Storeage resources: return annotation "free_space".
        Coordinating resources: return sum of all free space of the resource subtree.
        If "free_space" is not set, set value to 0.

        Parameters
        ----------
        resc_name : str
            Name of monolithic resource or the top of a resource tree.

        Returns
        -------
        int
            Number of bytes free in the resource hierarchy.

        The return value can have one of two possible values if not the actual
        free space:

            -1 if the resource does not exists (typo or otherwise)
             0 if no free space has been set in the whole resource tree
                starting at node resc_name.

        """
        try:
            resc = self.session.irods_session.resources.get(resc_name)
        except irods.exception.ResourceDoesNotExist:
            return -1
        if resc.free_space is not None:
            return int(resc.free_space)
        children = self.get_resource_children(resc)
        free_space = sum((
            int(child.free_space) for child in children
            if child.free_space is not None))
        return free_space

    def get_resource_children(self, resc: irods.resource.iRODSResource) -> list:
        """Get all the children for the resource `resc`.

        Parameters
        ----------
        resc : instance
            iRODS resource instance.

        Returns
        -------
        list
            Instances of child resources.

        """
        children = []
        for child in resc.children:
            children.extend(self.get_resource_children(child))
        return resc.children + children

    def resources(self, update: bool = False) -> dict:
        """iRODS resources and their metadata.

        Parameters
        ----------
        update
            Fetch information from iRODS server and overwrite _resources

        Returns
        -------
        dict
            Name, parent, status, context, and free_space of all
            resources.

        NOTE: free_space of a resource is the free_space annotated, if
              so annotated, otherwise it is the sum of the free_space of
              all its children.

        """
        if self._resources is None or update:
            query = self.session.irods_session.query(
                kw.RESC_NAME, kw.RESC_PARENT, kw.RESC_STATUS, kw.RESC_CONTEXT)
            resc_list = []
            for item in query.get_results():
                name, parent, status, context = item.values()
                free_space = 0
                if parent is None:
                    free_space = self.get_free_space(name)
                metadata = {
                    'parent': parent,
                    'status': status,
                    'context': context,
                    'free_space': free_space,
                }
                resc_list.append((name, metadata))
            resc_dict = dict(
                sorted(resc_list, key=lambda item: str.casefold(item[0].decode())))
            self._resources = resc_dict
        return self._resources

    @property
    def root_resources(self) -> list:
        """
        Filter resources for all root resources (data can only be written to root resources).
        Return their names, their status and their free space.

        Returns:
        List [(resource_name, status, free_space, context)]
        """
        parents = [(key, val) for key, val in self.resources().items() if not val['parent']]
        return [(resc[0], resc[1]["status"], resc[1]["free_space"], resc[1]["context"]) 
                for resc in parents]
