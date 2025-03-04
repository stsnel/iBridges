""" collections and data objects
"""
import os
import warnings
from pathlib import Path
from typing import Optional, Union

import irods.collection
import irods.data_object
import irods.exception
from irods.models import DataObject

from ibridges.irodsconnector import keywords as kw
from ibridges.irodsconnector.session import Session
from ibridges.utils.path import IrodsPath


def get_dataobject(session: Session,
                   path: Union[str, IrodsPath]) -> irods.data_object.iRODSDataObject:
    """Instantiate an iRODS data object.

    Parameters
    ----------
    path : str
        Name of an iRODS data object.

    Returns
    -------
    iRODSDataObject
        Instance of the data object with `path`.

    """
    path = IrodsPath(session, path)
    if path.dataobject_exists():
        return session.irods_session.data_objects.get(str(path))
    if path.collection_exists():
        raise ValueError("Error retrieving data object, path is linked to a collection."
                         " Use get_collection instead to retrieve the collection.")

    raise irods.exception.DataObjectDoesNotExist(path)

def obj_replicas(obj: irods.data_object.iRODSDataObject) -> list[tuple[int, str, str, int, str]]:
    """Retrieves information about replicas (copies of the file on different resources)
    of the data object in the iRODS system.

    Parameters
    ----------
    obj : irods.data_object.iRODSDataObject
        The data object

    Returns
    -------
    list(tuple(int, str, str, int, str))
        List with tuple where each tuple contains replica index/number, resource name on which
        the replica is stored about one replica, replica checksum, replica size,
        replica status of the replica
    """
    #replicas = []
    repl_states = {
        '0': 'stale',
        '1': 'good',
        '2': 'intermediate',
        '3': 'write-locked'
    }

    replicas = [(r.number, r.resource_name, r.checksum,
                 r.size, repl_states.get(r.status, r.status)) for r in obj.replicas]

    return replicas

def get_collection(session: Session,
                   path: Union[str, IrodsPath]) -> irods.collection.iRODSCollection:
    """Instantiate an iRODS collection.

    Parameters
    ----------
    path : str
        Name of an iRODS collection.

    Returns
    -------
    iRODSCollection
        Instance of the collection with `path`.

    """
    path = IrodsPath(session, path)
    if path.collection_exists():
        return session.irods_session.collections.get(str(path))
    if path.dataobject_exists():
        raise ValueError("Error retrieving collection, path is linked to a data object."
                         " Use get_dataobject instead to retrieve the data object.")
    raise irods.exception.CollectionDoesNotExist(path)

def is_dataobject(item) -> bool:
    """Determine if item is an iRODS data object
    """
    return isinstance(item, irods.data_object.iRODSDataObject)

def is_collection(item) -> bool:
    """Determine if item is an iRODS collection
    """
    return isinstance(item, irods.collection.iRODSCollection)

def _obj_put(session: Session, local_path: Union[str, Path], irods_path: Union[str, IrodsPath],
             overwrite: bool = False, resc_name: str = '', options: Optional[dict] = None):
    """Upload `local_path` to `irods_path` following iRODS `options`.

    Parameters
    ----------
    local_path : str or Path
        Path of local file.
    irods_path : str or IrodsPath
        Path of iRODS data object or collection.
    resc_name : str
        Optional resource name.

    """
    local_path = Path(local_path)
    irods_path = IrodsPath(session, irods_path)

    if not local_path.is_file():
        raise ValueError("local_path must be a file.")

    # Check if irods object already exists
    obj_exists = IrodsPath(session,
                           irods_path / local_path.name).dataobject_exists() \
                 or irods_path.dataobject_exists()

    options = {
        kw.ALL_KW: '',
        kw.NUM_THREADS_KW: kw.NUM_THREADS,
        kw.REG_CHKSUM_KW: '',
        kw.VERIFY_CHKSUM_KW: ''
    }
    if resc_name not in ['', None]:
        options[kw.RESC_NAME_KW] = resc_name
    if overwrite or not obj_exists:
        session.irods_session.data_objects.put(local_path, str(irods_path), **options)
    else:
        raise irods.exception.OVERWRITE_WITHOUT_FORCE_FLAG

def _obj_get(session: Session, irods_path: Union[str, IrodsPath], local_path: Union[str, Path],
             overwrite: bool = False, options: Optional[dict] = None):
    """Download `irods_path` to `local_path` following iRODS `options`.

    Parameters
    ----------
    irods_path : str or IrodsPath
        Path of iRODS data object.
    local_path : str or Path
        Path of local file or directory/folder.
    options : dict
        iRODS transfer options.

    """
    irods_path = IrodsPath(session, irods_path)
    if not irods_path.dataobject_exists():
        raise ValueError("irods_path must be a data object.")
    if options is None:
        options = {}
    options.update({
        kw.NUM_THREADS_KW: kw.NUM_THREADS,
        kw.VERIFY_CHKSUM_KW: '',
        })
    if overwrite:
        options[kw.FORCE_FLAG_KW] = ''

    session.irods_session.data_objects.get(str(irods_path), local_path, **options)

def _create_irods_dest(local_path: Path, irods_path: IrodsPath):
    """ Assmbles the irods destination paths for upload of a folder
    """

    upload_path = irods_path.joinpath(local_path.name)
    paths = [(root.removeprefix(str(local_path)), f)
             for root, _, files in os.walk(local_path) for f in files]

    source_to_dest = [(local_path.joinpath(folder.lstrip(os.sep), file_name),
                       upload_path.joinpath(folder.lstrip(os.sep), file_name))
                       for folder, file_name in paths]

    return source_to_dest

def _upload_collection(session: Session, local_path: Union[str, Path],
                       irods_path: Union[str, IrodsPath],
                       overwrite: bool = False, resc_name: str = '',
                       options: Optional[dict] = None):
    """Upload a local directory to iRODS

    Parameters
    ----------
    local_path : Path
        Absolute path to the directory to upload
    irods_path : IrodsPath
        Absolute irods destination path
    overwrite : bool
        If data already exists on iRODS, overwrite
    resc_name : str
        Name of the resource to which data is uploaded, by default the server will decide
    options : dict
        More options for the upload
    """
    local_path = Path(local_path)
    irods_path = IrodsPath(session, irods_path)
    # get all files and their relative path to local_path
    if not local_path.is_dir():
        raise ValueError("local_path must be a directory.")

    source_to_dest = _create_irods_dest(local_path, irods_path)
    for source, dest in source_to_dest:
        _ = create_collection(session, dest.parent)
        try:
            _obj_put(session, source, dest, overwrite, resc_name, options)
        except irods.exception.OVERWRITE_WITHOUT_FORCE_FLAG:
            warnings.warn(f'Upload: Object already exists\n\tSkipping {source}')

def _create_local_dest(session: Session, irods_path: IrodsPath, local_path: Path):
    """Assmbles the local destination paths for download of a collection
    """
    # get all data objects
    coll = get_collection(session, irods_path)
    all_objs = _get_data_objects(session, coll)

    download_path = local_path.joinpath(irods_path.name.lstrip('/'))
    source_to_dest = [(IrodsPath(session, subcoll_path, obj_name),
                      Path(download_path,
                           subcoll_path.removeprefix(str(irods_path)).lstrip('/'),
                           obj_name))
                      for subcoll_path, obj_name, _, _ in all_objs]

    return source_to_dest


def _download_collection(session: Session, irods_path: Union[str, IrodsPath], local_path: Path,
                         overwrite: bool = False, options: Optional[dict] = None):
    """Download a collection to the local filesystem

    Parameters
    ----------
    irods_path : IrodsPath
        Absolute irods source path pointing to a collection
    local_path : Path
        Absolute path to the destination directory
    overwrite : bool
        Overwrite existing local data
    options : dict
        More options for the download
    """

    irods_path = IrodsPath(session, irods_path)
    if not irods_path.collection_exists():
        raise ValueError("irods_path must be a collection.")

    source_to_dest = _create_local_dest(session, irods_path, local_path)

    for source, dest in source_to_dest:
        # ensure local folder exists
        if not dest.parent.is_dir():
            os.makedirs(dest)
        try:
            _obj_get(session, source, dest, overwrite, options)
        except irods.exception.OVERWRITE_WITHOUT_FORCE_FLAG:
            warnings.warn(f'Download: File already exists\n\tSkipping {source}')

def upload(session: Session, local_path: Union[str, Path], irods_path: Union[str, IrodsPath],
           overwrite: bool = False, resc_name: str = '', options: Optional[dict] = None):
    """Upload a local directory  or file to iRODS

    Parameters
    ----------
    local_path : Path
        Absolute path to the directory to upload
    irods_path : IrodsPath
        Absolute irods destination path
    overwrite : bool
        If data_description_ already exists on iRODS, overwrite
    resc_name : str
        Name of the resource to which data is uploaded, by default the server will decide
    options : dict
        More options for the upload
    """

    local_path = Path(local_path)
    try:
        if local_path.is_dir():
            _upload_collection(session, local_path, irods_path, overwrite, resc_name, options)
        else:
            _obj_put(session, local_path, irods_path, overwrite, resc_name, options)
    except irods.exception.CUT_ACTION_PROCESSED_ERR as exc:
        raise irods.exception.CUT_ACTION_PROCESSED_ERR(
            f"During upload operation to '{irods_path}': iRODS server forbids action.") from exc

def download(session: Session, irods_path: Union[str, IrodsPath], local_path: Union[str, Path],
             overwrite: bool = False, _resc_name: str = '', options: Optional[dict] = None):
    """Download a collection or data object to the local filesystem

    Parameters
    ----------
    irods_path : IrodsPath
        Absolute irods source path pointing to a collection
    local_path : Path
        Absolute path to the destination directory
    overwrite : bool
        Overwrite existing local data
    options : dict
        More options for the download
    """
    irods_path = IrodsPath(session, irods_path)
    local_path = Path(local_path)
    try:
        if irods_path.collection_exists():
            _download_collection(session, irods_path, local_path, overwrite, options)
        else:
            _obj_get(session, irods_path, local_path, overwrite, options)
    except irods.exception.CUT_ACTION_PROCESSED_ERR as exc:
        raise irods.exception.CUT_ACTION_PROCESSED_ERR(
            f"During download operation from '{irods_path}': iRODS server forbids action."
            ) from exc

def get_size(session: Session, item: Union[irods.data_object.iRODSDataObject,
                               irods.collection.iRODSCollection]) -> int:
    """Collect the sizes of a data object or a
    collection.

    Parameters
    ----------
    item : iRODSDataObject or iRODSCollection


    Returns
    -------
    int
        Total size [bytes] of the iRODS object or all iRODS objects in the collection.

    """
    if is_dataobject(item):
        return item.size
    all_objs = _get_data_objects(session, item)
    return sum(size for _, _, size, _ in all_objs)

def _get_data_objects(session: Session,
                      coll: irods.collection.iRODSCollection) -> list[str, str, int, str]:
    """Retrieve all data objects in a collection and all its subcollections.

    Parameters
    ----------
    coll : irods.collection.iRODSCollection
        The collection to search for all data pbjects

    Returns
    -------
    list of all data objects
        [(cllection path, name, size, checksum)]
    """

    # all objects in the collection
    objs = [(obj.collection.path, obj.name, obj.size, obj.checksum)
            for obj in coll.data_objects]

    # all objects in subcollections
    data_query = session.irods_session.query(kw.COLL_NAME, kw.DATA_NAME,
                                                  DataObject.size, DataObject.checksum)
    data_query = data_query.filter(kw.LIKE(kw.COLL_NAME, coll.path+"/%"))
    for res in data_query.get_results():
        path, name, size, checksum = res.values()
        objs.append((path, name, size, checksum))

    return objs

def create_collection(session: Session,
                      coll_path: Union[IrodsPath, str]) -> irods.collection.iRODSCollection:
    """Create a collection and all collections in its path.

    Parameters
    ----------
    coll_path: IrodsPath
        Collection path
    """
    try:
        return session.irods_session.collections.create(str(coll_path))
    except irods.exception.CUT_ACTION_PROCESSED_ERR as exc:
        raise irods.exception.CUT_ACTION_PROCESSED_ERR(
                f"While creating collection at '{coll_path}': iRODS server forbids action."
              ) from exc
