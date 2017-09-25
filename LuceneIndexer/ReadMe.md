# The PyLucene Project

Welcome to the project to try to get Apache Lucene working with
a Python Wrapper around it. This document will be updated
frequently with new features and improvements in response to your
feedback.

Before we go on you should know that this is a notoriously difficult
product to build and you should therefore not be alarmed about
the milliards of requirements that are going to be listed.

**There is NO allowed deviation from the listed requirements.**

If you deviate from any of the installation steps listed below your are
in essence, shooting yourself in the foot. You can choose to do this
and debug yourself but no help will be given to you seeing as how
with the current requirements, the build and execution process is
confirmed working.

# Install The Prerequisites

You need to have the following installed on your computer. Required
download links are given for each download.

- Python 3.6 via [Anaconda](https://www.anaconda.com/download/) 64 bit.
- 64 bit version of [JDK](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) 1.8.
- [Microsoft Visual C++ Build Tools](https://www.microsoft.com/en-us/download/details.aspx?id=48159)
for python 3.6.
- The latest (but still old) 32 bit build of [WinAnt](https://code.google.com/archive/p/winant/downloads).
- 64 bit [Cywgin](https://www.cygwin.com/).
During installation search for the package "make" and choose to
install it explicitly.

# Setting the Environment Variables

Set the following environment variables on our system. The paths given
should mostly be the same as yours, if you used the default locations
during installation. The java version number may be different so
update it to reflect the Java version that you have.

```
JAVA_HOME = C:\Program Files\Java\jdk1.8.0_144
JCC_JDK = C:\Program Files\Java\jdk1.8.0_144
PATH += ;%JAVA_HOME%\bin
PATH += ;%JAVA_HOME%\jre\bin\server
PATH += ;C:\cygwin\bin
ANT_HOME = C:\Program Files (x86)\WinAnt
CLASSPATH = .;C:\Program Files\Java\jdk1.8.0_144\lib
CLASSPATH += ;C:\Program Files\Java\jdk1.8.0_144\jre\lib
CLASSPATH += ;C:\Program Files\Java\jdk1.8.0_144\lib\tools.jar
```

# Installing Apache Lucene

First download [PyLucene](http://www.apache.org/dyn/closer.lua/lucene/pylucene/)
6.5.0.
Extract it into the LuceneIndexer directory where this readme is.
I am purposely
ignoring this folder since it is too big to upload to GitHub and
it should always be compiled from source on everyone's machines separately.

Your directory structure should now roughly look as follows (probably with
the exception of the index and dataset folders:

![alt text](../images/lucene-folder-structure.png)

Next, edit the variables in the makefile inside pylucene-x.x.x to
correspond to what you need for your system. The following should mostly
be the same with the exception of your user directory for the python
path.

```
PREFIX_PYTHON=C:/Users/Stanley/Anaconda3
ANT=C:/Progra~2/WinAnt/bin/ant
JAVA_HOME=C:/Progra~1/Java/jdk1.8.0_144
PYTHON=$(PREFIX_PYTHON)/python.exe
JCC=$(PYTHON) -m jcc
NUM_FILES=8
```

Now go to the LuceneIndexer directory using **Powershell**.

**You MUST use powershell to complete the installation.**

Run the following commands:

```
cd .\pylucene-6.5.0
pushd jcc
python .\setup.py build
python .\setup.py install
popd
make
make install
```

The make step should take a very long time to complete but should
finish eventually. Do not stop it if it seems like it is hanging, because
it's not.

# Installing the LuceneIndexer Package
Run: ```pip install -r requirements.txt``` to install all pip
dependencies.

# Download the Necessary Data Set Files

Download the NIPS papers in .sqlite format from
[kaggle](https://www.kaggle.com/benhamner/nips-papers).

Then extract the .sqlite file to ```IRPoject\LuceneIndexer\dataset```

# Launch The Server

To launch the server simple cd to the LuceneIndexer directory and run
```python .\server.py```

You can then query simple things by going to the url:

```127.0.0.1:5002/papers?query=data```

This will return all paper titles which have data in their title.

# PyCharm Settings

The following are a collection of useful hints and tips to know when
using the preferred IDE in this case, PyCharm.

- Set the _lucene directory in the build folder of PyLucene
as a sources route to remove those red lines everywhere. Auto-completion
of code still doesn't work even with this, but it's much nicer than before.

# What To Do If You Get Stuck
I have tried this installation guide on another clean-ish Windows machine.

However, chances are, this documentation isn't complete. It probably works for me
but doesn't for you. What options are left for you? Some serious googling.
And then update this file. Please please please update this file.
You'll be helping out everyone else who has to work on this. And
of course our professor since he has to be able to build this for
grading the project.

If your build fails and the errors have something to do with visual studio,
try going to control panel -> add/remove programs and "repair" the install
of the build tools. This fixed my problems all the time that I was working.