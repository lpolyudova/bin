#!/bin/zsh


# Load custom aliases
if [[ -f ~/.public_alias ]]
then
   . ~/.public_alias
fi

if [[ -f ~/.private_alias ]]
then
   . ~/.private_alias
fi

#
## Load PATH
if [[ -f ~/.path ]]
then
    . ~/.path
fi
#   




# library-cli-sdk
# The next line updates PATH for the Google Cloud SDK.
#source '/Users/lpolyudova/Downloads/Documents/google-cloud-sdk/path.zsh.inc'
# The next line enables shell command completion for gcloud.
# source '/Users/lpolyudova/Downloads/Documents/google-cloud-sdk/completion.zsh.inc'

# Enable git autocomplete
autoload -Uz compinit && compinit

# Add branch name to promp
autoload -Uz vcs_info

setopt prompt_subst
autoload -Uz vcs_info
zstyle ':vcs_info:*' actionformats \
       '%F{5}(%f%s%F{5})%F{3}-%F{5}[%F{2}%b%F{3}|%F{1}%a%F{5}]%f '
zstyle ':vcs_info:*' formats       \
       '%F{5}%F{3} %F{5}[%F{2}%b%F{5}]%f '
zstyle ':vcs_info:(sv[nk]|bzr):*' branchformat '%b%F{1}:%F{3}%r'
precmd () { vcs_info }

PS1=' %F{12}%3~ ${vcs_info_msg_0_}%f 
 > '

# Set history file variable
export HISTFILE=~/.zsh_history

# Set history search
bindkey "^[[A" history-beginning-search-backward
bindkey "^[[B" history-beginning-search-forward


extract ()
{
    if test -f "$1" && test -n "$1"  ; then
	case $1 in
	    *.tar.bz2)   tar xvjf $1    ;;
	    *.tar.gz)    tar xvzf $1    ;;
	    *.bz2)       bunzip2 $1     ;;
	    *.rar)       unrar x $1       ;;
	    *.gz)        gunzip $1      ;;
	    *.tar)       tar xvf $1     ;;
	    *.tbz2)      tar xvjf $1    ;;
	    *.tgz)       tar xvzf $1    ;;
	    *.zip)       unzip $1       ;;
	    *.Z)         uncompress $1  ;;
	    *.7z)        7z x $1        ;;
	    *)           echo "don't know how to extract '$1'..." ;;
	esac
    elif test -n "$1"; then
	 echo "'$1' is not a valid file!"
    else
	echo "no file to extract"
    fi
}
print_ascii()
{
    # Get random id f the picture 
    idx=$(( RANDOM % $(ls $BIN/ascii_art | wc -l ) +1 ))
    echo $idx
    list=($(ls))
    echo $list[idx]
    cat $BIN/ascii_art/$(echo $list[idx])
}
