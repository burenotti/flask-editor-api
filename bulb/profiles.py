from pathlib import Path

from runbox.models import DockerProfile

from bulb.models import LanguageProfile

cpp17_profile = LanguageProfile(
    language='C++',
    version='C++17',
    build_profile=DockerProfile(
        image='gcc10',
        workdir=Path('/build'),
        cmd_template=['g++', 'main.cpp', '--std=c++17', '/sandbox/build'],
        user='builder'
    ),
    profile=DockerProfile(
        image='gcc10',
        workdir=Path('/sandbox'),
        cmd_template=['/sandbox/build'],
        user='sandbox',
    ),
)

cpp11_profile = cpp17_profile.copy(update={
    'version': 'C++11',
    'build_profile': {
        'cmd_template': ['g++', 'main.cpp', '--std=c++11', '/sandbox/build']
    }
})

python3_10_profile = LanguageProfile(
    language='python',
    version='3.10',
    profile=DockerProfile(
        image='python3.10-sandbox',
        workdir=Path('/sandbox'),
        cmd_template=['python', 'main.py'],
        user='sandbox',
    ),
)

python2_7_profile = LanguageProfile(
    language='python',
    version='2.7',
    profile=DockerProfile(
        image='python2.7-sandbox',
        workdir=Path('/sandbox'),
        cmd_template=['python', 'main.py'],
        user='sandbox',
    )
)
