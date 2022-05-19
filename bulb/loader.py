from runbox import DockerExecutor

from bulb import profiles
from bulb.services.execution.pipeline_factory import PipelineFactory
from bulb.services.execution.pipelines import (
    get_default_non_building_pipeline,
    get_pipeline_with_default_build,
)
executor = DockerExecutor()
factory = (PipelineFactory()
           .register(profiles.python2_7_profile, get_default_non_building_pipeline)
           .register(profiles.python3_10_profile, get_default_non_building_pipeline)
           .register(profiles.cpp17_profile, get_pipeline_with_default_build)
           .register(profiles.cpp11_profile, get_pipeline_with_default_build))
