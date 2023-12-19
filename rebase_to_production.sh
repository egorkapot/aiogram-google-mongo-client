#Script to add changes from main branch to production
git checkout production
git rebase main
git push origin production --force
