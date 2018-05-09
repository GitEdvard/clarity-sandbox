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
