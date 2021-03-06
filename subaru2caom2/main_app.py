# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2021.                            (c) 2021.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

"""
This module implements the ObsBlueprint mapping, as well as the workflow
entry point that executes the workflow.

From SGw in Confluence:

All the raw data from Subaru Suprime-Cam has been downloaded and processed.
See this paper:
https://ui.adsabs.harvard.edu/abs/2020ASPC..527..575G/abstract

The files currently reside in: vos:sgwyn/suprime

The following sub-directories should be moved somewhere more permanent. All
the files should be moved to the new storage. Ideally the directory
structure should be preserved, but if not the filenames are unique and could
be put into a single namespace.

1. vos:sgwyn/suprime/images/ : the individual images downloaded from STARS,
stored as 1 file per image extension, includes science images and
calibration data. The images are stored the way Subaru stores them: 10
individual files, one per CCD of the mosaic. The filenames look like
SUPA0009658.fits.fz. The last digit refers to one of the 10 CCDs. Note that
for the first year, the camera only had 8 CCDs. These images are
uncalibrateable. Relevant keywords include:

FILTER01 (because FILTER would be too simple)
DATA-TYP (OBJECT, DOMEFLAT, BIAS, …)
DATE-OBS
UT-STR
EXPTIME

2. vos:sgwyn/suprime/proc/ : the calibrated science images, merged into .fz
compressed MEFs. Not all images were calibrated.  Filenames are like
SUPA0000965p.fits.fz. Process = SCLA

3. vos:sgwyn/suprime/weights/ : weight maps for the above, also as .fz
compressed MEFs. Filenames like: SUPA0000965p.weight.fits.fz

4. vos:sgwyn/suprime/stacks/ : contains stacked images, weight maps and
catalogs. These are very similar to MegaPipe files. Filter is in the
FILTER01 keyword. Like MegaPipe, I would like the images in multiple filters
covering the same patch of sky to be grouped into one CompositeObservation
with many Planes. There are two types of stacks, with filenames like:
SCLA_241.391+16.421.W-J-V.fits or like SCLA.013.157.W-J-V.fits, but have
basically the same headers and grouping.

From a CAOM perspective:


1 observation SUPA0037434
  - raw plane  (calibrationLevel=1)
    - 10 artifacts vos:sgwyn/suprime/images/SUPA0037434[0123456789].fits.fz
      - 1 chunk per artifact
  - calibrated plane (calibrationLevel=2)
    - 1 image artifact vos:sgwyn/suprime/proc/SUPA0037434p.fits.fz
      - 10 chunks per artifact
    - 1 weight artifact vos:sgwyn/suprime/proc/SUPA0037434p.weight.fits.fz

other examples
SUPA0102090
SUPA0122144
SUPA0142581

Stacks:

1 composite observation SCLA_189.232+62.201
  - 1 or more planes: calibrationLevel=3
    - SCLA_189.232+62.201.W-C-IC
    - SCLA_189.232+62.201.W-J-V
    - SCLA_189.232+62.201.W-S-I
    - SCLA_189.232+62.201.W-S-Z

    - each plane has 3 artifacts
      - vos:sgwyn/suprime/stacks/SCLA_189.232+62.201.W-C-IC.fits
        (productType=catalog)
      - vos:sgwyn/suprime/stacks/SCLA_189.232+62.201.W-C-IC.weight.fits.fz
        (productType=weight)
      - vos:sgwyn/suprime/stacks/SCLA_189.232+62.201.W-C-IC.cat
        (productType=catalog)

other examples:
SCLA.134.129.W-J-VR
SCLA.285.288.W-S-R+
SCLA.396.170.W-C-RC
SCLA.652.157.W-J-VR
SCLA_270.000+30.000.W-J-VR

JJ’s ingestion script: https://github.com/ijiraq/caom2maq/blob/master/subaru
/suprimecam2caom2.py

SGw - 09-06-21
Subaru prefers that raw files are not stored at CADC/released.

SG - 15-06-21
All files generated by CADC, at CADC, are DerivedObservations.

"""

import logging

from cadcutils.net import Subject
from caom2 import DataProductType, CalibrationLevel
from caom2 import ProductType, caom_util, Part
from caom2utils import ObsBlueprint, update_artifact_meta
from caom2utils import data_util
from caom2pipe import astro_composable as ac
from caom2pipe import caom_composable as cc
from caom2pipe import manage_composable as mc
from caom2pipe import translate_composable as tc


__all__ = [
    'APPLICATION',
    'COLLECTION',
    'PRODUCER',
    'SubaruName',
    'Telescope',
]


APPLICATION = 'subaru2caom2'
PRODUCER = 'cadc'
COLLECTION = 'SUBARUCADC'

# From SG - 27-05-21
# 0 - centre wavelength
# 1 - width
# units are Angstroms
filter_information = [
    ['I-A-L427', 4260, 257],
    ['I-A-L445', 4442, 244],
    ['I-A-L464', 4637, 269],
    ['I-A-L484', 4845, 282],
    ['I-A-L505', 5060, 287],
    ['I-A-L527', 5261, 320],
    ['I-A-L550', 5497, 350],
    ['I-A-L574', 5764, 348],
    ['I-A-L598', 6005, 376],
    ['I-A-L624', 6233, 378],
    ['I-A-L651', 6500, 410],
    ['I-A-L679', 6784, 429],
    ['I-A-L709', 7076, 413],
    ['I-A-L738', 7364, 402],
    ['I-A-L767', 7677, 445],
    ['I-A-L797', 7969, 458],
    ['I-A-L827', 8249, 423],
    ['I-A-L856', 8569, 412],
    ['N-A-L656', 6567, 202],
    ['N-B-L711', 7119, 116],
    ['N-B-L816', 8149, 168],
    ['N-B-L921', 9182, 188],
    ['W-A-Y', 9984, 633],
    ['W-C-IC', 7955, 1611],
    ['W-C-RC', 6505, 1346],
    ['W-J-B', 4398, 1106],
    ['W-J-V', 5443, 1142],
    ['W-J-VR', 5986, 1952],
    ['W-S-G', 4705, 1468],
    ['W-S-I', 7663, 1723],
    ['W-S-R', 6248, 1587],
    ['W-S-Z', 9157, 1555],
]
FILTER_LOOKUP = {}
for ii in filter_information:
    FILTER_LOOKUP[ii[0]] = {'cw': ii[1], 'fwhm': ii[2]}

# connected=False - don't ask the SVO filter service
filter_cache = ac.FilterMetadataCache(
    repair_filter_lookup=(lambda x: x),
    repair_instrument_lookup=(lambda x: x),
    telescope='SUBARU',
    cache=FILTER_LOOKUP,
    connected=False,
)

vo_client = None


class SubaruName(mc.StorageName):
    """Naming rules:
    - support mixed-case file name storage, and mixed-case obs id values
    - support uncompressed files in storage

    The first StorageInventory attempt, so have no '_archive' member for
    the first try.

    """

    SUBARU_NAME_PATTERN = '*'

    def __init__(self, file_name=None, uri=None, entry=None):
        if file_name is not None:
            self._file_name = file_name
            self.obs_id = self._get_obs_id()
            artifact_uri = mc.build_uri(COLLECTION, file_name, 'cadc')
            self._destination_uris = [artifact_uri]
        if uri is not None:
            scheme, path, file_name = mc.decompose_uri(uri)
            self._file_name = file_name
            self.obs_id = self._get_obs_id()
            if scheme == PRODUCER:
                self._destination_uris = [uri]
            else:
                artifact_uri = mc.build_uri(COLLECTION, file_name, 'cadc')
                self._destination_uris = [artifact_uri]
        self.scheme = PRODUCER
        self._collection = COLLECTION
        self._compression = ''
        self._entry = entry
        self._product_id = self._get_product_id()
        self._file_name = self._file_name.replace('.header', '')
        self._source_names = [entry]
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(self)

    def _get_obs_id(self):
        if self.is_legacy:
            bits = self._file_name.split('.')
            result = '.'.join(kk for kk in bits[:3])
        else:
            result = self._file_name[:11]
        return result

    def _get_product_id(self):
        return SubaruName.remove_extensions(self._file_name)

    @property
    def collection(self):
        return self._collection

    @property
    def file_name(self):
        return self._file_name

    @property
    def file_uri(self):
        """The Artifact URI for the file."""
        return mc.build_uri(
            archive=self._collection,
            file_name=self._file_name,
            scheme=self.scheme,
        )

    @property
    def is_legacy(self):
        return self._file_name.startswith('SCLA')

    def is_valid(self):
        return True

    @property
    def prev(self):
        return f'{self._obs_id}.gif'

    @property
    def thumb(self):
        return f'{self._obs_id}_th.gif'

    @property
    def product_id(self):
        return self._product_id

    @staticmethod
    def remove_extensions(entry):
        return (
            mc.StorageName.remove_extensions(entry)
            .replace('.fz', '')
            .replace('.weight', '')
            .replace('.cat', '')
        )


class Telescope:

    def __init__(self, uri, headers):
        self._uri = uri,
        self._headers = headers
        self._logger = logging.getLogger(self.__class__.__name__)

    def accumulate_bp(self, bp, storage_name):
        """Configure the telescope-specific ObsBlueprint at the CAOM model
        Observation level."""
        self._logger.debug('Begin accumulate_bp.')
        bp.configure_position_axes((1, 2))
        bp.configure_time_axis(3)

        meta_producer = mc.get_version(APPLICATION)

        # observation
        bp.set('Observation.metaProducer', meta_producer)

        bp.set('Observation.algorithm.name', 'Suprime-Cam Legacy Archive')
        bp.set('DerivedObservation.members', {})

        bp.clear('Observation.metaRelease')
        bp.add_fits_attribute('Observation.metaRelease', 'DATE')
        bp.clear('Observation.type')
        bp.add_fits_attribute('Observation.type', 'DATA-TYP')

        bp.set('Observation.environment.photometric', True)
        bp.add_fits_attribute('Observation.environment.seeing', 'IQFINAL')

        bp.set('Observation.instrument.name', 'Suprime-Cam')
        if '.cat' in storage_name.file_uri:
            bp.clear('Observation.instrument.keywords')

        bp.set('Observation.telescope.name', 'Subaru')
        x, y, z = ac.get_geocentric_location('Subaru')
        bp.set('Observation.telescope.geoLocationX', x)
        bp.set('Observation.telescope.geoLocationY', y)
        bp.set('Observation.telescope.geoLocationZ', z)

        # plane
        calibration_level = CalibrationLevel.CALIBRATED
        if storage_name.is_legacy:
            calibration_level = CalibrationLevel.PRODUCT
        bp.set('Plane.calibrationLevel', calibration_level)
        bp.set('Plane.dataProductType', DataProductType.IMAGE)
        bp.set('Plane.metaProducer', meta_producer)

        bp.clear('Plane.dataRelease')
        bp.add_fits_attribute('Plane.dataRelease', 'DATE')
        bp.clear('Plane.metaRelease')
        bp.add_fits_attribute('Plane.metaRelease', 'DATE')

        bp.clear('Plane.metrics.magLimit')
        bp.add_fits_attribute('Plane.metrics.magLimit', 'ML_5SIGA')

        bp.clear('Plane.provenance.lastExecuted')
        bp.add_fits_attribute('Plane.provenance.lastExecuted', 'DATE')
        bp.set('Plane.provenance.producer', 'CADC')
        if storage_name.is_legacy:
            bp.clear('Plane.provenance.name')
            bp.add_fits_attribute('Plane.provenance.name', 'SOFTNAME')
            bp.clear('Plane.provenance.project')
            bp.add_fits_attribute('Plane.provenance.project', 'SOFTAUTH')
            # I'd use this value, but it's not an URL
            # bp.add_fits_attribute('Plane.provenance.reference', 'SOFTINST')
            # SGw 7-09-21
            # For the stacks (SCLA*) everything is https://www.astromatic.net.
            # For the SUPA*p.fits, nothing is https://www.astromatic.net/
            bp.set('Plane.provenance.reference', 'https://www.astromatic.net/')
            bp.clear('Plane.provenance.version')
            bp.add_fits_attribute('Plane.provenance.version', 'SOFTVERS')
        else:
            bp.set('Plane.provenance.name', 'SCLA')

        # artifact
        bp.set('Artifact.metaProducer', meta_producer)
        artifact_product_type = ProductType.SCIENCE
        # SGw 19-01-22 - weight product type for all weight files
        if '.weight' in storage_name.file_uri:
            artifact_product_type = ProductType.WEIGHT
        elif '.cat' in storage_name.file_uri:
            artifact_product_type = ProductType.AUXILIARY
        bp.set('Artifact.productType', artifact_product_type)
        bp.set('Artifact.releaseType', 'data')

        # chunk
        bp.set('Chunk.metaProducer', meta_producer)

        bp.set('Chunk.position.resolution', '_get_position_resolution()')

        bp.set('Chunk.time.axis.axis.ctype', 'TIME')
        bp.set('Chunk.time.axis.axis.cunit', 'd')
        bp.set('Chunk.time.axis.function.naxis', 1)
        bp.set('Chunk.time.axis.function.refCoord.pix', 0.5)
        if storage_name.is_legacy:
            bp.add_fits_attribute(
                'Chunk.time.axis.function.refCoord.val', 'MJD-OBS'
            )
        else:
            bp.set(
                'Chunk.time.axis.function.refCoord.val',
                '_get_time_function_val()',
            )
        bp.clear('Chunk.time.exposure')
        bp.add_fits_attribute('Chunk.time.exposure', 'EXPTIME')
        bp.set('Chunk.time.timesys', 'UTC')

        self._logger.debug('Done accumulate_bp.')

    def update(self, observation, subaru_name, file_info):
        """Called to fill multiple CAOM model elements and/or attributes (an n:n
        relationship between TDM attributes and CAOM attributes). Must have this
        signature for import_module loading and execution.

        :param observation A CAOM Observation model instance.
        :param subaru_name SubaruName instance.
        :param file_info cadcdata.FileInfo instance
        """
        self._logger.debug('Begin update.')

        self._update_observation_metadata(observation, subaru_name)
        min_seeing = None
        if (
            observation.environment is not None
            and observation.environment.seeing is not None
        ):
            min_seeing = observation.environment.seeing
        for plane in observation.planes.values():
            if (
                '.weight' not in subaru_name.file_name
                and '.cat' not in subaru_name.file_name
                and subaru_name.product_id == plane.product_id
            ):
                if subaru_name.is_legacy and plane.provenance is not None:
                    cc.update_plane_provenance_single(
                        plane,
                        self._headers,
                        'HISTORY',
                        'SUBARUCADC',
                        _repair_history_provenance_value,
                        observation.observation_id,
                    )
                    if len(self._headers) > 0:
                        min_seeing = mc.minimize_on_keyword(
                            min_seeing,
                            mc.get_keyword(self._headers, 'IQFINAL'),
                        )
                else:
                    self._update_plane_provenance_inputs(plane)
            for artifact in plane.artifacts.values():
                if artifact.uri != subaru_name.file_uri:
                    self._logger.debug(
                        f'Skipping artifact {artifact.uri} as storage name is '
                        f'{subaru_name.file_uri}'
                    )
                    continue
                update_artifact_meta(artifact, file_info)
                if (
                    plane.meta_release is not None
                        and plane.data_release is None
                ):
                    plane.data_release = plane.meta_release
                for part in artifact.parts.values():
                    for chunk in part.chunks:
                        chunk.time_axis = None
                        if len(self._headers) > 0:
                            filter_name = mc.get_keyword(
                                self._headers, 'FILTER01'
                            )
                            if filter_name is not None:
                                filter_name = filter_name.replace(
                                    '+', ''
                                ).strip()
                                cc.build_chunk_energy_range(
                                    chunk,
                                    filter_name,
                                    FILTER_LOOKUP.get(filter_name),
                                )
                self._update_weight_artifact(observation, plane, subaru_name)

        if observation.environment is not None:
            observation.environment.seeing = min_seeing
        if subaru_name.is_legacy:
            cc.update_observation_members(observation)
        self._logger.debug('Done update.')
        return observation

    def _get_position_resolution(self, ext):
        # 04-01-22 - SGw
        # it is ok if IQFINAL is an empty string
        return mc.to_float(self._headers[ext].get('IQFINAL'))

    def _get_time_function_val(self, ext):
        date_obs = self._headers[ext].get('DATE-OBS')
        ut_str = self._headers[ext].get('UT-STR')
        start_time = None
        if date_obs is not None and ut_str is not None:
            temp = f'{date_obs}T{ut_str}'
            start_time = ac.get_datetime(temp).value
        return start_time

    def _update_observation_metadata(self, obs, subaru_name):
        """
        Why this method exists:

        There are files that have almost no metadata in the primary HDU, but
        all the needed metadata in subsequent HDUs.

        It's not possible to apply extension numbers for non-chunk blueprint
        entries, so that means that to use the information captured in the
        blueprint, the header that's provided must be manipulated instead.

        :param obs:
        :para subaru_name:
        :return:
        """
        self._logger.debug(
            f'Begin _update_observation_metadata for {obs.observation_id}'
        )
        # headers is not None => .cat files
        if (
            self._headers is not None
            and len(self._headers) > 1
            and not subaru_name.is_legacy
        ):
            from urllib.parse import urlparse
            bits = urlparse(subaru_name.source_names[0])
            if bits.scheme == '':
                unmodified_headers = data_util.get_local_file_headers(
                    subaru_name.source_names[0]
                )
            else:
                # assume default file locations and service end-points
                subject = Subject(certificate='/usr/src/app/cadcproxy.pem')
                client = data_util.StorageClientWrapper(
                    subject,
                    resource_id='ivo://cadc.nrc.ca/uvic/minoc'
                )
                unmodified_headers = client.get_head(subaru_name.file_uri)

            original_headers = self._headers
            self._headers = unmodified_headers[1:]
            bp = ObsBlueprint(instantiated_class=self)
            self.accumulate_bp(bp, subaru_name)
            tc.add_headers_to_obs_by_blueprint(
                obs,
                unmodified_headers[1:],
                bp,
                subaru_name.file_uri,
                subaru_name.product_id,
            )
            self._headers = original_headers
        self._logger.debug('End _update_observation_metadata.')

    def _update_plane_provenance_inputs(self, plane):
        """
        Predict provenance inputs for level 2 calibration
        :param plane:
        :return:
        """
        if plane.provenance is not None:
            # this behaviour is consistent with existing SUBARU raw records in
            # CAOM2
            ignore, plane_uri = cc.make_plane_uri(
                plane.product_id.replace('p', '0'),
                plane.product_id.replace('p', 'X'),
                'SUBARU',
            )
            plane.provenance.inputs.add(plane_uri)

    def _update_weight_artifact(self, observation, plane, subaru_name):
        """Use the same WCS for the weight artifact as for the 'p' artifact.
        Because cutouts.
        """
        self._logger.debug(
            f'Begin _update_weight_artifact for {observation.observation_id}'
        )
        if subaru_name.is_legacy:
            # only applicable to 'p' files
            return

        if 'weight' in subaru_name.file_name:
            w_artifact_key = subaru_name.file_uri
            p_artifact_key = subaru_name.file_uri.replace('.weight', '')
        else:
            p_artifact_key = subaru_name.file_uri
            w_artifact_key = subaru_name.file_uri.replace(
                '.fits', '.weight.fits'
            )

        features = mc.Features()
        features.supports_latest_caom = True

        if w_artifact_key in plane.artifacts.keys():
            w_artifact = plane.artifacts[w_artifact_key]

            if p_artifact_key in plane.artifacts.keys():
                # use the WCS generated from the p file for the
                # weight file as well
                p_artifact = plane.artifacts[p_artifact_key]

                for part in p_artifact.parts.values():
                    w_artifact.parts.add(cc.copy_part(part))
                    for chunk in part.chunks:
                        w_artifact.parts[
                            part.name
                        ].chunks.append(cc.copy_chunk(chunk, features))
                w_artifact.meta_producer = p_artifact.meta_producer
            else:
                # remove the WCS generated from the weight file as it
                # fails validation
                w_artifact.parts = caom_util.TypedOrderedDict(Part, )
        self._logger.debug('End _update_weight_artifact')


def _repair_history_provenance_value(value, obs_id):
    logging.debug(f'Begin _repair_history_provenance_value for {obs_id}')
    results = []
    # HISTORY headers with provenance:
    # HISTORY  input image SUPA0010787
    # HISTORY  input image SUPA0010788
    # HISTORY  input image SUPA0010789
    # HISTORY  input image SUPA0010791
    #
    # SGw 20-07-21
    # The inputs to the planes of the stacks are planes from the individual
    # images which end in "p". Basically, I want people to be able to click
    # on an input plane and be taken to the record for that plane. If that's
    # what's happening already, that's fine.
    #
    # SGo - add a 'p' after the 7 digits that identify an observation.
    if 'input image' in str(value):
        for entry in value:
            if 'input image' in entry:
                temp = str(entry).split('input image ')
                prov_file_id = f'{temp[1].strip()}p'
                sn = SubaruName(file_name=prov_file_id)
                # 0 - observation
                # 1 - plane
                # product_ids for 'p' files need to be handled correctly
                #
                results.append([sn.obs_id, sn.product_id])
    logging.debug(f'End _repair_history_provenance_value')
    return results
