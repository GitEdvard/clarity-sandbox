import unittest
from unittest import skip
import xml.etree.ElementTree as ET
from collections import namedtuple
from clarity_ext.utils import single
from clarity_ext.domain.shared_result_file import SharedResultFile
from clarity_ext_scripts.aggregate.route_libraries import Extension as RerouteArtifacts
from clarity_snpseq.test.utility.higher_level_builders.reroute_extension_builder import RerouteExtensionBuilder
from clarity_snpseq.test.utility.pair_builders import PairBuilderBase
from clarity_snpseq.test.utility.fake_artifacts import FakeArtifactRepository


class TestAggregateRerouting(unittest.TestCase):
    def test_reroute__with_two_samples_different_workflows__step_uris_ok(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_with_user_settings(
            'analyte1', builder,
            step_name='a_step_name', workflow_name='a_workflow_name', conc_status='Failed')
        self.create_analyte_with_user_settings(
            'analyte2', builder,
            step_name='another_step_name', workflow_name='another_workflow_name', conc_status='Failed')
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

    @skip('Wait, I want input artifact for shared result file to be fetched from previously added')
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

    def test_reroute__with_udfs_for_new_location_lacking__no_entry_in_http_post(self):
        # Arrange
        builder = RerouteExtensionBuilder()
        builder.create(RerouteArtifacts)
        self.create_analyte_without_new_workflow_udfs('analyte1', builder)
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

    def create_analyte_without_new_workflow_udfs(self, artifact_name, rerouting_builder):
        pair_builder = PairBuilderBase(FakeArtifactRepository())
        stage = SingleWorkflowStage(uri='current_workflow_uri')
        workflow_stage = WorkflowStages(stage=stage, status='IN_PROGRESS', workflow='')
        pair_builder.with_attribute_input('workflow_stages_and_statuses', [workflow_stage])
        pair_builder.with_input_udf('Initial qPCR conc. status', 'Passed')
        rerouting_builder.with_artifact_pair(artifact_name, pair_builder)

    def create_analyte_with_user_settings(
            self, artifact_name, rerouting_builder, step_name, workflow_name, conc_status):
        pair_builder = PairBuilderBase(FakeArtifactRepository())
        stage = SingleWorkflowStage(uri='current_workflow_uri')
        workflow_stage = WorkflowStages(stage=stage, status='IN_PROGRESS', workflow='')
        pair_builder.with_attribute_input('workflow_stages_and_statuses', [workflow_stage])
        pair_builder.with_input_udf('New Workflow (from aggr.)', workflow_name)
        pair_builder.with_input_udf('New Step (from aggr.)', step_name)
        pair_builder.with_input_udf('Initial qPCR conc. status', conc_status)
        rerouting_builder.with_artifact_pair(artifact_name, pair_builder)

    def create_shared_result_file_proxy(self, rerouting_builder):
        pair_builder = PairBuilderBase(FakeArtifactRepository())
        pair_builder.target_type = SharedResultFile
        rerouting_builder.with_artifact_pair('shared result file', pair_builder)


class WorkflowStages(namedtuple('workflow_stages', ['stage', 'status', 'workflow'])):
    pass


class SingleWorkflowStage(namedtuple('single_workflow_stage', ['uri'])):
    pass
