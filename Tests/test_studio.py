from unittest import TestCase
from Helpers.configuration_manager import StudioConfiguration
from Helpers.converter import Converter
from Helpers.merger import Merger
from studio import Studio
from mock import MagicMock, Mock, call


class TestStudio(TestCase):
    sample_xcassets_dir = "sample_xcassets_dir"
    sample_raw_assets_dir = "sample_raw_assets_dir"
    sample_generated_assets_dir = "sample_generated_assets_dir"
    sample_merge_with = True

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_if_all_configuration_properties_are_passed(self):
        configuration = StudioConfiguration()

        configuration.xcassets_dir = self.sample_xcassets_dir
        configuration.raw_assets = self.sample_raw_assets_dir
        configuration.generated_assets_dir = self.sample_generated_assets_dir
        configuration.merge_with_xcassets = self.sample_merge_with

        merger = Merger()
        converter = Converter()
        studio = Studio(merger=merger, converter=converter, configuration=configuration)

        self.assertTrue(studio.merger.default_xcasset_dir == self.sample_xcassets_dir)
        self.assertTrue(studio.merger.source_assets_dir == self.sample_generated_assets_dir)

        self.assertTrue(studio.converter.inputDir == self.sample_raw_assets_dir)
        self.assertTrue(studio.converter.outputDir == self.sample_generated_assets_dir)

    def test_if_converter_and_merger_methods_are_called_in_order(self):
        configuration = StudioConfiguration()
        configuration.merge_with_xcassets = True

        merger = Mock()
        converter = Mock()

        studio = Studio(merger=merger, converter=converter, configuration=configuration)
        studio.launch()

        converter.convert.assert_called_once_with()
        merger.merge.assert_called_once_with()

    def test_respect_merge_with_xcassets_flag(self):
        configuration = StudioConfiguration()
        configuration.merge_with_xcassets = False

        merger = Mock()
        converter = Mock()
        studio = Studio(merger=merger, converter=converter, configuration=configuration)
        studio.launch()

        converter.convert.assert_called_once_with()
        self.assertEqual(merger.merge.call_count, 0)
