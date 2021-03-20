#!/usr/bin/env bash
# The concept for our semantic versioning is based on the format of the branch names:
# - main: the head of the code with the latest, next-gen development
# - develop/major.minor: the branch that targets the specified major-minor pair (no patches)
# - develop/major.minor.patch: the branch that targets the specified major-minor pair with patches
# Therefore, if you want a new version, just create a new develop branch.
DEVELOP_BRANCH_REGEX="^develop\/([0-9]*)\.([0-9]*)(\.([0-9]*))?$"
ACTIVE_BRANCH_NAME=`git branch --show-current`
REMOTE_NAME=`git remote`
REMOTE_BRANCH_NAMES=`git branch -r`
VERSION_MAJOR=0
VERSION_MINOR=0
VERSION_PATCH=0
VERSION_BUILD=`git rev-list --count $ACTIVE_BRANCH_NAME`

echo "Active branch: ${ACTIVE_BRANCH_NAME}"

get_actual_branch_version() {
    local __resultvar=$2
    local myresult=""
    [[ $1 =~ $DEVELOP_BRANCH_REGEX ]]
    if [[ ${BASH_REMATCH[0]} = "" ]]; then
        return 1
    fi

    # This implosion is required as arrays of arrays don't exist in shell scripts.
    # major;minor;patch
    myresult="${BASH_REMATCH[1]};${BASH_REMATCH[2]};"
    if [[ ${BASH_REMATCH[4]} != "" ]]; then
        myresult+="${BASH_REMATCH[4]}"
    else
        myresult+="0"
    fi
    #echo "Version for branch '$1': ${versions}"
    eval $__resultvar="'${myresult}'"
    return 0
}

should_swap() {
    IFS=";" read -r -a arr1 <<< "$1"
    IFS=";" read -r -a arr2 <<< "$2"
    #echo "test ${arr1[@]}, ${arr2[@]}"
    if [[ ${arr1[0]} -gt ${arr2[0]} ]]; then
        return 1
    fi
    if [[ ${arr2[0]} -gt ${arr1[0]} ]]; then
        return 0
    fi
    if [[ ${arr1[1]} -gt ${arr2[1]} ]]; then
        return 1
    fi
    if [[ ${arr2[1]} -gt ${arr1[1]} ]]; then
        return 0
    fi
    if [[ ${arr1[2]} -gt ${arr2[2]} ]]; then
        return 1
    fi
    return 0
}

sort_by_version() {
    for ((i=0; i < $((${#version_tuples[@]} - 1)); ++i))
    do
        for ((j=0; j < ((${#version_tuples[@]} - $i - 1)); ++j))
        do
            should_swap ${version_tuples[j]} ${version_tuples[j+1]}
            swap=$?
            if [[ $swap -eq 1 ]]; then
                tmp=${version_tuples[j]}
                version_tuples[j]=${version_tuples[j+1]}
                version_tuples[j+1]=$tmp
            fi
        done
    done
}

get_actual_branch_version $ACTIVE_BRANCH_NAME active_branch_version
has_version=$?
if [[ $has_version -eq 0  ]]; then # develop branch
    echo "Determining version for develop branch..."
    IFS=";" read -r -a arr <<< "$active_branch_version"
    VERSION_MAJOR=${arr[0]}
    VERSION_MINOR=${arr[1]}
    VERSION_PATCH=${arr[2]}
else # main branch
    echo "Determining version for main branch..."
    version_tuples=()
    for branch_name in "${REMOTE_BRANCH_NAMES[@]}"
    do
        branch_name=${branch_name/${REMOTE_NAME}\//}
        get_actual_branch_version $branch_name versions
        success=$?
        if [[ $success -ne 0 ]]; then
            continue
        fi
        version_tuples+=($versions)
    done
    sort_by_version "${version_tuples[@]}"
    if [[ ${#version_tuples[@]} -eq 0 ]]; then
        VERSION_MAJOR=1
        echo "No develop branches yet, assuming major 1."
    else
        current_highest_version=${version_tuples[-1]}
        IFS=";" read -r -a arr <<< "$current_highest_version"
        VERSION_MAJOR=$((${arr[0]}+1))
    fi
fi

echo "New version: ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}.${VERSION_BUILD}"
sed -i "s/self.version = Version\(.*\)/self.version = Version\(${VERSION_MAJOR}, ${VERSION_MINOR}, ${VERSION_PATCH}, ${VERSION_BUILD}\)/" ./holobot/env/environment.py