import setuptools

setuptools.setup(name='Audio_Player',
      version='0.0.1',
      author='Prabhjit Kumar Dutta',
      description='A GUI based Audio Player that Streams audio from an URL',
      install_requires=['PyQt5', 'pygame', 'requests', 'mutagen'],
      packages=setuptools.find_packages(), url = 'https://github.com/PrabhjitDutta/URL_Audio_Player.git',
      )
