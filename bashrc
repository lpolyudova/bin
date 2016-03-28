#!/bin/bash

#
# For Julia <3
#
#

git_prompt ()
{
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
      return 0
        fi

  git_branch=$(git branch 2>/dev/null| sed -n '/^\*/s/^\* //p')

  if git diff --quiet 2>/dev/null >&2; then
      git_color="${c_git_clean}"
        else
	    git_color=${c_git_cleanit_dirty}
	      fi

  echo " [$git_color$git_branch${c_reset}]"
  }

GREEN="\[$(tput setaf 2)\]"
RESET="\[$(tput sgr0)\]"

PS1="${c_path}\w${c_reset} ${GREEN} $(git_prompt) ${RESET}\n > "

# Hehe, I'm a fish ~____~
#         ,-.-,-,
#       _/ / / /       /)
#     ,'        `.   ,'')
#   _/(@) `.      `./ ,')
#  (____,`  \:`-.   \ ,')
#   (_      /::::}  / `.)
#    \    ,' :,-' ,)\ `.)
#     `.        ,')  `..)
#       \-....-'\      \)  hjw
#        `-`-`-`-`
