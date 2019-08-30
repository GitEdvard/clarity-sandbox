import unittest
import xml.etree.ElementTree as ET
from collections import namedtuple
from clarity_ext_scripts.fu.fu_example_rerouting import Extension as RerouteArtifacts
from clarity_snpseq.test.utility.higher_level_builders.reroute_extension_builder import RerouteExtensionBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class TestFuRerouting(unittest.TestCase):
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
        pair_builder.with_output_udf('New Workflow (from FU)', workflow_name)
        pair_builder.with_output_udf('New Step (from FU)', step_name)
        rerouting_builder.with_artifact_pair(artifact_name, pair_builder)


class WorkflowStages(namedtuple('workflow_stages', ['stage', 'status', 'workflow'])):
    pass


class SingleWorkflowStage(namedtuple('single_workflow_stage', ['uri'])):
    pass
