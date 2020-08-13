from setuptools import setup, find_packages


setup(
   name='moka',
   version='1.0',
   description='A useful module',
   author='Zhengping Zhou',
   author_email='zpzhou@stanford.edu',
   packages=find_packages(),
   install_requires=['numpy', 'opencv-python', 'matplotlib', 'torch', 'visdom', 'scipy', 'scikit-learn', 'jupyter', 'tqdm', 'dominate', 'torchsummary', 'pillow', 'tabulate', 'termcolor'],
)