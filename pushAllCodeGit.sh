# Call this using comamnd:
#./pushCodeGit.sh, then enter commit message
# From http://stackoverflow.com/questions/8482843/git-commit-bash-script

#!/bin/bash
read -p "Commit description: " desc  
echo $desc

git add *
git add .
git commit -m "$desc"
git push -u upstream shafaafCVST
