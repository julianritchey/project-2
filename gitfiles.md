Learn how to use Linux commands, because if you are running a server at one point or another, you will be using Linux

In Git Bash you can use up and down arrows to check your history

Commands:
pwd                                         To check which folder you are in (Print Working Directory)
cd                                          Goes to a folder (change directory)
mkdir                                       Make Directory
touch                                       (Creates a file inside a folder)
mv (1) (2)                                  1 - file to bew moved 2 - which folder to move the file (Move command)
Ctrl+C                                      Cancels the command being executed
clear                                       Clears the Console
ls                                          Shows what files you have in this directory (folder) - files in white and directories in blue
ls -la                                      Shows more information about the files
cd ..                                       Goes back to previous directory
cd .. && cd ..                              Goes back 2 levels of folders
ls *name of the file*                       Checks whether the file exists in that directory
start *name of directory*                   Opens the directory
start .                                     Opens the current directory
rmdir                                       Remove Directory (Can only be executed when the directory is empty)
rm -r *name of directory*                   Removes the directory with files inside
**note -r                                   Stands for recursive, so it applies the command to all the files/directories
> *file name*                               Creates a file, same as touch
ls --help                                   Gives you instructions on how to use this command
rm *name of the file*                       Removes the file
**note you can use rm and li                st files in order to delete multiple files
rm *                                        Deletes all the files in the directory
echo "Hello" > text.txt                     Creates file named Text.txt and writes Hello in it
cat *name of .txt file*                     Reads the content of the file
cp *name of the file* *name of directory*   Copy file to a directory
vim *name of the file*                      You can edit the contents of the file
***note once done editing in vim, press ESC, then :x (saves the file cahnges) or :q (exits without saving)
:q!                                         forces exit without saving
cp newdir/* difdir                          Copies files from newdir to difdir
Ctrl+Can                                    Stops executing a long command
exit                                        Closes the Bash
git init1                                   Initialize an empty repository
git status                                  Tells you the status of this git repository (braches, commits, what to commit)
git add *name of the file*                  Adds file to repository
git commit -m "message"                     Commits the changes with a comment
git remote set-url origin *Github URL*      Sets the local repository to be connected to the remote depository on Github
git remote -v                               Shows the repositories associated with github on the local computer
git push origin main                        Pushes the committed changes to github


