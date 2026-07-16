from setuptools import find_packages, setup

package_name = 'mini_project'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='monouk',
    maintainer_email='p20240062@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
                'mainpage = mini_project.main:main',
                'keyboard = mini_project.keyboard.keyboard_publisher:main'
        ],
    },
)
