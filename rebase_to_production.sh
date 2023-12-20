#Script to add changes from main branch to production
git checkout main
git add .
git commit -m "another fix"
git checkout production
git rebase main
git push origin production --force
