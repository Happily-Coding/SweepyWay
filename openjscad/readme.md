# Intro
The idea of using openjscad cli is to be able to convert openjscad files to stls.
This file lists the steps for local testing

# Build the image
- Build an image you can the run to perform the conversions
  - tag it as openjscad-cli so it's easily callable
  - Use the dockerfile located in openjscad
```
docker build -t openjscad-cli openjscad
```


# Run the image 
Run the image to convert all files in ergogen\output\cases to .stl

From a powershell cli at the project root:
```
docker run -it -v "${PWD}\ergogen\output\cases:/designs" openjscad-cli bash -c convert-all.sh
```

- -it: Keeps it interactive so you see output/errors
- -v "${PWD}\ergogen\output\cases:/designs" Mounts your local designs directory into the container
- openjscad-cli: The image you built and tagged
- overrides the entry point of the node image, instead executing the convert all script which on the workdir iterates through all the jscad files and outputs the stls