
import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ball_on_plate'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='andre',
    maintainer_email='andre@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ball_reference_node = ball_on_plate.ball_reference_node:main',
            'ball_sensor_node = ball_on_plate.ball_sensor_node:main',
            'ball_error_node = ball_on_plate.ball_error_node:main',
            'ball_filter_node = ball_on_plate.ball_filter_node:main',
            'ball_control_node = ball_on_plate.ball_control_node:main'
        ],
    },
)
