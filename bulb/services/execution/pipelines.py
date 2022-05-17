from .base_execution_pipeline import BaseExecutionPipeline
from .build_stage import *
from bulb.cfg import LanguageProfile


def get_default_non_building_pipeline(profile: LanguageProfile) -> BaseExecutionPipeline:
    pipeline = BaseExecutionPipeline() \
        .with_profile(profile) \
        .then(CreateSandbox("sandbox")) \
        .then(WriteSourceCode("/sandbox/main.py", "sandbox")) \
        .then(Run("sandbox")) \
        .then(Observe("sandbox"))

    return pipeline


def get_pipeline_with_default_build(profile: LanguageProfile) -> BaseExecutionPipeline:
    pipeline = BaseExecutionPipeline() \
        .with_profile(profile) \
        .then(BuildAndMountAt('/build')) \
        .then(CreateSandbox("sandbox")) \
        .then(Run("sandbox")) \
        .then(Observe("sandbox"))

    return pipeline
