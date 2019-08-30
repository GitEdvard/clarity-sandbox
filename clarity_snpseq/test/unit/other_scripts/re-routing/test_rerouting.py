import unittest
import xml.etree.ElementTree as ET
from collections import namedtuple
from clarity_ext.utils import single
from clarity_ext.domain.shared_result_file import SharedResultFile
from clarity_ext_scripts.general.route_artifacts import Extension as RerouteArtifacts
from clarity_snpseq.test.utility.higher_level_builders.reroute_extension_builder import RerouteExtensionBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class TestRerouting(unittest.TestCase):
    def test_reroute__with_one_approved_sample__one_entry_to_http_post(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(1, len(builder.post_cache))

    def test_reroute__with_one_approved_and_one_shared_resultfile__one_entry_to_http_post(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.create_shared_result_file_proxy(builder)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(1, len(builder.post_cache))

    def test_reroute__with_one_nothing_filled_in__no_entry_in_http_post(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='', workflow_name='', confirm_workflow_move=False)
        self.create_shared_result_file_proxy(builder)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(0, len(builder.post_cache))

    def test_reroute__with_one_approved_sample__stage_uri_in_xml_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        post_command = ET.fromstring(builder.post_cache['route.artifacts'])
        assign_node = single(post_command.findall('assign'))
        self.assertEqual('a_step_uri', assign_node.get('stage-uri'))

    def test_reroute__with_one_approved_sample__artifact_uri_in_xml_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        post_command = ET.fromstring(builder.post_cache['route.artifacts'])
        assign_node = single(post_command.findall('assign'))
        artifact_node = single(assign_node.findall('artifact'))
        self.assertEqual('artifacts.analyte1', artifact_node.get('uri'))

    def test_reroute__with_one_approved_sample__header_in_xml_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        post_command = ET.fromstring(builder.post_cache['route.artifacts'])
        self.assertEqual('{http://genologics.com/ri/routing}routing', post_command.tag)

    def test_reroute__with_two_approved_samples_different_workflows__step_uris_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.create_analyte_with_user_settings(
            'analyte2', builder,
            step_name='another_step_name', workflow_name='another_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')
        self.add_available_step_and_workflows(
            builder, step_name='another_step_name', step_uri='another_step_uri',
            workflow_name='another_workflow_name', workflow_uri='another_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        post_command = ET.fromstring(builder.post_cache['route.artifacts'])
        assign_nodes = post_command.findall('assign')
        self.assertEqual(2, len(assign_nodes))
        for node in assign_nodes:
            if node.find('artifact').get('uri') == 'artifacts.analyte1':
                node1 = node
            if node.find('artifact').get('uri') == 'artifacts.analyte2':
                node2 = node
        self.assertEqual('a_step_uri', node1.get('stage-uri'))
        self.assertEqual('another_step_uri', node2.get('stage-uri'))

    def test_reroute__with_two_approved_samples_same_workflows__step_uris_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.create_analyte_with_user_settings(
            'analyte2', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=True)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')
        self.add_available_step_and_workflows(
            builder, step_name='another_step_name', step_uri='another_step_uri',
            workflow_name='another_workflow_name', workflow_uri='another_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        post_command = ET.fromstring(builder.post_cache['route.artifacts'])
        assign_nodes = post_command.findall('assign')
        self.assertEqual(2, len(assign_nodes))
        for node in assign_nodes:
            if node.find('artifact').get('uri') == 'artifacts.analyte1':
                node1 = node
            if node.find('artifact').get('uri') == 'artifacts.analyte2':
                node2 = node
        self.assertEqual('a_step_uri', node1.get('stage-uri'))
        self.assertEqual('a_step_uri', node2.get('stage-uri'))

    def test_reroute__with_one_dismissed_sample__no_http_post_command(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', confirm_workflow_move=False)
        self.add_available_step_and_workflows(
            builder, step_name='a_step_name', step_uri='a_step_uri',
            workflow_name='a_workflow_name', workflow_uri='a_workflow_uri')

        # Act
        builder.extension.execute()

        # Assert
        self.assertEqual(0, len(builder.post_cache))

    def add_available_step_and_workflows(self, builder, step_name, step_uri, workflow_name, workflow_uri):
        workflow_configuration_entry = {'status': 'ACTIVE', 'uri': workflow_uri, 'name': workflow_name}
        builder.add_entry_for_available_workflows(workflow_configuration_entry, 'configuration', 'workflows')
        stage_entry = {'name': step_name, 'uri': step_uri}
        builder.add_entry_for_available_stages(stage_entry, workflow_uri)

    def create_analyte_with_user_settings(
            self, artifact_name, rerouting_builder, step_name, workflow_name, confirm_workflow_move):
        pair_builder = PairBuilderBase(FakeArtifactRepository())
        stage = SingleWorkflowStage(uri='current_workflow_uri')
        workflow_stage = WorkflowStages(stage=stage, status='IN_PROGRESS', workflow='')
        pair_builder.with_attribute_input('workflow_stages_and_statuses', [workflow_stage])
        pair_builder.with_output_udf('Confirm Workflow Move', confirm_workflow_move)
        pair_builder.with_output_udf('New Workflow (from holding)', workflow_name)
        pair_builder.with_output_udf('New Step (from holding)', step_name)
        rerouting_builder.with_artifact_pair(artifact_name, pair_builder)

    def create_shared_result_file_proxy(self, rerouting_builder):
        pair_builder = PairBuilderBase(FakeArtifactRepository())
        pair_builder.target_type = SharedResultFile
        rerouting_builder.with_artifact_pair('shared result file', pair_builder)

    def test_xml(self):
        def get_workflows_raw():
            contents = {'status': 'ACTIVE', 'uri': 'a_workflow_uri', 'name': 'a_workflow_name'}
            root = ET.Element('root')
            ET.SubElement(root, 'workflow', contents)
            for workflow in root:
                yield tuple(workflow.attrib.get(attrib) for attrib in ["status", "uri", "name"])
        workflows = {name.lower(): uri for status, uri, name in get_workflows_raw() if status == "ACTIVE"}
        print(workflows)

        self.assertEqual(1, len(workflows))

    def test_zip(self):
        def myfunc(*segments):
            return '.'.join(segments)
        self.assertEqual('a.b', myfunc('a', 'b'))


class WorkflowStages(namedtuple('workflow_stages', ['stage', 'status', 'workflow'])):
    pass


class SingleWorkflowStage(namedtuple('single_workflow_stage', ['uri'])):
    pass
