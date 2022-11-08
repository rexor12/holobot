# Specify the required Python version.
ARG PYTHON_IMAGE=python:3.10-slim
FROM ${PYTHON_IMAGE}

ARG PYTHON_EXECUTABLE=python3.10
ARG WORKING_DIRECTORY=/usr/holobot
ARG VENV_DIRECTORY=${WORKING_DIRECTORY}/.venv

# Create the working directory.
RUN mkdir -p ${WORKING_DIRECTORY}
WORKDIR ${WORKING_DIRECTORY}

# Make and activate a virtual environment for the dependencies.
RUN mkdir ${VENV_DIRECTORY}
RUN ${PYTHON_EXECUTABLE} -m venv ${VENV_DIRECTORY}
RUN . ${VENV_DIRECTORY}/bin/activate

# Install the bot's dependencies.
COPY requirements.txt ${WORKING_DIRECTORY}
RUN ${PYTHON_EXECUTABLE} -m pip install -r requirements.txt

# Copy the source code.
COPY . .

# Start the bot.
ENV HOLO_PYTHON_EXECUTABLE ${PYTHON_EXECUTABLE}
STOPSIGNAL SIGINT
ENTRYPOINT ["/bin/bash", "-c", "${HOLO_PYTHON_EXECUTABLE} -OOm holobot"]
