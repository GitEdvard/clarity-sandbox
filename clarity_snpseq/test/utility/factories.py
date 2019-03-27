from clarity_ext.domain.analyte import Analyte
from clarity_ext.domain.container import Container
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.library_dilution_start import Extension as ExtensionLib
from clarity_ext_scripts.dilution.factor_dilution_start import Extension as ExtensionFactor
from clarity_ext_scripts.clustering.driverfile import Extension as ExtensionClustering
from clarity_ext_scripts.dilution.fixed_dilution_start import Extension as ExtensionFixed
from clarity_ext_scripts.clustering.driverfile import Extension as ExtensionClusterDriverfile
from clarity_snpseq.test.utility.scripts_for_testing.fixed_with_end_sort_order import Extension as FixedWithEndSortOrder
from clarity_ext_scripts.fragment_analyzer.analyze_quality_table import Extension as AnalyzeQualityTable
from clarity_ext_scripts.qpcr.analyze_qpcr_resultfile import Extension as AnalyzeQpcrResultfile
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderConc
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderFactor
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderFixed
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder


class ExtensionBuilderFactory:
    @classmethod
    def create_with_dna_extension(cls, context_builder=None):
        return ExtensionBuilderConc(ExtensionDna, source_type=Analyte, target_type=Analyte,
                                   context_builder=context_builder)

    @classmethod
    def create_with_library_dil_extension(cls, context_builder=None,
                                          target_container_type=Container.CONTAINER_TYPE_96_WELLS_PLATE,
                                          source_sorted_from_first=True):
        return ExtensionBuilderConc(ExtensionLib, source_type=Analyte, target_type=Analyte,
                                   context_builder=context_builder,
                                   target_container_type=target_container_type,
                                    source_sorted_from_first=source_sorted_from_first)

    @classmethod
    def create_with_factor_extension(cls, context_builder=None):
        return ExtensionBuilderFactor(ExtensionFactor, source_type=Analyte, target_type=Analyte,
                                      context_builder=context_builder)

    @classmethod
    def create_with_fixed_extension(cls, context_builder=None):
        return ExtensionBuilderFixed(ExtensionFixed, source_type=Analyte, target_type=Analyte,
                                     context_builder=context_builder)

    @classmethod
    def create_with_fixed_end_sort_order(cls, context_builder=None):
        return ExtensionBuilderFixed(FixedWithEndSortOrder, source_type=Analyte, target_type=Analyte,
                                     context_builder=context_builder)

    @classmethod
    def create_with_cluster_driverfile_extension(cls, context_builder=None):
        return ExtensionBuilderFixed(ExtensionClusterDriverfile, source_type=Analyte, target_type=Analyte,
                                     context_builder=context_builder)

    @classmethod
    def create_with_clustering_extension(cls, context_builder=None):
        return ExtensionBuilderConc(ExtensionClustering, source_type=Analyte, target_type=Analyte,
                                          context_builder=context_builder)

    @classmethod
    def create_with_read_result_file_type(cls, extension_type, context_builder=None):
        """
        User has to provide extension type
        """
        return ExtensionBuilder(extension_type,
                                source_type=Analyte, target_type=Analyte,
                                context_builder=context_builder)
