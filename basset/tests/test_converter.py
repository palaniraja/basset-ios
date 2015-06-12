import os
import shutil
import tempfile
from unittest import TestCase

from wand.image import Image

from basset.exceptions import *
from basset.helpers.converter import Converter


class TestConverter(TestCase):
    temp_dir_path = ""
    converter_tests_resource_path = "converter"
    converter_output_tests_resource_path = "converterOutput"
    script_root_dir_path = ""

    @classmethod
    def setUpClass(cls):
        TestConverter.script_root_dir_path = os.getcwd()

    @classmethod
    def tearDownClass(cls):
        os.chdir(TestConverter.script_root_dir_path)

    def setUp(self):
        self.temp_dir_path = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.temp_dir_path, self.converter_output_tests_resource_path))
        shutil.copytree(os.path.join(TestConverter.script_root_dir_path, "basset/tests/Resources/tests_converter"),
                        os.path.join(self.temp_dir_path, self.converter_tests_resource_path))
        os.chdir(self.temp_dir_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir_path)

    def test_set_up(self):
        def assert_valid_eps_file(test_file_path):
            self.assertTrue(os.path.isfile(test_file_path))
            self.assertEqual(Image(filename=test_file_path).size, (100, 100))
            self.assertEqual(Image(filename=test_file_path).format, "EPT")

        for i in range(1, 3):
            assert_valid_eps_file(
                os.path.join(self.converter_tests_resource_path, "convert_test", "test-0" + str(i) + ".eps"))

        assert_valid_eps_file(
            os.path.join(self.converter_tests_resource_path, "convert_test", "subfolder", "test-04.eps"))
        assert_valid_eps_file(
            os.path.join(self.converter_tests_resource_path, "convert_test", "subfolder", "subsubfolder",
                         "test-05.eps"))

    def assert_valid_png_file(self, test_file_path, size):
        self.assertTrue(os.path.isfile(test_file_path))
        self.assertEqual(Image(filename=test_file_path).size, size)
        self.assertEqual(Image(filename=test_file_path).format, "PNG")

    def test_convert(self):
        converter = Converter()
        converter.inputDir = os.path.join(self.converter_tests_resource_path, "convert_test")
        converter.outputDir = self.converter_output_tests_resource_path
        converter.convert()

        for i in range(1, 3):
            test_file_path_1x = os.path.join(self.converter_output_tests_resource_path, "test-0" + str(i) + ".png")
            test_file_path_2x = os.path.join(self.converter_output_tests_resource_path, "test-0" + str(i) + "@2x.png")
            test_file_path_3x = os.path.join(self.converter_output_tests_resource_path, "test-0" + str(i) + "@3x.png")

            self.assert_valid_png_file(test_file_path=test_file_path_1x, size=(100, 100))
            self.assert_valid_png_file(test_file_path=test_file_path_2x, size=(200, 200))
            self.assert_valid_png_file(test_file_path=test_file_path_3x, size=(300, 300))

        self.assert_valid_png_file(os.path.join(self.converter_output_tests_resource_path, "subfolder", "test-04.png"),
                                   (100, 100))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", "test-04@2x.png"),
            (200, 200))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", "test-04@3x.png"),
            (300, 300))

        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", "subsubfolder", "test-05.png"),
            (100, 100))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", "subsubfolder", "test-05@2x.png"),
            (200, 200))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", "subsubfolder", "test-05@3x.png"),
            (300, 300))

    def test_should_raise_exception_with_assets_dir_not_present(self):
        converter = Converter()
        os.chdir(os.path.join(self.converter_tests_resource_path, "suggest_asset_diretory_test"))
        converter.inputDir = "FaceAssetsDir"
        converter.outputDir = self.converter_output_tests_resource_path

        try:
            converter.convert()
            self.fail("This should fail")
        except AssetsDirNotFoundException as e:
            self.assertEqual(e.asset_dir_candidate, "Vector_assets")

    def test_should_raise_exception_with_empty_parameter_if_no_vector_files_found(self):
        converter = Converter()
        os.chdir(os.path.join(self.converter_tests_resource_path, "suggest_asset_diretory_test", "Images.xcassets"))
        converter.inputDir = "FaceAssetsDir"
        converter.outputDir = self.converter_output_tests_resource_path

        try:
            converter.convert()
            self.fail("This should fail")
        except AssetsDirNotFoundException as e:
            self.assertEqual(e.asset_dir_candidate, None)


    def test_dont_reconvert_old_files_test(self):
        converter = Converter()
        os.chdir(os.path.join(self.converter_tests_resource_path, "dont_reconvert_old_files_test"))
        converter.inputDir = "Assets"
        converter.outputDir = self.converter_output_tests_resource_path

        converter.convert()

        sha1_of_generated_files = []
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-01.png")))
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-02.png")))

        shutil.copy2(os.path.join(converter.inputDir, "test-01.eps"), os.path.join(converter.inputDir, "test-02.eps"))
        converter.convert()

        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-01.png")))
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-02.png")))

        self.assertEqual(sha1_of_generated_files[0], sha1_of_generated_files[2])
        self.assertNotEqual(sha1_of_generated_files[1], sha1_of_generated_files[3])


    def test_respect_force_flag(self):
        converter = Converter()
        os.chdir(os.path.join(self.converter_tests_resource_path, "dont_reconvert_old_files_test"))
        converter.inputDir = "Assets"
        converter.outputDir = self.converter_output_tests_resource_path
        converter.force_convert = True

        converter.convert()

        sha1_of_generated_files = []
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-01.png")))
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-02.png")))

        converter.convert()

        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-01.png")))
        sha1_of_generated_files.append(converter.sha1_of_file(os.path.join(converter.outputDir, "test-02.png")))

        self.assertNotEqual(sha1_of_generated_files[0], sha1_of_generated_files[2])
        self.assertNotEqual(sha1_of_generated_files[1], sha1_of_generated_files[3])

    def test_escape_filenames(self):
        converter = Converter()
        converter.inputDir = os.path.join(self.converter_tests_resource_path, "convert_test")
        converter.outputDir = self.converter_output_tests_resource_path

        fancy_filename = "& :()[]{}|"
        shutil.rmtree(os.path.join(converter.inputDir, "subfolder", "subsubfolder"))
        os.remove(os.path.join(converter.inputDir, "test-01.eps"))
        os.remove(os.path.join(converter.inputDir, "test-02.eps"))
        os.remove(os.path.join(converter.inputDir, "test-03.eps"))
        os.rename(os.path.join(converter.inputDir, "subfolder", "test-04.eps"),
                  os.path.join(converter.inputDir, "subfolder", fancy_filename + ".eps"))
        converter.convert()

        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", fancy_filename + ".png"),
            (100, 100))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", fancy_filename + "@2x.png"),
            (200, 200))
        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", fancy_filename + "@3x.png"),
            (300, 300))

    def check_if_file_not_resized_and_additional_suffix_not_added(self, filename):
        converter = Converter()
        converter.inputDir = os.path.join(self.converter_tests_resource_path, "convert_test")
        converter.outputDir = self.converter_output_tests_resource_path

        shutil.rmtree(os.path.join(converter.inputDir, "subfolder", "subsubfolder"))
        os.remove(os.path.join(converter.inputDir, "test-01.eps"))
        os.remove(os.path.join(converter.inputDir, "test-02.eps"))
        os.remove(os.path.join(converter.inputDir, "test-03.eps"))
        os.rename(os.path.join(converter.inputDir, "subfolder", "test-04.eps"),
                  os.path.join(converter.inputDir, "subfolder", filename + ".png"))
        converter.convert()

        self.assert_valid_png_file(
            os.path.join(self.converter_output_tests_resource_path, "subfolder", filename + ".png"),
            (100, 100))
        self.assertFalse(os.path.isfile(os.path.join(self.converter_output_tests_resource_path, "subfolder", filename + "@2x.png")))
        self.assertFalse(os.path.isfile(os.path.join(self.converter_output_tests_resource_path, "subfolder", filename + "@3x.png")))

    def test_dont_resize_and_rename_f_suffixes_2x(self):
        self.check_if_file_not_resized_and_additional_suffix_not_added("a@2x")

    def test_dont_resize_and_rename_f_suffixes_3x(self):
        self.check_if_file_not_resized_and_additional_suffix_not_added("a@3x")