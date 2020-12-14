import os
from copy import deepcopy
from pathlib import Path

# TODO: <Alex>ALEX</Alex>
import pytest
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

try:
    from unittest import mock
except ImportError:
    from unittest import mock

import logging

# TODO: <Alex>ALEX</Alex>
import great_expectations.exceptions as ge_exceptions
from great_expectations.data_context.store.util import (
    delete_config_from_filesystem,
    load_config_from_filesystem,
    save_config_to_filesystem,
)
from great_expectations.data_context.types.base import BaseConfig
from great_expectations.marshmallow__shade import (
    INCLUDE,
    Schema,
    ValidationError,
    fields,
    validates_schema,
)
from great_expectations.util import gen_directory_tree_str

yaml = YAML()

logger = logging.getLogger(__name__)


def test_v3_configuration_store(tmp_path_factory):
    class SampleConfig(BaseConfig):
        def __init__(
            self,
            some_param_0: str = None,
            some_param_1: int = None,
            commented_map: CommentedMap = None,
        ):
            if some_param_0 is None:
                some_param_0 = "param_value_0"
            self.some_param_0 = some_param_0
            if some_param_1 is None:
                some_param_1 = 169
            self.some_param_1 = some_param_1

            super().__init__(commented_map=commented_map)

        @classmethod
        def from_commented_map(cls, commented_map: CommentedMap) -> BaseConfig:
            try:
                config: dict = SampleConfigSchema().load(commented_map)
                return cls(commented_map=commented_map, **config)
            except ValidationError:
                logger.error(
                    "Encountered errors during loading config. See ValidationError for more details."
                )
                raise

        def get_schema_validated_updated_commented_map(self) -> CommentedMap:
            commented_map: CommentedMap = deepcopy(self.commented_map)
            commented_map.update(SampleConfigSchema().dump(self))
            return commented_map

    class SampleConfigSchema(Schema):
        class Meta:
            unknown = INCLUDE

        some_param_0 = fields.String()
        some_param_1 = fields.Integer()

        @validates_schema
        def validate_schema(self, data, **kwargs):
            pass

    root_directory_path: str = "test_v3_configuration_store"
    root_directory: str = str(tmp_path_factory.mktemp(root_directory_path))
    base_directory: str = os.path.join(root_directory, "some_store_config_dir")

    config_0: SampleConfig = SampleConfig(some_param_0="test_str_0", some_param_1=65)
    store_name_0: str = "test_config_0"
    save_config_to_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_0,
        base_directory=base_directory,
        config=config_0,
    )

    dir_tree: str = gen_directory_tree_str(startpath=base_directory)
    assert (
        dir_tree
        == """some_store_config_dir/
    .ge_store_backend_id
    test_config_0.yml
"""
    )
    assert (
        len(
            [
                path
                for path in Path(base_directory).iterdir()
                if str(path).find(".ge_store_backend_id") == (-1)
            ]
        )
        == 1
    )

    stored_file_name_0: str = os.path.join(base_directory, f"{store_name_0}.yml")
    with open(stored_file_name_0, "r") as f:
        config: CommentedMap = yaml.load(f)
        expected_config: CommentedMap = CommentedMap(
            {"some_param_0": "test_str_0", "some_param_1": 65}
        )
        assert config == expected_config

    loaded_config: BaseConfig = load_config_from_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_0,
        base_directory=base_directory,
    )
    assert loaded_config.to_json_dict() == config_0.to_json_dict()

    config_1: SampleConfig = SampleConfig(some_param_0="test_str_1", some_param_1=26)
    store_name_1: str = "test_config_1"
    save_config_to_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_1,
        base_directory=base_directory,
        config=config_1,
    )

    dir_tree: str = gen_directory_tree_str(startpath=base_directory)
    assert (
        dir_tree
        == """some_store_config_dir/
    .ge_store_backend_id
    test_config_0.yml
    test_config_1.yml
"""
    )
    assert (
        len(
            [
                path
                for path in Path(base_directory).iterdir()
                if str(path).find(".ge_store_backend_id") == (-1)
            ]
        )
        == 2
    )

    stored_file_name_1: str = os.path.join(base_directory, f"{store_name_1}.yml")
    with open(stored_file_name_1, "r") as f:
        config: CommentedMap = yaml.load(f)
        expected_config: CommentedMap = CommentedMap(
            {"some_param_0": "test_str_1", "some_param_1": 26}
        )
        assert config == expected_config

    loaded_config: BaseConfig = load_config_from_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_1,
        base_directory=base_directory,
    )
    assert loaded_config.to_json_dict() == config_1.to_json_dict()

    delete_config_from_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_0,
        base_directory=base_directory,
    )
    assert (
        len(
            [
                path
                for path in Path(base_directory).iterdir()
                if str(path).find(".ge_store_backend_id") == (-1)
            ]
        )
        == 1
    )

    delete_config_from_filesystem(
        configuration_class=SampleConfig,
        store_name=store_name_1,
        base_directory=base_directory,
    )
    assert (
        len(
            [
                path
                for path in Path(base_directory).iterdir()
                if str(path).find(".ge_store_backend_id") == (-1)
            ]
        )
        == 0
    )