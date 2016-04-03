# Awesomenauts File Dumper
This command line utility will decrypt files from the game Awesomenauts.

**Requires a CPU with the AES-NI instruction set.**

## Usage

1. Download the latest release version from [here](https://github.com/Nodja/AwesomenautsFileDumper/releases).
2. Copy the executable to the game's directory and run it without arguments, alternatively you can pass the game's directory as the first argument.

   Example: ```AwesomenautsFileDumper.exe "C:\Program Files (x86)\Steam\steamapps\common\Awesomenauts"```

   The decrypted files will be placed in a folder called _decrypted under the current directory.

## Development

If you wish to change the code you will not be able to run the dumper with just python. You will see that it tries to import a _aesenc module that doesn't exist. This is because we need to built it first using cffi and a C compiler (only visual studio tested).

### Instructions
These instruction are for specific for windows.

1. Install Visual Studio 2015 express. 
2. Install cffi ```pip install cffi```
3. Build the _aesenc by running the aesenc.build.py script. Open a command line in the project folder and then:

   ```
   cd animolite
   python aesenc.build.py
   ```
   this will create a _aesenc.<platform>.pyd file in the animolite directory.

The code should now run.


### Creating a single exe.

If you want to create a single exe file to distribute your fixes, etc. use pyinstaller and run the following command. I'm just placing this section here for future reference :)
```pyinstaller -onefile --hidden-import=_cffi_backend AwesomenautsFileDumper.py```
