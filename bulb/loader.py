from runbox import DockerExecutor

from bulb import cfg
from bulb.services.execution.pipeline_factory import PipelineFactory
from bulb.services.execution.pipelines import (
    get_default_non_building_pipeline,
    get_pipeline_with_default_build,
)
executor = DockerExecutor()
factory = (PipelineFactory()
           .register(cfg.python2_7_profile, get_default_non_building_pipeline)
           .register(cfg.python3_10_profile, get_default_non_building_pipeline)
           .register(cfg.cpp17_profile, get_pipeline_with_default_build)
           .register(cfg.cpp11_profile, get_pipeline_with_default_build))
