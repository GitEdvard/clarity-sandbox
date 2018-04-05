from clarity_ext.domain import *
from clarity_ext.service.dilution.service import *


class FakeArtifactRepository:
    """
    Repository of analytes and containers
    Methods that links analyes and container together
    """
    def __init__(self, create_well_order=Container.DOWN_FIRST):
        self.default_source = "source"
        self.default_target = "target"
        self.containers = dict()

        self.create_container(self.default_source, True)
        self.create_container(self.default_target, False)
        self.well_enumerator = self.containers[self.default_source].enumerate_wells(create_well_order)
        self.pairs = list()

    def container_by_name(self, container_name):
        return self.containers[container_name]

    def set_default_containers(self, source_postfix, target_postfix):
        self.default_source = "source{}".format(source_postfix)
        self.default_target = "target{}".format(target_postfix)

    def create_container(self, container_id, is_source):
        container = Container(container_type=Container.CONTAINER_TYPE_96_WELLS_PLATE,
                              container_id=container_id, name=container_id, is_source=is_source)
        self.containers[container_id] = container
        return container

    def get_container_by_name(self, container_name, is_source):
        """Returns a container by name, creating it if it doesn't exist yet"""
        if container_name not in self.containers:
            self.containers[container_name] = self.create_container(container_name, is_source)
        return self.containers[container_name]

    def create_analyte(self, is_input, partial_name, analyte_type=Analyte, samples=None, id=None):
        name = "{}-{}".format("in" if is_input else "out", partial_name)
        id = id or name
        project = Project("IntegrationTest")
        if not samples:
            samples = [Sample("S_" + name, "S_" + name, project)]
        ret = analyte_type(api_resource=None, is_input=is_input, id=id, name=name, samples=samples)
        return ret

    def create_pair(self, pos_from=None, pos_to=None, source_container_name=None, target_container_name=None,
                    source_type=Analyte, target_type=Analyte, source_id=None, target_id=None):
        if source_container_name is None:
            source_container_name = self.default_source
        if target_container_name is None:
            target_container_name = self.default_target

        source_container = self.get_container_by_name(source_container_name, True)
        target_container = self.get_container_by_name(target_container_name, False)

        if pos_from is None:
            well = self.well_enumerator.next()
            pos_from = well.position
        if pos_to is None:
            pos_to = pos_from

        name = "FROM:{}".format(pos_from)
        pair = ArtifactPair(self.create_analyte(True, name, source_type, id=source_id),
                            self.create_analyte(False, name, target_type, id=target_id))
        source_container.set_well_update_artifact(pos_from, artifact=pair.input_artifact)
        target_container.set_well_update_artifact(pos_to, artifact=pair.output_artifact)
        self.pairs.append(pair)
        return pair


class DilutionAnalyteCreator:
    """
    Use DilutionPairBuilder instead
    """
    def __init__(self, concentration_ref):
        self.concentration_unit = DilutionSettings._parse_conc_ref(concentration_ref)
        assert self.concentration_unit is not None
        self.fake_artifact_repo = FakeArtifactRepository()

    def create_dilution_pair(self, conc1, vol1, conc2, vol2, pos_from=None, pos_to=None,
                             source_type=Analyte, target_type=Analyte,
                             source_container_name=None, target_container_name=None):
        """Creates an analyte pair ready for dilution"""
        pair = self.fake_artifact_repo.create_pair(pos_from, pos_to,
                                source_type=source_type, target_type=target_type,
                                source_container_name=source_container_name,
                                target_container_name=target_container_name)
        concentration_unit = DilutionSettings.concentration_unit_to_string(self.concentration_unit)
        conc_source_udf = "Conc. Current ({})".format(concentration_unit)
        conc_target_udf = "Target conc. ({})".format(concentration_unit)
        pair.input_artifact.udf_map = UdfMapping({conc_source_udf: conc1,
                                                  "Current sample volume (ul)": vol1})
        pair.output_artifact.udf_map = UdfMapping({conc_source_udf: conc1,
                                                   "Current sample volume (ul)": vol1,
                                                   "Target vol. (ul)": vol2,
                                                   conc_target_udf: conc2,
                                                   "Dil. calc target vol": None,
                                                   "Dil. calc target conc.": None,
                                                   "Dil. calc source vol": None})
        return pair

    def create_pair(self, pos_from=None, pos_to=None, source_container_name=None, target_container_name=None,
                    source_type=Analyte, target_type=Analyte):
        return self.fake_artifact_repo.create_pair(pos_from, pos_to, source_container_name, target_container_name,
                                                   source_type, target_type)

    def create_pooled_pairs(self, pool_size):
        """
        Creates n pairs that are pooled, i.e. there are n analytes that are mapped to m analytes, where m < n.

        The wells in the source container are [A1, B2, ...]

        NOTE: Currently we model the REST API interface when it comes to pools, but it would probably
        be an improvement to introduce new domain objects, Pool and PoolInput that would
        be used in this case to simplify the use of the API.
        """
        source_analytes = list()
        for i in range(1, pool_size + 1):
            source_container = self.fake_artifact_repo.get_container_by_name("source{}".format(i), True)
            name = "analyte{}".format(i)
            analyte = self.fake_artifact_repo.create_analyte(True, name, Analyte)
            source_container.append(analyte)
            source_analytes.append(analyte)

        # Now create one analyte for the output, but containing all the input samples
        samples = [analyte.sample() for analyte in source_analytes]
        target_analyte = self.fake_artifact_repo.create_analyte(False, "analyte1", samples=samples)
        target_container = self.fake_artifact_repo.get_container_by_name(
            self.fake_artifact_repo.default_target, False)
        target_container.append(target_analyte)

        for source_analyte in source_analytes:
            yield ArtifactPair(source_analyte, target_analyte)