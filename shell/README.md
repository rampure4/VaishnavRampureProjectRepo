# Project Three

## Author Information
- **Name**: Varchasvi Vaishnav Rampure
- **CS Login**: [varchasvi]
- **Wisc ID**: [908 216 7157]
- **Email**: rampure@wisc.edu

## Program Description
This program implements a simple shell in C, named "wsh" (Wiscon Shell), that can interpret and execute command line inputs. It supports features such as:
Execution of basic commands directly from the terminal or a batch file.
- Handling of environment variables and shell-local variables.
- Command history management, allowing users to view and execute previous commands.
- Support for command piping (`|`) to direct the output of one command as input to another.
- Built-in commands for changing the current directory (`cd`), setting environment (`export`) and local (`local`) variables, and exiting the shell (`exit`).

## Implementation Status
As of late, the program is fully implemented and is passing all the tests. The functionalities that are working and done would be:
- Basic command parsing and execution.
- Environment and local variable management.
- Command history with adjustable capacity.
- Basic piping between commands.

## Usage Instructions
gcc -o wsh wsh.c

    Interactive Mode
    ./wsh
    wsh>  indicating that the shell is running in interactive mode.
    Batch Mode
    Must provide a script file as an argument to the program:
    ./wsh scriptfile.wsh
    The shell will execute commands from the provided file.

