#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>
#include <errno.h>


// Defining a struct for storing individual shell command history entries.
typedef struct HistoryNode
{
    char *command;
    struct HistoryNode *next;
} HistoryNode;
// Defining a struct for storing shell variables.
typedef struct VarNode
{
    char *name;
    char *value;
    struct VarNode *next;
} VarNode;


// Function prototypes for managing history and variables.
void free_history_node(HistoryNode *node);
void adjust_history_capacity(int new_capacity);
void add_history(char *command);
void print_history();
void execute_history_command(int index);
void free_history();
VarNode *find_variable(VarNode *head, const char *name);
void free_variables(VarNode **head);
void substitute_variables(char **argv, VarNode *envVars, VarNode *shellVars);
void execute_command(char **argv);
void set_env_variable(const char *name, const char *value);
void set_env_variable(const char *name, const char *value);

#define MAX_ARGS 64 // max number of arguments for a command 
#define DELIM " \t\r\n\a" // delimiters for splitting compand inputs. 

// Global variables for environment variables, shell variables, and command history.
VarNode *envVars = NULL;
VarNode *shellVars = NULL;
HistoryNode *history_head = NULL;
int history_count = 0;
int history_capacity = 5; // default history capacity

//Frees a single history node ands its associated command
void free_history_node(HistoryNode *node)
{
    free(node->command);
    node->command = NULL;
    free(node);
}

//frees all nodes in the history list
void free_history() {
    while (history_head != NULL) {
        HistoryNode *temp = history_head;
        history_head = history_head->next;
        free(temp->command);
        free(temp);
        history_count--;
    }
    history_count = 0;
}

// adjust the max number of commands that history can hold
void adjust_history_capacity(int new_capacity)
{
    // set the new capacity to the global history_capacity
    history_capacity = new_capacity;
    //check if the current number of commands in history excceds the limit of the new capacity 
    while (history_count > history_capacity)
    {
        // Traverse through the list to find the last commmand
        HistoryNode *temp = history_head, *prev = NULL; 
        // Iterate until the last command is found
        while (temp->next != NULL)
        {
            prev = temp;
            temp = temp->next;
        }

        // prev is the last command in the "cutoff" pointing to null gets rid of the values after prev
        if (prev != NULL)
        {
            prev->next = NULL;
        }
        free_history_node(temp);
        history_count--; // decrement the count of commands in history 
        // if prev is null it means that we have only one node in the list
        if (prev == NULL)
        {
            history_head = NULL;
        }
    }
}

// adding commands to history list, respecting the limit
void add_history(char *command)
{
    // if  the is ) or the command is a duplicate of the last command(the head) we want to ignore 
   if (history_capacity == 0 || (history_head && strcmp(history_head->command, command) == 0)) return;  

    
    HistoryNode *new_node = (HistoryNode *)malloc(sizeof(HistoryNode));
    if (!new_node)
    {
        perror("Failed to allocate memory for new history node");
        return;
    }
    // duplucate the command string into the new node
    new_node->command = strdup(command);
    if (!new_node->command)
    {
        perror("Failed to duplicate command string");
        free(new_node);
        return;
    }
    
    //inserting the command into the history list
    new_node->next = history_head;
    history_head = new_node;
    history_count++;

    // check if the hostory count exceeds the limit
    if (history_count > history_capacity)
    {
        //need to traverse to the last node in the list
        HistoryNode *temp = history_head;
        HistoryNode *prev = NULL;
        while (temp->next != NULL)
        {
            prev = temp;
            temp = temp->next;
        }
         // prev is the last command in the "cutoff" pointing to null gets rid of the values after prev
        if (prev != NULL)
        {
            prev->next = NULL;
        }
        free_history_node(temp);
        history_count--;
    }
}

void print_history()
{
    int num = 0;
    HistoryNode *current = history_head;
    // traverse through the list until end make sure it only prints until the limit
    while (current != NULL && num < history_capacity)
    {
        printf("%d) %s\n", num + 1, current->command);
        current = current->next;
        num++;
    }
}

void execute_history_command(int index)
{
    //check if the index if in vaild range
    if (index < 1 || index > history_count)
    {
        printf("Invalid history reference: %d\n", index);
        return;
    }
    //traverse the history linked list to find the command at the given index 
    HistoryNode *current = history_head; // start from the head
    for (int i = 1; i < index && current != NULL; i++)
    {
        current = current->next;
    }
    // if command is found in history
    if (current != NULL)
    {
        // duplicate the command strinf to avoid modyfing the orginal in history 
        char *cmd_copy = strdup(current->command);
        if (!cmd_copy)
        {
            perror("strdup failed");
            return;
        }
        free(cmd_copy);

         // parse the duplicated command into arguments.
        char *argv[MAX_ARGS];
        int argc = 0;
        char *token = strtok(cmd_copy, DELIM);
        while (token != NULL && argc < MAX_ARGS - 1)
        {
            // Handle variable expansion for tokens starting with '$'.
            if (token[0] == '$')
            {
                VarNode *var = find_variable(envVars, token + 1); // // Try to find the variable in environment variables first.
                if (var == NULL)
                {
                    var = find_variable(shellVars, token + 1);
                }

                 // If the variable is found, use its value; otherwise, use an empty string.
                if (var != NULL)
                {
                    argv[argc++] = var->value;
                }
                else 
                {
                    argv[argc++] = ""; 
                }
            }
            else // For regular tokens, just add them to the arguments array.
            {
                argv[argc++] = token;
            }

            token = strtok(NULL, DELIM);  // Continue tokenizing the command string.
        }
        argv[argc] = NULL;

        // Special handling for 'echo' command to directly print the arguments.
        if (strcmp(argv[0], "echo") == 0 && argc > 1)
        {
            for (int i = 1; i < argc; i++)
            {
                printf("%s ", argv[i]);
            }
            printf("\n");
        }
        else
        {
            // For all other commands, use the execute_command function.
            execute_command(argv);
        }
        free(cmd_copy);
    }
}


VarNode *find_variable(VarNode *head, const char *name)
{
    // start at the head
    VarNode *curr = head;
    while (curr != NULL)
    {
        // if variable is found need to return it
        if (strcmp(curr->name, name) == 0)
        {
            return curr;
        }
        //update to next otherwise
        curr = curr->next;
    }
    //if not found null
    return NULL;
}

// function to remove a variable from a linked list
void unset_variable(VarNode **head, const char *name)
{
    //  printf("Debug: unset_variable called for '%s'\n", name);
    // Temporary pointers to traverse the list. temp is used to find the target node, and prev to keep track of the node before temp.
    VarNode *temp = *head, *prev = NULL;
     // Traverse the list to find the node with the matching name. Stop if it reaches the end (NULL) or finds the node.
    while (temp != NULL && strcmp(temp->name, name) != 0)
    {
        prev = temp;
        temp = temp->next;
    }

    // reached end of list
    if (temp == NULL)
    {
        // printf("Debug: Variable '%s' not found in list, cannot unset.\n", name);
        return;
    }
    // variable was found at the head
    if (prev == NULL)
    {
        // Removing the head of the list
        *head = temp->next;
    }
    // if in the middle
    else
    {
        // Removing a middle or tail node
        prev->next = temp->next;
    }
    // printf("Debug: Unsetting variable '%s', freeing resources.\n", name);
    free(temp->name);
    free(temp->value);
    free(temp);
}

// Function to handle environment variables
void set_env_variable(const char *name, const char *value)
{
    // if the value is null or an empty string remove the environment variable.
    if (value == NULL || value[0] == '\0')
    {
        unsetenv(name);
    }
    else
    {
        // set  the environment variable with the given value. 1 means to overwrite the value if varaible already exists
        setenv(name, value, 1);
    }
}

// Function to handle local (shell) variables

void set_local_variable(VarNode **head, const char *name, const char *value)
{
    VarNode *curr = *head;
    VarNode *prev = NULL;
    
    // Traverse the list to find a variable with the matching name.
    while (curr != NULL && strcmp(curr->name, name) != 0)
    {
        prev = curr;
        curr = curr->next;
    }
    
     // If the variable is found in the list.
    if (curr)
    {
          // Free the existing value of the found variable.
        free(curr->value);
          // If the new value is NULL or empty, remove the variable from the list.
        if (value == NULL || value[0] == '\0')
        {
             // If there's a previous node, bypass the current node, effectively removing it.
            if (prev)
                prev->next = curr->next;
            else
                *head = curr->next;  // If removing the head, update the head pointer.
            free(curr->name);
            free(curr);
        }
        else
        {
             // If the new value is not NULL or empty, update the variable's value.
            curr->value = strdup(value);
        }
    }
    // If the variable is not found and the new value is not NULL or empty, create a new variable.
    else if (value && value[0])
    {
        // Allocate memory for the new variable node.
        VarNode *newVar = (VarNode *)malloc(sizeof(VarNode));
        // Duplicate the name and value for the new variable.
        newVar->name = strdup(name);
        newVar->value = strdup(value);
        newVar->next = NULL;
        // if there is a prev node add the new node right after it 
        if (prev)
        {
            prev->next = newVar;
        }
        else
        {
            // if not it is inserted at the head
            *head = newVar;
        }
    }
}

// Function to free all variables in a linked list and reset the list head to NULL.
void free_variables(VarNode **head)
{
    VarNode *current = *head; // 
    while (current != NULL)
    {
        VarNode *next = current->next;
        free(current->name);
        free(current->value);
        free(current);
        current = next;
    }
    *head = NULL;
}

void substitute_variables(char **argv, VarNode *envVars, VarNode *shellVars)
{
    // iterate over each argument in argv
    for (int i = 0; argv[i] != NULL; i++)
    {
         // Check if the argument is a variable 
        if (argv[i][0] == '$')
        {
            char *varName = argv[i] + 1;                // Skip the '$'
            const char *substitution = getenv(varName); // Attempt to retrieve the variable's value from the environment variables.

            // If the environment variable is not found, try to find it in the shell variables list.
            if (!substitution)
            { // If not found, try shell variable
                VarNode *var = find_variable(shellVars, varName);
                substitution = var ? var->value : NULL;
            }

            // If a substitution is found, replace the argument with the variable's value.
            if (substitution)
            {
                argv[i] = strdup(substitution); // Replace with the variable's value
            }
            else
            {
                // Shift all elements to the left to remove the empty argument
                for (int j = i; argv[j] != NULL; j++)
                {
                    argv[j] = argv[j + 1];
                }
                i--; // Adjust index to revisit the current position with the next argument
            }
        }
    }
}

// Function to remove empty strings from argv, compacting the array.
void compact_argv(char **argv)
{
    int compactIndex = 0;  // Initialize an index to track the position for compacted arguments.
    // Iterate through argv.
   for (int i = 0; argv[i] != NULL; i++)
    {
        // Check if the current argument is not an empty string.
        if (argv[i][0] != '\0')
        {                               
            argv[compactIndex++] = argv[i]; 
        }
    }
     // After moving all non-empty arguments, terminate the compacted argv with a NULL pointer.
    argv[compactIndex] = NULL; 
}
// Function to count the number of pipe characters ('|') in the command arguments array.
int count_pipes(char **argv)
{
    int pipes = 0; 
    // Iterate through the argv array until a NULL pointer is encountered, which signifies the end of the array.
    for (int i = 0; argv[i] != NULL; i++)
    {
         // Check if the current argument is a pipe character.
        if (strcmp(argv[i], "|") == 0)
            pipes++; // Increment the pipe count for each pipe found.
    }
    return pipes; // Return the total count of pipes found in argv.
}
// Function to execute commands that include pipes for inter-process communication.
void execute_commands_with_pipes(char **argv)
{
    int pipes = count_pipes(argv); // count the number of pipes in the command
    int fd[2 * pipes]; // create an array for filedescriptors, two for each pipe

    // Initialize pipes and file descriptors.
    for (int i = 0; i < pipes; i++)
    {
         // Create a pipe and store its file descriptors.
        if (pipe(fd + i * 2) < 0)
        {
            perror("pipe");  // Print an error message if pipe creation fails.
            exit(EXIT_FAILURE);
        }
    }

    int j = 0; // index to iterate through argv
    int command_start = 0; // Index to mark the start of the current command before a pipe.
    for (int i = 0; i <= pipes; i++)
    {
        // Find the next pipe character (or the end of argv) to determine the command to execute.
        while (argv[j] != NULL && strcmp(argv[j], "|") != 0)
        {
            j++;
        }
        argv[j] = NULL;

        //fork a new process for each command
        pid_t pid = fork();
        if (pid == 0)
        {
            // If not the first command, redirect standard input from the previous pipe.
            if (i > 0)
            {
                dup2(fd[(i - 1) * 2], 0);
            }
            // If not the last command, redirect standard output to the next pipe.
            if (i < pipes)
            {
                dup2(fd[i * 2 + 1], 1);
            }
             // Close all file descriptors in the child process.
            for (int k = 0; k < 2 * pipes; k++)
            {
                close(fd[k]);
            }
            // Execute the command.
            if (execvp(argv[command_start], &argv[command_start]) == -1)
            {
                perror("execvp");
                exit(EXIT_FAILURE);
            }
        }
        else if (pid < 0)
        {
            perror("fork");
            exit(EXIT_FAILURE);
        }
        // Prepare for the next command by updating command_start and j.
        command_start = j + 1;
        j++;
    }
    //close all the file descriptors
    for (int i = 0; i < 2 * pipes; i++)
    {
        close(fd[i]);
    }
    // Wait for all child processes to finish.
    for (int i = 0; i <= pipes; i++)
    {
        wait(NULL);
    }
}
// method to change into a directory
void change_directory(char *path)
{
    // If no path is provided, use the HOME environment variable as the default path
    if (path == NULL)
        path = getenv("HOME");
    // Attempt to change the current working directory to the specified path
    if (chdir(path) == -1)
        perror("chdir");
}

// function to execute a given command
void execute_command(char **argv)
{
    // Handle export command to set an enviroment variable
    if (strcmp(argv[0], "export") == 0 && argv[1] != NULL)
    {
        //split the argument into a name and value
        char *name = strtok(argv[1], "=");
        char *value = strtok(NULL, "");
        // set an enviroment variable
        set_env_variable(name, value);
    }
    // Handle local command to set a shell local variable
    else if (strcmp(argv[0], "local") == 0 && argv[1] != NULL)
    {
        //split the argument into a name and value
        char *name = strtok(argv[1], "=");
        char *value = strtok(NULL, "");
        // Set the local variable
        set_local_variable(&shellVars, name, value);
    }
    // handle vars command to list all the shell local vars
    else if (strcmp(argv[0], "vars") == 0)
    {
        //
        VarNode *current = shellVars;
        // iterate through linked list of variables and print each one
        while (current != NULL)
        {
            printf("%s=%s\n", current->name, current->value);
            current = current->next;
        }
    }
    // handle the cd command to change directory
    else if (strcmp(argv[0], "cd") == 0)
    {
        change_directory(argv[1]);
    }
    // handle exit command to exit the shell 
    else if (strcmp(argv[0], "exit") == 0)
    {
        free_history();
        exit(0);
    }
    // handle the history command to mange command history
    else if (strcmp(argv[0], "history") == 0)
    {
        //adjust history capacity if set and a number provided 
        if (argv[1] != NULL && strcmp(argv[1], "set") == 0 && argv[2] != NULL)
        {
            adjust_history_capacity(atoi(argv[2]));
        }
         // Execute a specific command from history if a number is provided
        else if (argv[1] != NULL)
        {
            execute_history_command(atoi(argv[1]));
        }
          // Print the history if no specific instruction is provided
        else
        {
            print_history();
        }
    }
     // Handle external commands and commands with pipes
    else
    {
        int pipes = count_pipes(argv); // Determine if the command involves piping
        if (pipes == 0)
        {
            pid_t pid = fork(); // create new process 
            if (pid == 0)
            {
                // Child process
                // Replace the process with the new program
                if (execvp(argv[0], argv) == -1)
                {
                    if (errno == ENOENT)
                    {
                        fprintf(stderr, "execvp: No such file or directory\n");
                    }
                    else
                    {
                        perror("execvp");
                    }
                    exit(EXIT_FAILURE);
                }
            }
            else if (pid < 0)
            {
                perror("fork");
                exit(EXIT_FAILURE);
            }
            else
            {
                wait(NULL);
            }
        }
        else// If there are pipes involved
        {
            // Execute the commands with pipes
            execute_commands_with_pipes(argv);
        }
    }
}

int main(int argc, char *argv[])
{
    char *line = NULL; 
    size_t bufsize = 0;
    ssize_t nread;
    FILE *input_stream = stdin;
    // if there are two argumnets then we have to consider batch mode 
    if (argc == 2)
    {
        input_stream = fopen(argv[1], "r");
        if (!input_stream)
        {
            perror("Error opening script file");
            exit(EXIT_FAILURE);
        }
    }
    // to run shell we can have a max arguments of 2
    else if (argc > 2)
    {
        fprintf(stderr, "Usage: %s [script file]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    // infinte loop to start up the shell
    while (1)
    {
        // if it is interactive mode 
        if (input_stream == stdin)
        {
            printf("wsh> ");
            fflush(stdout);
        }

        // read each line entered or in batch file
        nread = getline(&line, &bufsize, input_stream);
        if (nread == -1)
        {
            // if end of file then exit the infinte loop
            if (feof(input_stream))
            {
                break;
            }
            else
            {
                perror("getline");
                continue;
            }
        }

        //replacing the new line with the null character to end the string
        if (line[nread - 1] == '\n')
        {
            line[nread - 1] = '\0';
        }

        //skip processing if the line is empty 
        if (line[0] == '\0')
        {
            continue;
        }
        
        // all the builtInCommands so we do not add the commands into history
        const char *builtInCommands[] = {"history", "cd", "exit", "export", "local", "vars"};
        int numBuiltIns = sizeof(builtInCommands) / sizeof(char *);

        int isBuiltIn = 0; // flag to incidate if the commans is built- in
        for (int i = 0; i < numBuiltIns; i++)
        {
            // compare the command with each builit in command
            if (strncmp(line, builtInCommands[i], strlen(builtInCommands[i])) == 0)
            {
                isBuiltIn = 1;
                break;
            }
        }
        // if the command is not built in, add it the history
        if (!isBuiltIn && line[0] != '\0')
        {
            add_history(line);
        }

        //parse the command line into arguments
        char *argv[MAX_ARGS];
        int argc = 0;
        char *token = strtok(line, DELIM);
        while (token != NULL && argc < MAX_ARGS - 1)
        {
            argv[argc++] = token;
            token = strtok(NULL, DELIM);
        }
        argv[argc] = NULL; 
        
         // Execute the command if it's not empty
        if (argv[0] != NULL)
        {

            compact_argv(argv); // Function to compact arguments if necessary
            substitute_variables(argv, envVars, shellVars); // Substitute variables in arguments
            execute_command(argv); // Execute the parsed command
        }
    }

    // Cleanup before exiting 
    if (input_stream != stdin)
    {
        fclose(input_stream); //close the file if it was opened 
    }

    //free 
    free(line);
    free_history();
    free_variables(&envVars);
    free_variables(&shellVars);

    return 0;
}