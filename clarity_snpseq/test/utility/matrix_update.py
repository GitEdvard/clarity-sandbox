from itertools import chain
from clarity_ext.domain.udf import UdfMapping


class MatrixUpdate:
    """
    Option to update a context to a specified state before the integration test is run.
    Context state is updated by either update_matrix_by_limsid, or update_matrix_by_artnames,
    or both.

    Format for update_matrix_by_limsid:
    [
        ('limsid', 'field name', field value),
        ...
    ]

    Format for update_matrix_by_artnames:
    [
        ('input/output ref', 'artifact name', 'field name', field value),
        ...
    ]
    with input/output ref either of:
        'input'
        'output'
    """

    def __init__(self, update_matrix_by_limsid=None, update_matrix_by_artnames=None,
                 artifact_service=None, clarity_service=None):
        self._update_matrix_by_limsid = update_matrix_by_limsid
        self._update_matrix_by_artnames = update_matrix_by_artnames
        self._update_matrix = None
        # artifact service is not defined in outer scope until the prepare
        # method is called
        self.artifact_service = artifact_service
        self.clarity_service = clarity_service

    def update_matrix(self):
        self.artifact_service = self.artifact_service
        artifacts = chain(self.artifact_service.all_input_artifacts(),
                          self.artifact_service.all_output_artifacts())
        artifact_dict = {artifact.id: artifact for artifact in artifacts}
        self._check_artifacts_exists(artifact_dict)
        update_queue = []
        default_udf_map = self._udf_map()
        for update_row in self._get_update_matrix():
            art_id = update_row[0]
            udf_name = update_row[1]
            value = update_row[2]
            artifact = artifact_dict[art_id]
            self._add_to_map(artifact, default_udf_map)
            artifact.udf_map[udf_name] = value
            update_queue.append(artifact)

        self.clarity_service.update(update_queue, ignore_commit=False)

    def _add_to_map(self, artifact, default_map):
        for key in default_map:
            try:
                artifact.udf_map.add(key, default_map[key])
            except ValueError:
                pass

    def _udf_map(self):
        ret = dict()
        for update_row in self._get_update_matrix():
            udf_name = update_row[1]
            ret[udf_name] = None
        return ret

    def _check_artifacts_exists(self, artifact_dict):
        for update_row in self._get_update_matrix():
            art_id = update_row[0]
            if art_id not in artifact_dict:
                raise ArtifactsNotFound(
                    "Given lims-id is not matching artifacts in step ({})".format(art_id))

    def _get_update_matrix(self):
        if not self._update_matrix:
            matrix = self._transform_update_matrix_by_artnames(
                update_matrix_by_artnames=self._update_matrix_by_artnames)
            if not matrix:
                matrix = []
            if not self._update_matrix_by_limsid:
                self._update_matrix_by_limsid = []
            self._update_matrix = self._update_matrix_by_limsid + matrix
        return self._update_matrix

    def _transform_update_matrix_by_artnames(self, update_matrix_by_artnames=None):
        if not update_matrix_by_artnames:
            return
        update_matrix_by_limsid = []
        for row in update_matrix_by_artnames:
            artifact = self._fetch_artifact(
                input_output_ref=row[0], artifact_name=row[1])
            new_row = ("{}".format(artifact.id), row[2], row[3])
            update_matrix_by_limsid.append(new_row)
        return update_matrix_by_limsid

    def _fetch_artifact(self, input_output_ref=None, artifact_name=None):
            if input_output_ref == 'input':
                artifacts = self.artifact_service.all_input_artifacts()
            elif input_output_ref == 'output':
                artifacts = self.artifact_service.all_output_artifacts()
            else:
                raise ValueError(
                    "Not recognized key word in matrix, should be either ''input'' or ''output'', {}".format(row[0]))
            arts = [art for art in artifacts if art.name == artifact_name]
            return arts[0]


class ArtifactsNotFound(Exception):
    pass
