from clarity_ext.domain.analyte import Analyte
from clarity_ext_scripts.dilution.dna_dilution_start import Extension as ExtensionDna
from clarity_ext_scripts.dilution.factor_dilution_start import Extension as ExtensionFactor
from clarity_ext_scripts.clustering.driverfile import Extension as ExtensionClustering
from clarity_ext_scripts.dilution.fixed_dilution_start import Extension as ExtensionFixed
from clarity_ext_scripts.fragment_analyzer.analyze_quality_table import Extension as AnalyzeQualityTable
from clarity_ext_scripts.qpcr.analyze_qpcr_resultfile import Extension as AnalyzeQpcrResultfile
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderDna
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderFactor
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilderFixed
from clarity_snpseq.test.utility.extension_builders import ExtensionBuilder


class ExtensionBuilderFactory:
    @classmethod
    def create_with_dna_extension(cls, context_builder=None):
        return ExtensionBuilderDna(ExtensionDna, source_type=Analyte, target_type=Analyte,
                                   context_builder=context_builder)

    @classmethod
    def create_with_factor_extension(cls, context_builder=None):
        return ExtensionBuilderFactor(ExtensionFactor, source_type=Analyte, target_type=Analyte,
                                      context_builder=context_builder)

    @classmethod
    def create_with_fixed_extension(cls, context_builder=None):
        return ExtensionBuilderFixed(ExtensionFixed, source_type=Analyte, target_type=Analyte,
                                     context_builder=context_builder)

    @classmethod
    def create_with_clustering_extension(cls, context_builder=None):
        return ExtensionBuilderDna(ExtensionClustering, source_type=Analyte, target_type=Analyte,
                                          context_builder=context_builder)

    @classmethod
    def create_with_read_result_file_type(cls, extension_type, context_builder=None):
        """
        User has to provide extension type
        """
        return ExtensionBuilder(extension_type,
                                source_type=Analyte, target_type=Analyte,
                                context_builder=context_builder)
