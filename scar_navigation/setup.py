from setuptools import setup
import os
from glob import glob

package_name = 'scar_navigation'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # config 폴더 설치
        (os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')),
        # launch 폴더 설치
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your@email.com',
    description='SCAR robot Nav2 navigation stack',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'wheel_odom_node = scar_navigation.wheel_odom_node:main',
            'fake_sensor_node = scar_navigation.fake_sensor_node:main',
        ],
    },
)

