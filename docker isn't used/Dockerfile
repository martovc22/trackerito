# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app
COPY trackerito-83f27862540c.json /usr/src/app/trackerito-83f27862540c.json
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Run the application when the container launches
CMD ["python", "./tracker.py"]
